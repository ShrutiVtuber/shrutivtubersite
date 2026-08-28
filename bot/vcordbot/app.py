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

import logging
from datetime import datetime, timezone

import asyncio
from contextlib import asynccontextmanager

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, Header, HTTPException, Request

from vcordbot import announce, commands, config, discord_api, render, storage
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


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    The watcher runs beside the web service rather than as a second container.

    It needs no connection to Discord — it polls the platforms and posts over
    REST — so it is a task, not a process. Cancelled cleanly on shutdown so a
    redeploy does not leave a sweep half-finished.
    """
    global _watcher
    storage.setup()
    if CFG.token:
        _watcher = asyncio.create_task(
            announce.loop(CFG.token, CFG.bot_url, CFG.site_url))
        log.info("watching for streams every %ss", announce.INTERVAL)
    else:
        log.warning("no token — the watcher is NOT running")
    try:
        yield
    finally:
        if _watcher:
            _watcher.cancel()
            try:
                await _watcher
            except asyncio.CancelledError:
                pass
            _watcher = None


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
