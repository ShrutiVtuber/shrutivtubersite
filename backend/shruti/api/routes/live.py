"""Live status endpoint. Cached, and always fails closed to offline."""

from __future__ import annotations

from fastapi import APIRouter, Response

from shruti.core.live import twitch

router = APIRouter(prefix="/api", tags=["live"])


@router.get("/live")
async def get_live(response: Response) -> dict:
    status = await twitch.status()
    # Let the edge hold it briefly too — the backend cache is the real defence,
    # this just stops a burst of tab-focus refetches reaching us at all.
    response.headers["Cache-Control"] = "public, max-age=30, s-maxage=30"
    return {
        "isLive": status.is_live,
        "title": status.title,
        "game": status.game,
        "viewers": status.viewers,
        "startedAt": status.started_at,
        "url": status.url,
        "checkedAt": status.checked_at.isoformat(),
    }
