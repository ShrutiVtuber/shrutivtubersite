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

from vcordbot.discord_api import add_reaction, post_and_tell_id

log = logging.getLogger("vcordbot.bridge")

# How much of a reading goes into the channel. Enough to decide whether to open
# it; not so much that a week of readings fills the scrollback.
OPENING = 400

# ⚠ The one reaction that counts as a vote, and the bot puts it there itself.
# A vote that only works if you guess the right emoji is a vote nobody casts.
VOTE = "\u2b50"          # ⭐


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
        "footer": {"text": f"{author} · {what} · reply here and it reaches them"},
    }
    return "", embed


async def announce_submission(
    work: dict, *, channel_id: str, token: str, site_url: str,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    """
    Put a submission in the channel, and say which message it became.

    ⚠ Returns None rather than raising. A Discord outage must not fail
    somebody's submission — they wrote it, it is saved, and the channel can
    catch up. Losing the announcement is a small thing; losing the work is not.

    ⚠ The MESSAGE ID is the return value, not a bool. Every vote and every
    reply that comes back names a message, and with nothing to match it against
    it is a number on nothing.
    """
    if not (channel_id and token):
        return None
    content, embed = submission_message(work, site_url)
    message_id = await post_and_tell_id(
        channel_id, token, content=content, embed=embed, client=client)
    if message_id:
        # The bot votes first so the channel has something to tap.
        await add_reaction(channel_id, message_id, token, VOTE, client=client)
    return message_id


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
