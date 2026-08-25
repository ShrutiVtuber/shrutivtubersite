# SPDX-License-Identifier: AGPL-3.0-only
"""
Recent uploads and VODs, for /videos.

**Thumbnails are proxied, not hotlinked.** A YouTube thumbnail served from
i.ytimg.com tells Google the IP of everyone who opens this page, and a Twitch
one tells Amazon. This site puts no tracking pixel in its email, runs no
cookies beyond the strictly necessary, and says so out loud on the privacy
page; hotlinking a third party's image on a listing page quietly undoes a
piece of that. Proxying costs a little bandwidth and keeps the promise.
"""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException, Response

from shruti.core.videos import recent

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["videos"])

# Only these hosts, and only image paths. A proxy that fetches whatever it is
# handed is an open relay for probing the inside of the network.
THUMB_HOSTS = {
    "youtube": "https://i.ytimg.com/vi/{id}/hqdefault.jpg",
    "twitch": "https://static-cdn.jtvnw.net/cf_vods/{id}",
}


@router.api_route("/videos/thumb/{platform}/{video_id}", methods=["GET", "HEAD"])
async def thumbnail(platform: str, video_id: str) -> Response:
    """
    One thumbnail, fetched by this server rather than by the visitor.

    The id is checked against the shape the platforms actually use before it
    is put in a URL; anything else is refused rather than fetched.
    """
    if platform != "youtube" or not video_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(404, "no such thumbnail")
    if not 5 <= len(video_id) <= 24:
        raise HTTPException(404, "no such thumbnail")

    url = THUMB_HOSTS["youtube"].format(id=video_id)
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=False) as client:
            r = await client.get(url)
    except Exception as exc:                       # noqa: BLE001
        log.info("thumbnail fetch failed: %s", type(exc).__name__)
        raise HTTPException(404, "no such thumbnail")
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(404, "no such thumbnail")

    return Response(
        content=r.content,
        media_type=r.headers.get("content-type", "image/jpeg"),
        # A day: a channel can replace a thumbnail, so not immutable, but long
        # enough that Cloudflare answers almost all of these.
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/videos")
async def list_videos(limit: int = 24) -> dict:
    videos = await recent()
    return {
        "videos": videos[: max(1, min(limit, 60))],
        "counts": {
            "youtube": sum(1 for v in videos if v["platform"] == "youtube"),
            "twitch": sum(1 for v in videos if v["platform"] == "twitch"),
        },
    }
