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


async def tell_the_site(kind: str, *, title: str, body: str, url: str,
                        client: httpx.AsyncClient | None = None) -> bool:
    """
    Ask the site to wake the phones that asked about this.

    ⚠ The bot is the only thing that knows a stream STARTED. The site polls a
    status and can say whether she is live now; deciding the transition twice
    would mean two things with two opinions about it, and one of them
    announcing at the wrong moment.

    Never raises, and never blocks the Discord announcement — the channel post
    is the thing that must happen.
    """
    import os

    site = os.environ.get("SHRUTI_API_INTERNAL", "").strip()
    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    if not (site and secret):
        return False
    try:
        owned = client is None
        client = client or httpx.AsyncClient(timeout=8)
        try:
            r = await client.post(
                f"{site}/api/devices/notify",
                json={"kind": kind, "title": title, "body": body, "url": url},
                headers={"X-Shruti-Internal": secret},
            )
            return r.status_code == 200
        finally:
            if owned:
                await client.aclose()
    except Exception as exc:                       # noqa: BLE001
        log.warning("the site was not told about %s: %s", kind, type(exc).__name__)
        return False


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
    # ⚠ Once per sweep, not once per watch. She is announced in however many
    # servers have a watch on her; the phones are ONE audience. Told per watch,
    # this looks perfect with one server and becomes five notifications the day
    # a second one adds the bot.
    told_the_site = False
    watches = await storage.to_thread(storage.watches)
    if not watches:
        return 0

    async def sweep(c: httpx.AsyncClient) -> int:
        # ⚠ nonlocal for BOTH. Assigning told_the_site inside this closure
        # without it makes the name local, and the read two lines above becomes
        # an UnboundLocalError the first time a stream starts — which is the one
        # moment this function exists for.
        nonlocal said, told_the_site
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
                # ⚠ The phones are told HERE, at the transition, and once —
                # `should_announce` is the thing that knows a stream started
                # rather than merely being on. Told per WATCH would notify the
                # same audience once per Discord server she is announced in.
                if not told_the_site:
                    told_the_site = True
                    # ⚠ Guarded at the CALL SITE as well as inside. The channel
                    # post below is the thing that must happen; a notification
                    # is strictly secondary, and it must not be able to take the
                    # announcement down with it however it fails.
                    try:
                        await tell_the_site(
                            "live",
                            title=f"{w.handle} is live",
                            body=status.title or "She has started streaming.",
                            url=status.url or "/videos",
                            client=c,
                        )
                    except Exception as exc:       # noqa: BLE001
                        log.warning("the site was not told she is live: %s",
                                    type(exc).__name__)
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
