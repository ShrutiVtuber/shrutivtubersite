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

from vcordbot.discord_api import post_message

log = logging.getLogger("vcordbot.bridge")

# How much of a reading goes into the channel. Enough to decide whether to open
# it; not so much that a week of readings fills the scrollback.
OPENING = 400


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
) -> bool:
    """
    Put a submission in the channel.

    ⚠ Returns False rather than raising. A Discord outage must not fail
    somebody's submission — they wrote it, it is saved, and the channel can
    catch up. Losing the announcement is a small thing; losing the work is not.
    """
    if not (channel_id and token):
        return False
    content, embed = submission_message(work, site_url)
    try:
        await post_message(channel_id, token, content=content, embed=embed,
                           client=client)
        return True
    except Exception as exc:                       # noqa: BLE001
        log.warning("practice announcement not posted: %s", type(exc).__name__)
        return False
