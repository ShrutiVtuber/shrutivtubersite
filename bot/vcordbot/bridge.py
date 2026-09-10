# SPDX-License-Identifier: AGPL-3.0-only
"""
The practice bridge: the app's room and a Discord channel, one conversation.

Her decision, in the plan: "truly seamless — someone types normally in Discord
and it appears in the app; somebody posts in the app and it appears in Discord."

**Two halves, and they cost very different amounts.**

- **App → Discord** needs nothing special. When somebody submits a piece of
  work, the site tells this bot and the bot posts it. That half works today.
- **Discord → app** needs to READ the channel, which needs a gateway socket and
  the privileged MESSAGE_CONTENT intent. See `gateway.py`.

⚠ **A bridged message has no site account behind it.** Somebody in Discord has
not signed up, agreed to anything, or been bannable. So a comment arriving this
way is marked as coming from Discord and carries the name Discord gave it —
never a made-up account, and never silently attributed to somebody real.
"""
from __future__ import annotations

import logging

import httpx

from vcordbot.discord_api import add_reaction, post_and_tell_id, start_thread

log = logging.getLogger("vcordbot.bridge")

# How much of a reading goes into the channel. Enough to decide whether to open
# it; not so much that a week of readings fills the scrollback.
OPENING = 400

# ⚠ The one reaction that counts as a vote, and the bot puts it there itself.
# A vote that only works if you guess the right emoji is a vote nobody casts.
VOTE = "\u2b50"          # ⭐


#: The glyph for each sign, so a reading is recognisable before it is read.
#: Discord renders these from the reader's own fonts — nothing is shipped.
GLYPH = {
    "aries": "\u2648", "taurus": "\u2649", "gemini": "\u264a",
    "cancer": "\u264b", "leo": "\u264c", "virgo": "\u264d",
    "libra": "\u264e", "scorpio": "\u264f", "sagittarius": "\u2650",
    "capricorn": "\u2651", "aquarius": "\u2652", "pisces": "\u2653",
}

#: An embed description is hard-capped by Discord. A reading longer than this
#: is trimmed at a word and finished on the site.
BODY = 4000


def reading_message(work: dict, reading: dict, site_url: str) -> dict:
    """
    One sign's reading, as it appears inside the thread.

    ⚠ The FULL text, not an excerpt. Her reasoning, when she asked how anybody
    would read a whole reading otherwise: the practice room is a workshop for
    members, and making somebody click out to a website to critique a paragraph
    is friction in exactly the wrong place. The channel still stays readable
    because all of this is inside a thread, not in the channel itself.
    """
    sign = (reading.get("sign") or "").lower()
    body = (reading.get("bodyMd") or "").strip()
    if len(body) > BODY:
        body = body[:BODY].rsplit(" ", 1)[0] + f"…\n\n[Read the rest]({site_url}/practice/{work.get('id')})"

    return {
        "title": f"{GLYPH.get(sign, '')} {sign.title()}".strip(),
        "description": body or "_(nothing written)_",
        "url": f"{site_url}/practice/{work.get('id')}",
        "image": {"url": f"{site_url}/practice/{work.get('id')}/sky/{sign}.png"},
        "footer": {"text": "reply to THIS message and it lands on this reading"},
    }


def submission_message(work: dict, site_url: str) -> tuple[str, dict]:
    """What a new submission looks like in the channel."""
    author = work.get("author") or "somebody"
    signs = work.get("signs") or []
    where = f"{site_url}/practice/{work.get('id')}"

    if len(signs) > 1:
        what = f"{len(signs)} signs"
    elif signs:
        what = signs[0].title()
    else:
        what = "a reading"

    opening = (work.get("opening") or "").strip()
    if len(opening) > OPENING:
        opening = opening[:OPENING].rsplit(" ", 1)[0] + "…"

    embed = {
        "title": work.get("title") or what,
        "description": opening or "_(no opening)_",
        "url": where,
        # The sky the whole set was written from. One image for the submission,
        # because the sky does not change between signs — only the houses do,
        # and those belong on each reading.
        "image": {"url": f"{site_url}/practice/{work.get('id')}/sky.png"},
        "footer": {"text": f"{author} · {what} · \u2b50 to vote · replies here are about the whole set"},
    }
    return "", embed


def thread_name(work: dict) -> str:
    """What the post is called in a list of posts."""
    author = work.get("author") or "somebody"
    signs = work.get("signs") or []
    what = f"{len(signs)} signs" if len(signs) > 1 else (
        signs[0].title() if signs else "a reading")
    return (work.get("title") or f"{what} — {author}")[:100]


async def announce(
    work: dict, *, channel_id: str, token: str, site_url: str,
    client: httpx.AsyncClient | None = None,
) -> tuple[str, str] | None:
    """
    Put a submission in the channel and open its thread.

    Returns `(message_id, thread_id)` — the message a vote or a whole-set reply
    names, and the thread each reading goes into.

    ⚠ **A thread in a text channel hangs off a message.** There is no other
    kind here: the message stays in the channel and the thread opens beneath
    it, which is how a text channel full of threads is built. The message is
    posted first because a thread needs something to hang from, so the two
    calls cannot be collapsed into one.

    ⚠ Fails soft, and returns None rather than raising. A Discord outage must
    not fail somebody's submission — they wrote it, it is saved, and the
    channel can catch up. A thread that could not be opened leaves the
    announcement standing and votable. Losing the announcement is a small
    thing; losing the work is not.
    """
    if not (channel_id and token):
        return None                 # no bridge configured; a working state

    content, embed = submission_message(work, site_url)
    message_id = await post_and_tell_id(
        channel_id, token, content=content, embed=embed, client=client)
    if not message_id:
        return None
    # The bot votes first so the channel has something to tap.
    await add_reaction(channel_id, message_id, token, VOTE, client=client)
    thread_id = await start_thread(
        channel_id, message_id, token, thread_name(work), client=client) or ""
    return message_id, thread_id


async def announce_the_readings(
    work: dict, *, thread_id: str, token: str, site_url: str,
    client: httpx.AsyncClient | None = None,
) -> tuple[str, list[tuple[str, str]]]:
    """
    Put each reading into the thread the announcement opened.

    Returns the thread id and a list of `(sign, message_id)` — everything the
    site needs to route a reply to the reading it answers.

    ⚠ **The organisation is made of REPLIES, not of nested threads.** Discord
    has no thread inside a thread: one hangs off a message in a channel, and a
    message already inside a thread cannot have one. So each reading is its own
    message in the thread, and answering a reading means replying to its
    message — which Discord shows with a "replying to →" reference. `sign` on
    the bridge row is what makes that mean something on this side.

    ⚠ Fails soft, one reading at a time. A single reading that did not post is
    one reading missing from a thread rather than a submission that errored.
    The work is saved either way; this is presentation.
    """
    # ⚠ model_dump() gives dicts here, but a caller with pydantic objects is
    # easy to write by accident; both are read the same way.
    readings = [
        r if isinstance(r, dict) else r.model_dump()
        for r in (work.get("readings") or [])
    ]
    if not (readings and thread_id):
        return "", []

    posted: list[tuple[str, str]] = []
    for reading in readings:
        sign = (reading.get("sign") or "").lower()
        if not sign:
            continue
        # ⚠ Posting to the THREAD id. A thread is a channel; the message the
        # thread hangs from is not one, and posting there would put every
        # reading back in the channel the thread exists to keep clear.
        said = await post_and_tell_id(
            thread_id, token, embed=reading_message(work, reading, site_url),
            client=client)
        if said:
            posted.append((sign, said))

    return thread_id, posted


async def tell_the_site(
    path: str, payload: dict, *, site_url: str, secret: str,
    client: httpx.AsyncClient | None = None,
) -> dict | None:
    """
    Hand something from the channel back to the room.

    ⚠ Fails soft and says so in the log. A reply that does not make it across
    is a comment nobody sees; a raised exception here is the gateway socket
    dying and the whole bridge going quiet, which is far worse.
    """
    if not (site_url and secret):
        return None

    async def _send(c: httpx.AsyncClient) -> dict | None:
        r = await c.post(
            f"{site_url}/api/practice/bridge/{path}",
            json=payload,
            headers={"X-Shruti-Internal": secret},
            timeout=10.0)
        if r.status_code >= 400:
            log.warning("the room refused %s: %s", path, r.status_code)
            return None
        return r.json()

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not reach the room: %s", type(exc).__name__)
        return None
