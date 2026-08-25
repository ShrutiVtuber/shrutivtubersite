# SPDX-License-Identifier: AGPL-3.0-only
"""
Recent videos from both platforms.

**YouTube uploads come from the RSS feed, not the API.** The feed is free,
needs no key and carries everything a card needs — id, title, published date,
thumbnail. The Data API would cost quota for the same information, and quota
is what makes the live badge possible at a useful frequency. The key stays for
the one thing RSS cannot answer, which is whether a video is live *now*.

**Twitch VODs need two Helix calls**, because Helix speaks user ids and the
site is configured with a login name. Both are cheap and the app token is
already cached by the live check.

Failure is per-platform and never fatal. One platform being unreachable must
leave the other's videos on the page rather than emptying it — an empty page
is indistinguishable from "she has never streamed", which is the wrong thing
to tell somebody.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from shruti.core.config import get_settings
from shruti.core.live import _twitch_app_token

log = logging.getLogger(__name__)

YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
YOUTUBE_PLAYLIST = "https://www.googleapis.com/youtube/v3/playlistItems"
TWITCH_USERS = "https://api.twitch.tv/helix/users"
TWITCH_VIDEOS = "https://api.twitch.tv/helix/videos"

# Videos change when she uploads, which is not often, and this is on a page
# anyone can load. Cached so a burst of visitors is one fetch.
_CACHE: dict[str, Any] = {"at": None, "videos": []}
CACHE_MINUTES = 15

_ENTRY = re.compile(r"<entry>(.*?)</entry>", re.S)
_FIELD = {
    "id": re.compile(r"<yt:videoId>([^<]+)</yt:videoId>"),
    "title": re.compile(r"<title>(.*?)</title>", re.S),
    "published": re.compile(r"<published>([^<]+)</published>"),
}


def _unescape(text: str) -> str:
    from html import unescape

    return unescape(text).strip()


async def _youtube(client: httpx.AsyncClient) -> list[dict]:
    """
    Recent uploads. RSS first, the Data API as a fallback.

    RSS is free and needs no key, which is why it is tried first. It is also
    not a supported product: it began returning 404 and 500 for a channel it
    had served minutes earlier, and the videos page emptied. The uploads
    playlist answers the same question for ONE quota unit — the uploads
    playlist id is the channel id with its `UC` prefix swapped for `UU` — so
    the fallback costs almost nothing and removes a dependency on an endpoint
    nobody promises.
    """
    s = get_settings()
    if not s.youtube_channel_id:
        return []
    try:
        return await _youtube_rss(client, s.youtube_channel_id)
    except Exception as exc:                       # noqa: BLE001
        log.info("youtube RSS unavailable (%s); using the Data API", type(exc).__name__)
    return await _youtube_api(client, s)


async def _youtube_api(client: httpx.AsyncClient, s) -> list[dict]:
    if not s.youtube_api_key:
        return []
    uploads = "UU" + s.youtube_channel_id[2:]
    r = await client.get(
        YOUTUBE_PLAYLIST,
        params={"part": "snippet,contentDetails", "playlistId": uploads,
                "maxResults": 12, "key": s.youtube_api_key},
        timeout=12.0,
    )
    r.raise_for_status()
    out = []
    for item in r.json().get("items", []):
        snippet = item.get("snippet") or {}
        vid = (item.get("contentDetails") or {}).get("videoId", "")
        if not vid:
            continue
        out.append({
            "platform": "youtube",
            "id": vid,
            "title": snippet.get("title", "") or "Untitled",
            "href": f"https://www.youtube.com/watch?v={vid}",
            "thumb": f"/api/videos/thumb/youtube/{vid}",
            "date": (snippet.get("publishedAt") or "")[:10],
            "duration": "",
        })
    return out


async def _youtube_rss(client: httpx.AsyncClient, channel_id: str) -> list[dict]:
    r = await client.get(YOUTUBE_RSS.format(channel_id=channel_id), timeout=10.0)
    r.raise_for_status()

    out = []
    for block in _ENTRY.findall(r.text):
        fields = {k: (p.search(block).group(1) if p.search(block) else "")
                  for k, p in _FIELD.items()}
        if not fields["id"]:
            continue
        out.append({
            "platform": "youtube",
            "id": fields["id"],
            "title": _unescape(fields["title"]),
            "href": f"https://www.youtube.com/watch?v={fields['id']}",
            # Through this site, not from i.ytimg.com — see the route's
            # docstring. Hotlinking would tell Google who reads this page.
            "thumb": f"/api/videos/thumb/youtube/{fields['id']}",
            "date": fields["published"][:10],
            "duration": "",
        })
    return out


async def _twitch(client: httpx.AsyncClient) -> list[dict]:
    s = get_settings()
    token = await _twitch_app_token(client)
    if not (token and s.twitch_login):
        return []
    headers = {"Client-ID": s.twitch_client_id, "Authorization": f"Bearer {token}"}

    r = await client.get(TWITCH_USERS, params={"login": s.twitch_login},
                         headers=headers, timeout=10.0)
    r.raise_for_status()
    users = r.json().get("data") or []
    if not users:
        return []

    r = await client.get(
        TWITCH_VIDEOS,
        params={"user_id": users[0]["id"], "type": "archive", "first": 12},
        headers=headers, timeout=10.0,
    )
    r.raise_for_status()

    out = []
    for v in r.json().get("data") or []:
        out.append({
            "platform": "twitch",
            "id": v.get("id", ""),
            "title": v.get("title", "") or "Untitled stream",
            "href": v.get("url", ""),
            # Twitch's are on a path this proxy does not accept, and a VOD
            # card without a still is a smaller loss than a third-party
            # request on every page load. Left absent; the card has a designed
            # state for it.
            "thumb": None,
            "date": (v.get("created_at") or "")[:10],
            "duration": v.get("duration", ""),
        })
    return out


async def recent(force: bool = False) -> list[dict]:
    """Both platforms, newest first. Cached, and never raises."""
    now = datetime.now(timezone.utc)
    if not force and _CACHE["at"] and now - _CACHE["at"] < timedelta(minutes=CACHE_MINUTES):
        return _CACHE["videos"]

    videos: list[dict] = []
    async with httpx.AsyncClient() as client:
        for name, job in (("youtube", _youtube), ("twitch", _twitch)):
            try:
                videos.extend(await job(client))
            except Exception as exc:               # noqa: BLE001
                # One platform down must not empty the page. An empty page
                # reads as "she has never streamed", which is worse than a
                # shorter list.
                log.warning("%s videos unavailable: %s", name, type(exc).__name__)

    videos.sort(key=lambda v: v.get("date") or "", reverse=True)

    # An empty result is NOT cached over a good one.
    #
    # Both platforms failing is far more likely to be an upstream hiccup than
    # a channel that suddenly has no videos, and caching the empty answer
    # turned a momentary 404 from YouTube's RSS into fifteen minutes of a
    # videos page saying she has never streamed. Keeping the last good list is
    # the honest failure: slightly stale beats confidently empty.
    if videos or not _CACHE["videos"]:
        _CACHE["at"] = now
        _CACHE["videos"] = videos
        return videos

    log.warning("no videos from any platform; keeping the previous list")
    return _CACHE["videos"]
