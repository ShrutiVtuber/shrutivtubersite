# SPDX-License-Identifier: AGPL-3.0-only
"""
The few REST calls the bot makes outward.

Posting a message is the only thing it does that Discord did not ask for
first, and it needs no gateway and no privileged intent — a bot with Send
Messages in a channel may post to it.
"""
from __future__ import annotations

import logging

import httpx

log = logging.getLogger("vcordbot.discord")

API = "https://discord.com/api/v10"


class DiscordError(RuntimeError):
    pass


async def post_message(channel_id: str, token: str, *, content: str = "",
                       embed: dict | None = None,
                       allowed_role: str = "",
                       client: httpx.AsyncClient | None = None) -> bool:
    """
    Send one message. True if it landed.

    **`allowed_mentions` is set explicitly and always.** Left to the default, a
    message containing @everyone in a stream title — or in a custom template
    somebody pasted — would ping the entire server. Naming exactly the one role
    that may be pinged makes that impossible rather than unlikely.
    """
    payload: dict = {
        "allowed_mentions": {"parse": [],
                             "roles": [allowed_role] if allowed_role else []},
    }
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    async def _send(c: httpx.AsyncClient) -> bool:
        r = await c.post(f"{API}/channels/{channel_id}/messages",
                         json=payload,
                         headers={"Authorization": f"Bot {token}",
                                  "User-Agent": "vcordbot/1.0"},
                         timeout=10.0)
        if r.status_code == 403:
            # The commonest failure by far, and not ours: the bot was invited
            # but cannot see or speak in that channel.
            log.warning("cannot post in channel %s — missing permission", channel_id)
            return False
        if r.status_code == 404:
            log.warning("channel %s no longer exists", channel_id)
            return False
        if r.status_code == 429:
            # Rate limited. Dropping one announcement is better than queuing
            # and posting it an hour late, when the stream may have ended.
            log.warning("rate limited posting to %s", channel_id)
            return False
        r.raise_for_status()
        return True

    try:
        if client is not None:
            return await _send(client)
        async with httpx.AsyncClient() as c:
            return await _send(c)
    except Exception as exc:                        # noqa: BLE001
        log.warning("posting to %s failed: %s", channel_id, type(exc).__name__)
        return False
