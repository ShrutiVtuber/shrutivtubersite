# SPDX-License-Identifier: AGPL-3.0-only
"""
Watching channels, and saying so once.

The poll loop is deliberately dull. Everything interesting was decided in
`platforms.should_announce`, and everything dangerous is in the two rules
below: a check that fails must not look like "offline", and a state must be
recorded whether or not anything was said.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from vcordbot import platforms, render, storage
from vcordbot.discord_api import post_message

log = logging.getLogger("vcordbot.announce")

# Twitch and YouTube both tolerate this comfortably, and it is the difference
# between "she is live" arriving usefully and arriving as history.
INTERVAL = 90


def message_for(watch: storage.Watch, status: platforms.Status,
                template: str, mention: str) -> tuple[str, dict]:
    """The line and the card. Her words if she gave any, ours if not."""
    handle = watch.handle
    title = status.title or "is live"
    body = (template or "{handle} is live — {title}") \
        .replace("{handle}", handle) \
        .replace("{title}", status.title or "") \
        .replace("{game}", status.game or "") \
        .replace("{url}", status.url)
    content = f"<@&{mention}> {body}".strip() if mention else body

    fields = []
    if status.game:
        fields.append({"name": "Playing", "value": status.game, "inline": True})
    embed = {
        "title": title[:250],
        "url": status.url,
        "description": f"**{handle}** is live on {watch.platform.title()}.",
        "color": 0x9146FF if watch.platform == "twitch" else 0xFF0000,
        "fields": fields,
    }
    return content, embed


async def check_all(token: str, bot_url: str, site_url: str,
                    client: httpx.AsyncClient | None = None) -> int:
    """One sweep. Returns how many announcements were made."""
    said = 0
    watches = await storage.to_thread(storage.watches)
    if not watches:
        return 0

    async def sweep(c: httpx.AsyncClient) -> int:
        nonlocal said
        for w in watches:
            if w.platform == "twitch":
                status = await platforms.twitch(w.handle, c)
            elif w.platform == "youtube":
                status = await platforms.youtube(w.handle, c)
            else:
                continue

            # An unknown state is recorded as unknown and NEVER collapsed to
            # offline — that collapse is what makes a blip look like a stream
            # ending and starting again.
            if platforms.should_announce(w.last_state, status.state):
                g = await storage.to_thread(storage.guild, w.guild_id)
                if g and g.channel_id:
                    content, embed = message_for(w, status, g.template, g.mention_role)
                    embed["description"] += "\n\n" + render.footer(bot_url, site_url)
                    ok = await post_message(g.channel_id, token, content=content,
                                            embed=embed, allowed_role=g.mention_role,
                                            client=c)
                    if ok:
                        said += 1
                    # The state is recorded either way. If a failed post left
                    # the state unchanged, the next sweep would try again — and
                    # keep trying, every ninety seconds, for the whole stream.
                    await storage.to_thread(storage.record_state, w.id, status.state, ok)
                    continue
            await storage.to_thread(storage.record_state, w.id, status.state)
        return said

    if client is not None:
        return await sweep(client)
    async with httpx.AsyncClient() as c:
        return await sweep(c)


async def loop(token: str, bot_url: str, site_url: str) -> None:
    """Forever, and never allowed to die."""
    while True:
        try:
            n = await check_all(token, bot_url, site_url)
            if n:
                log.info("announced %d stream(s)", n)
        except asyncio.CancelledError:
            raise
        except Exception as exc:                    # noqa: BLE001
            # One bad sweep must not stop the watcher. Silence would be
            # indistinguishable from nobody streaming.
            log.warning("sweep failed: %s", type(exc).__name__)
        await asyncio.sleep(INTERVAL)
