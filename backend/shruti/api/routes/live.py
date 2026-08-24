# SPDX-License-Identifier: AGPL-3.0-only
"""Live status across platforms. Cached, and always fails closed to offline."""

from __future__ import annotations

from fastapi import APIRouter, Response

from shruti.core.config import get_settings
from shruti.core.live import status

router = APIRouter(prefix="/api", tags=["live"])


@router.get("/live")
async def get_live(response: Response) -> dict:
    """
    Every platform, reported separately, plus one named primary.

    `anyLive` is what a badge should key off. `primary` is what the call to
    action should point at — during a simulcast both platforms are live and it
    is the same stream, so offering two "watch now" buttons is worse than one.

    A platform that could not be checked reports `isLive: false` with its
    `error` set. That is deliberate: a site that falsely claims a stream sends
    people to an empty channel, which is worse than saying nothing.
    """
    s = get_settings()
    live = await status()
    primary = live.primary(s.primary_platform)

    # Brief edge caching so a burst of tab-focus refetches never reaches us.
    response.headers["Cache-Control"] = "public, max-age=30, s-maxage=30"

    return {
        "anyLive": live.any_live,
        "checkedAt": live.checked_at.isoformat(),
        "primary": None if primary is None else {
            "platform": primary.platform,
            "title": primary.title,
            "game": primary.game,
            "viewers": primary.viewers,
            "startedAt": primary.started_at,
            "watchUrl": primary.watch_url,
        },
        "platforms": [
            {
                "platform": p.platform,
                "isLive": p.is_live,
                "title": p.title,
                "game": p.game,
                "viewers": p.viewers,
                "startedAt": p.started_at,
                "url": p.url,
                "watchUrl": p.watch_url,
                # Present so a degraded check is visible rather than
                # indistinguishable from a genuinely offline channel.
                "error": p.error or None,
            }
            for p in live.platforms
        ],
    }
