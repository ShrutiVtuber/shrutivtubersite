# SPDX-License-Identifier: AGPL-3.0-only
"""
Live status, across platforms.

Three rules, all deliberate:

1. **Fail closed, per platform.** Any error — network, auth, quota, malformed
   response — reports that platform offline. A site that falsely claims a stream
   sends people to an empty channel, which is worse than saying nothing. One
   platform failing must never take the other down with it.

2. **Secrets never reach the browser.** This module exists mainly to hold the
   Twitch client secret and the YouTube key server-side.

3. **Simulcasting is the normal case, not an edge case.** She streams on Twitch
   *and* YouTube, often at once, so the answer is not a boolean. The response
   reports every platform separately and names one as primary for the call to
   action — because two "WATCH NOW" buttons is a worse experience than one.

**On YouTube quota.** The obvious call, `search?eventType=live`, costs **100
units** against a 10,000/day default — about one check every fifteen minutes
before the quota is gone. Instead this reads the channel's RSS feed (free, no
key) to get recent video ids, then asks `videos?part=liveStreamingDetails`
(**1 unit**) whether any of them is live. Same answer, a hundredth of the cost.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import httpx

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"
YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
YOUTUBE_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

_VIDEO_ID = re.compile(r"<yt:videoId>([\w-]{11})</yt:videoId>")


@dataclass
class PlatformStatus:
    platform: str
    is_live: bool = False
    title: str = ""
    game: str = ""
    viewers: int | None = None
    started_at: str | None = None
    url: str = ""
    watch_url: str = ""
    error: str = ""


@dataclass
class LiveStatus:
    platforms: list[PlatformStatus] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def any_live(self) -> bool:
        return any(p.is_live for p in self.platforms)

    def primary(self, preferred: str) -> PlatformStatus | None:
        """
        The one platform the call to action should point at.

        Prefers the configured platform when it is live — during a simulcast both
        are live and the same stream, so this is a preference, not a judgement.
        Falls back to whichever is live.
        """
        live = [p for p in self.platforms if p.is_live]
        if not live:
            return None
        for p in live:
            if p.platform == preferred:
                return p
        return live[0]


class _Cache:
    """One cached answer, refreshed at most once per TTL."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._value: LiveStatus | None = None
        self._at = datetime.min.replace(tzinfo=timezone.utc)

    def fresh(self, ttl: int) -> LiveStatus | None:
        if self._value and (datetime.now(timezone.utc) - self._at).total_seconds() < ttl:
            return self._value
        return None

    def put(self, value: LiveStatus) -> LiveStatus:
        self._value, self._at = value, datetime.now(timezone.utc)
        return value


_cache = _Cache()
_twitch_token: dict = {"token": None, "expires": datetime.min.replace(tzinfo=timezone.utc)}


async def _twitch_app_token(client: httpx.AsyncClient) -> str | None:
    s = get_settings()
    if not (s.twitch_client_id and s.twitch_client_secret):
        return None
    now = datetime.now(timezone.utc)
    if _twitch_token["token"] and now < _twitch_token["expires"]:
        return _twitch_token["token"]

    r = await client.post(
        TWITCH_TOKEN_URL,
        data={"client_id": s.twitch_client_id,
              "client_secret": s.twitch_client_secret,
              "grant_type": "client_credentials"},
        timeout=8.0,
    )
    r.raise_for_status()
    payload = r.json()
    _twitch_token["token"] = payload["access_token"]
    # Refresh a minute early rather than racing the expiry.
    _twitch_token["expires"] = now + timedelta(seconds=int(payload.get("expires_in", 3600)) - 60)
    return _twitch_token["token"]


async def _check_twitch(client: httpx.AsyncClient) -> PlatformStatus:
    s = get_settings()
    out = PlatformStatus(platform="twitch", url=f"https://twitch.tv/{s.twitch_login}")
    out.watch_url = out.url
    try:
        token = await _twitch_app_token(client)
        if token is None:
            out.error = "not configured"
            return out
        r = await client.get(
            TWITCH_STREAMS_URL,
            params={"user_login": s.twitch_login},
            headers={"Client-ID": s.twitch_client_id, "Authorization": f"Bearer {token}"},
            timeout=8.0,
        )
        r.raise_for_status()
        data = r.json().get("data", [])
        if data:
            d = data[0]
            out.is_live = True
            out.title = d.get("title", "")
            out.game = d.get("game_name", "")
            out.viewers = int(d.get("viewer_count", 0))
            out.started_at = d.get("started_at")
    except Exception as exc:                       # noqa: BLE001 — fail closed
        log.warning("twitch check failed: %s", type(exc).__name__)
        out.error = type(exc).__name__
    return out


async def _check_youtube(client: httpx.AsyncClient) -> PlatformStatus:
    """
    Recent uploads from RSS (free), then one videos call (1 unit) to ask which,
    if any, is currently live.
    """
    s = get_settings()
    channel = s.youtube_channel_id
    out = PlatformStatus(
        platform="youtube",
        url=f"https://www.youtube.com/channel/{channel}" if channel else "",
    )
    out.watch_url = f"{out.url}/live" if out.url else ""

    if not channel:
        out.error = "not configured"
        return out

    try:
        feed = await client.get(YOUTUBE_RSS.format(channel_id=channel), timeout=8.0)
        feed.raise_for_status()
        ids = _VIDEO_ID.findall(feed.text)[:5]
        if not ids:
            return out

        if not s.youtube_api_key:
            # Without a key the live check is not possible. Reporting offline is
            # honest; guessing from the feed is not — an upload is not a stream.
            out.error = "no api key; cannot determine live state"
            return out

        r = await client.get(
            YOUTUBE_VIDEOS,
            params={"part": "snippet,liveStreamingDetails",
                    "id": ",".join(ids), "key": s.youtube_api_key},
            timeout=8.0,
        )
        r.raise_for_status()
        for item in r.json().get("items", []):
            snippet = item.get("snippet", {})
            if snippet.get("liveBroadcastContent") != "live":
                continue
            details = item.get("liveStreamingDetails", {})
            out.is_live = True
            out.title = snippet.get("title", "")
            out.started_at = details.get("actualStartTime")
            viewers = details.get("concurrentViewers")
            out.viewers = int(viewers) if viewers is not None else None
            out.watch_url = f"https://www.youtube.com/watch?v={item['id']}"
            break
    except Exception as exc:                       # noqa: BLE001 — fail closed
        log.warning("youtube check failed: %s", type(exc).__name__)
        out.error = type(exc).__name__
    return out


async def status() -> LiveStatus:
    s = get_settings()
    cached = _cache.fresh(s.live_cache_ttl)
    if cached:
        return cached

    async with _cache._lock:
        cached = _cache.fresh(s.live_cache_ttl)
        if cached:
            return cached

        async with httpx.AsyncClient() as client:
            # Concurrently, and independently: one platform failing must not
            # take the other with it.
            results = await asyncio.gather(
                _check_twitch(client), _check_youtube(client),
                return_exceptions=True,
            )

        platforms: list[PlatformStatus] = []
        for name, result in zip(("twitch", "youtube"), results):
            if isinstance(result, BaseException):
                log.warning("%s check raised: %s", name, type(result).__name__)
                platforms.append(PlatformStatus(platform=name, error=type(result).__name__))
            else:
                platforms.append(result)

        return _cache.put(LiveStatus(platforms=platforms))
