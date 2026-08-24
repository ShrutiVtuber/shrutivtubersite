"""
Live status.

Two rules, both deliberate:

1. The Twitch client secret never reaches the browser. This module is the only
   reason the backend exists on the critical path of the homepage.
2. It FAILS CLOSED. Any error — network, auth, rate limit, malformed response —
   reports offline. A site that falsely claims you are live sends people to an
   empty channel, which is worse than saying nothing.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import httpx

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
_STREAMS_URL = "https://api.twitch.tv/helix/streams"


@dataclass
class LiveStatus:
    is_live: bool = False
    title: str = ""
    game: str = ""
    viewers: int = 0
    started_at: str | None = None
    thumbnail_url: str = ""
    url: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class _TwitchClient:
    """Caches both the app token and the stream result. One request per TTL."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._token: str | None = None
        self._token_expires: datetime = datetime.now(timezone.utc)
        self._cached: LiveStatus | None = None
        self._cached_at: datetime = datetime.min.replace(tzinfo=timezone.utc)

    async def _app_token(self, client: httpx.AsyncClient) -> str | None:
        s = get_settings()
        if not (s.twitch_client_id and s.twitch_client_secret):
            return None
        now = datetime.now(timezone.utc)
        if self._token and now < self._token_expires:
            return self._token

        r = await client.post(
            _TOKEN_URL,
            data={
                "client_id": s.twitch_client_id,
                "client_secret": s.twitch_client_secret,
                "grant_type": "client_credentials",
            },
            timeout=8.0,
        )
        r.raise_for_status()
        payload = r.json()
        self._token = payload["access_token"]
        # Refresh a minute early rather than racing the expiry.
        self._token_expires = now + timedelta(seconds=int(payload.get("expires_in", 3600)) - 60)
        return self._token

    async def status(self) -> LiveStatus:
        s = get_settings()
        now = datetime.now(timezone.utc)

        if self._cached and (now - self._cached_at).total_seconds() < s.live_cache_ttl:
            return self._cached

        async with self._lock:
            # Another coroutine may have refreshed while we waited.
            now = datetime.now(timezone.utc)
            if self._cached and (now - self._cached_at).total_seconds() < s.live_cache_ttl:
                return self._cached

            result = LiveStatus(url=f"https://twitch.tv/{s.twitch_login}")
            try:
                async with httpx.AsyncClient() as client:
                    token = await self._app_token(client)
                    if token is None:
                        log.debug("twitch credentials not configured; reporting offline")
                        self._cached, self._cached_at = result, now
                        return result

                    r = await client.get(
                        _STREAMS_URL,
                        params={"user_login": s.twitch_login},
                        headers={
                            "Client-ID": s.twitch_client_id,
                            "Authorization": f"Bearer {token}",
                        },
                        timeout=8.0,
                    )
                    r.raise_for_status()
                    data = r.json().get("data", [])
                    if data:
                        d = data[0]
                        result = LiveStatus(
                            is_live=True,
                            title=d.get("title", ""),
                            game=d.get("game_name", ""),
                            viewers=int(d.get("viewer_count", 0)),
                            started_at=d.get("started_at"),
                            thumbnail_url=d.get("thumbnail_url", ""),
                            url=f"https://twitch.tv/{s.twitch_login}",
                        )
            except Exception:                      # noqa: BLE001 — fail closed, always
                log.warning("live status check failed; reporting offline", exc_info=True)
                result = LiveStatus(url=f"https://twitch.tv/{s.twitch_login}")

            self._cached, self._cached_at = result, datetime.now(timezone.utc)
            return result


twitch = _TwitchClient()
