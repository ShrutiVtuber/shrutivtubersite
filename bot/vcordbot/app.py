# SPDX-License-Identifier: AGPL-3.0-only
"""
The web service Discord talks to.

A thin adapter and nothing else: verify the signature, hand the payload to
`dispatch`, return what it gives back. Every decision worth testing lives in
`dispatch`, which knows nothing about HTTP.

**Signature verification is not optional and cannot be "improved" later.** The
endpoint is a public URL that anybody can POST to. Without the check, a
stranger can make this bot say anything, in any server it is in, by sending a
made-up interaction — and Discord will not be involved at all. Discord also
refuses to save an endpoint that does not answer its signed PING correctly, so
getting this wrong fails closed rather than silently.
"""
from __future__ import annotations

import hmac
import logging
import os
from datetime import datetime, timezone

import asyncio
from contextlib import asynccontextmanager

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from vcordbot import (announce, bridge, commands, config, discord_api, gateway,
                      render, storage)
from vcordbot.astro import Astro
from vcordbot.dispatch import dispatch

# uvicorn configures its own loggers and leaves everybody else at WARNING, so
# the watcher's own lines never appeared. Set it here rather than wondering
# later whether silence means "nothing happened" or "nothing is running".
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("vcordbot")

# Held so `/health` can say whether the sweep is actually running. "Silence"
# and "stopped" look identical from outside, and only one of them is fine.
_watcher: "asyncio.Task | None" = None

# Deferred answers in flight. Held in a set because asyncio keeps only a weak
# reference to a bare task, and a garbage-collected one is an interaction that
# is acknowledged and then never answered — which looks to the person asking
# like the bot simply stopped.
_pending: "set[asyncio.Task]" = set()

# Discord's "I heard you, the answer is coming". The message can be edited for
# fifteen minutes afterwards, which is far more room than anything here needs.
DEFERRED_CHANNEL_MESSAGE = 5

CFG = config.load()


_reader: "gateway.Reader | None" = None
_listening: "asyncio.Task | None" = None


def _internal_site() -> str:
    """
    Where the room is, from in here.

    ⚠ Not the public URL when there is an internal one: the bot and the site
    are in the same compose network, and going out to the internet and back to
    reach a container two hops away is a round trip that fails whenever DNS or
    the proxy has a bad moment.
    """
    return (os.environ.get("SHRUTI_INTERNAL_SITE", "").strip()
            or os.environ.get("SHRUTI_SITE_URL", "").strip()
            or CFG.site_url)


async def _channel_said(message: dict) -> None:
    """A reply in the channel becomes a comment on the work it answers."""
    reference = message.get("message_reference") or {}
    replying_to = str(reference.get("message_id") or "")
    if not replying_to:
        # ⚠ Only replies, never every message. The channel is a channel:
        # sweeping all of it into somebody's reading would fill the room with
        # conversation that was never about it.
        return

    author = message.get("author") or {}
    who = (author.get("global_name") or author.get("username") or "").strip()
    body = (message.get("content") or "").strip()
    if not (who and body):
        return

    await bridge.tell_the_site(
        "comment",
        {"message_id": replying_to, "who": who, "body_md": body},
        site_url=_internal_site(),
        secret=os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip(),
    )


async def _channel_voted(event: dict, on: bool) -> None:
    """The star reaction, counted as a vote."""
    emoji = (event.get("emoji") or {}).get("name") or ""
    if emoji != bridge.VOTE:
        return          # somebody reacting with something else is not a vote

    await bridge.tell_the_site(
        "vote",
        {
            "message_id": str(event.get("message_id") or ""),
            "who": str(event.get("user_id") or ""),
            "on": on,
        },
        site_url=_internal_site(),
        secret=os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip(),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    The watcher runs beside the web service rather than as a second container.

    It needs no connection to Discord — it polls the platforms and posts over
    REST — so it is a task, not a process. Cancelled cleanly on shutdown so a
    redeploy does not leave a sweep half-finished.
    """
    global _watcher, _reader, _listening
    storage.setup()
    if CFG.token:
        _watcher = asyncio.create_task(
            announce.loop(CFG.token, CFG.bot_url, CFG.site_url))
        log.info("watching for streams every %ss", announce.INTERVAL)
    else:
        log.warning("no token — the watcher is NOT running")

    # ⚠ The bridge's inbound half, which was written and never started.
    #
    # It needs a channel and a token and nothing else to READ reactions —
    # GUILD_MESSAGE_REACTIONS is not a privileged intent — so votes from the
    # channel work the day this deploys. Replies additionally need
    # MESSAGE_CONTENT switched on in the developer portal, and the reader says
    # so in the log rather than sitting quiet if it is off.
    if CFG.token and CFG.practice_channel_id:
        _reader = gateway.Reader(
            CFG.token,
            channel_id=CFG.practice_channel_id,
            on_message=_channel_said,
            on_reaction=_channel_voted,
        )
        _listening = asyncio.create_task(_reader.run())
        log.info("listening to the practice channel")
    else:
        log.info("no practice channel — the bridge only goes outward")

    try:
        yield
    finally:
        if _reader is not None:
            _reader.stop()
        for task in (_watcher, _listening):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        _watcher = None
        _listening = None
        _reader = None


app = FastAPI(title="vcordbot", docs_url=None, redoc_url=None, openapi_url=None,
              lifespan=lifespan)


def _verifier() -> Ed25519PublicKey | None:
    if not CFG.public_key:
        return None
    try:
        return Ed25519PublicKey.from_public_bytes(bytes.fromhex(CFG.public_key))
    except ValueError:
        log.error("the configured public key is not valid hex; refusing everything")
        return None


VERIFIER = _verifier()


@app.get("/health")
async def health() -> dict:
    """
    No secrets, no counts, nothing about who uses it.

    **A health check must not be able to fail.** This read the store directly
    and raised when the store was not there — so the one moment the endpoint
    exists for, a startup that did not finish, was the one moment it could not
    answer. An unreachable store is now something it REPORTS.
    """
    running = _watcher is not None and not _watcher.done()
    try:
        watching = len(storage.watches())
        store = "ready"
    except Exception:                               # noqa: BLE001
        # Deliberately broad: whatever went wrong with the store, saying so is
        # more useful than a 500 that says nothing at all.
        watching, store = None, "unavailable"
    return {"ok": True, "app": CFG.app_id or None,
            "verifying": VERIFIER is not None,
            "watcher": "running" if running else "stopped",
            "store": store,
            "watching": watching}


class PracticeIn(BaseModel):
    """A submission the site is telling us about."""

    id: int
    author: str = ""
    title: str = ""
    signs: list[str] = []
    opening: str = ""


@app.post("/internal/practice")
async def practice_submitted(
    body: PracticeIn,
    x_shruti_internal: str = Header(default="", alias="X-Shruti-Internal"),
) -> dict:
    """
    The site telling the channel that somebody submitted a reading.

    ⚠ **Not public.** It posts to a Discord channel under her bot's name, so an
    open endpoint here is an open endpoint for putting words in her server. The
    shared secret is checked in constant time, and a missing secret refuses
    everything rather than defaulting to open.

    ⚠ Answers ok either way. A Discord outage must not fail somebody's
    submission — they wrote it, it is saved, and the channel can catch up.
    """
    cfg = config.load()
    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    if not secret or not hmac.compare_digest(x_shruti_internal, secret):
        raise HTTPException(401, "no")

    site_url = os.environ.get("SHRUTI_SITE_URL", "https://shrutivtuber.com")
    message_id = await bridge.announce_submission(
        body.model_dump(),
        channel_id=cfg.practice_channel_id,
        token=cfg.token,
        site_url=site_url,
    )

    # ⚠ Tell the room which message it became, or the bridge only goes one
    # way: a reaction on this message would arrive naming an id the room has
    # never heard of, and be dropped as a reaction to nothing.
    internal = os.environ.get("SHRUTI_INTERNAL_SITE", site_url)
    readings_posted = 0
    if message_id:
        await bridge.tell_the_site(
            f"{body.id}/message",
            {"message_id": message_id, "channel_id": cfg.practice_channel_id},
            site_url=internal,
            secret=secret,
        )

        # The readings themselves, in a thread under the announcement, one
        # message each. Registered the same way and with their sign, so a reply
        # to one of them is a comment on THAT reading rather than on the week.
        thread_id, posted = await bridge.announce_the_readings(
            body.model_dump(),
            message_id=message_id,
            channel_id=cfg.practice_channel_id,
            token=cfg.token,
            site_url=site_url,
        )
        for sign, said in posted:
            await bridge.tell_the_site(
                f"{body.id}/message",
                {"message_id": said, "channel_id": thread_id,
                 "sign": sign, "thread_id": thread_id},
                site_url=internal,
                secret=secret,
            )
        readings_posted = len(posted)

    return {"ok": True, "posted": bool(message_id), "readings": readings_posted}


@app.post("/interactions")
async def interactions(
    request: Request,
    x_signature_ed25519: str = Header(default=""),
    x_signature_timestamp: str = Header(default=""),
) -> dict:
    body = await request.body()

    # Fail CLOSED. A missing key means we cannot tell Discord from anyone else,
    # and the safe reading of "cannot tell" is "do not answer".
    if VERIFIER is None:
        raise HTTPException(503, "not configured")
    if not x_signature_ed25519 or not x_signature_timestamp:
        raise HTTPException(401, "invalid request signature")

    try:
        VERIFIER.verify(bytes.fromhex(x_signature_ed25519),
                        x_signature_timestamp.encode() + body)
    except (InvalidSignature, ValueError):
        # 401 with exactly Discord's expected wording. Nothing about WHY —
        # a probe learns only that it failed.
        raise HTTPException(401, "invalid request signature")

    payload = await request.json()

    # Some commands cannot answer inside Discord's three seconds — `/chart`
    # asks a gazetteer and then an ephemeris. Acknowledge first and fill the
    # answer in, rather than racing a deadline and losing the birth data
    # somebody just typed to "the application did not respond".
    #
    # `dispatch` is untouched by this: it still takes a payload and returns a
    # response, and every test of it still runs with no HTTP anywhere. The
    # transport concern stays in the adapter, which is what the adapter is for.
    name = (payload.get("data") or {}).get("name")
    if payload.get("type") == 2 and name in commands.DEFERRED:
        task = asyncio.create_task(_answer_later(payload))
        _pending.add(task)
        task.add_done_callback(_pending.discard)
        return {"type": DEFERRED_CHANNEL_MESSAGE,
                # Decided HERE and never afterwards: the flag belongs to the
                # acknowledgement, so a chart cannot become public because
                # something failed halfway through producing it.
                "data": {"flags": 0 if _wants_sharing(payload) else 1 << 6}}

    return await _answer(payload)


def _wants_sharing(payload: dict) -> bool:
    """Whether the person asked for this to be posted in the channel."""
    for option in ((payload.get("data") or {}).get("options") or []):
        if option.get("name") == "share":
            return bool(option.get("value"))
    return False


async def _answer(payload: dict) -> dict:
    return await dispatch(
        payload,
        Astro(CFG.astro_url),
        bot_url=CFG.bot_url,
        site_url=CFG.site_url,
        now_iso=datetime.now(timezone.utc).isoformat(),
    )


async def _answer_later(payload: dict) -> None:
    """
    Do the slow work, then replace the acknowledgement with the answer.

    Nothing raised in here reaches the person as a stack trace or as silence.
    Silence is the worse of the two: an acknowledged interaction that is never
    edited sits there saying the bot is thinking, forever.
    """
    try:
        response = await _answer(payload)
        embeds = (response.get("data") or {}).get("embeds") or []
        answer = embeds[0] if embeds else render.failure(
            "I could not put that together.", CFG.bot_url, CFG.site_url)
    except Exception as exc:                        # noqa: BLE001
        # Deliberately says nothing about WHAT failed. The inputs to this
        # command are somebody's birth details and they must not end up in a
        # message or a log line.
        log.warning("deferred %s failed: %s",
                    (payload.get("data") or {}).get("name"), type(exc).__name__)
        answer = render.failure(
            "Something went wrong working that out. Try again in a moment.",
            CFG.bot_url, CFG.site_url)

    await discord_api.edit_original(CFG.app_id, payload.get("token", ""), answer)
