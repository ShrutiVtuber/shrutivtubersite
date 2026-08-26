# SPDX-License-Identifier: AGPL-3.0-only
"""
Is this channel live?

Multi-tenant, so every function takes the handle rather than reading one from
configuration — that is the whole difference between this and the website's own
watcher, which only ever asks about hers.

**YouTube is checked the cheap way**, the same technique the website settled
on: the channel's RSS feed is free and lists recent uploads, and one
`videos.list` call costs a single quota unit. The obvious approach —
`search.list` with `eventType=live` — costs **100 units a call**, which at a
default of 10,000 a day would allow about four channels checked every ten
minutes for the whole application. Polling that way does not scale past a
handful of servers, and it fails silently by exhausting quota rather than by
erroring.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

log = logging.getLogger("vcordbot.platforms")

TWITCH_TOKEN = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS = "https://api.twitch.tv/helix/streams"
YT_FEED = "https://www.youtube.com/feeds/videos.xml"
YT_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

LIVE, OFFLINE, UNKNOWN = "live", "offline", "unknown"


@dataclass
class Status:
    """
    What a check found.

    `state` is one of three, and the third is the important one. An API that
    errors means we do not KNOW — and treating not-knowing as offline is how a
    watcher announces a stream twice: once when it starts, and again after a
    blip makes it look as though it stopped and restarted.
    """
    state: str
    title: str = ""
    game: str = ""
    url: str = ""


_token: dict = {"value": None, "expires": datetime.min.replace(tzinfo=timezone.utc)}


async def _twitch_token(client: httpx.AsyncClient) -> str | None:
    cid = os.environ.get("SHRUTI_TWITCH_CLIENT_ID", "")
    secret = os.environ.get("SHRUTI_TWITCH_CLIENT_SECRET", "")
    if not (cid and secret):
        return None
    now = datetime.now(timezone.utc)
    if _token["value"] and now < _token["expires"]:
        return _token["value"]
    r = await client.post(TWITCH_TOKEN, data={
        "client_id": cid, "client_secret": secret,
        "grant_type": "client_credentials"}, timeout=8.0)
    r.raise_for_status()
    body = r.json()
    _token["value"] = body["access_token"]
    # A minute early, rather than racing the expiry and retrying on a 401.
    _token["expires"] = now + timedelta(seconds=int(body.get("expires_in", 3600)) - 60)
    return _token["value"]


async def twitch(login: str, client: httpx.AsyncClient) -> Status:
    """
    App token only — no broadcaster OAuth, so no token custody.

    Checking whether somebody is live is public information; it needs no
    permission from them and holds nothing on their behalf.
    """
    url = f"https://twitch.tv/{login}"
    cid = os.environ.get("SHRUTI_TWITCH_CLIENT_ID", "")
    try:
        token = await _twitch_token(client)
        if not token:
            return Status(UNKNOWN, url=url)
        r = await client.get(TWITCH_STREAMS, params={"user_login": login},
                             headers={"Client-ID": cid,
                                      "Authorization": f"Bearer {token}"}, timeout=8.0)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            return Status(OFFLINE, url=url)
        d = data[0]
        return Status(LIVE, title=d.get("title", ""), game=d.get("game_name", ""), url=url)
    except Exception as exc:                        # noqa: BLE001
        log.warning("twitch check for %s failed: %s", login, type(exc).__name__)
        return Status(UNKNOWN, url=url)


_ENTRY = re.compile(r"<yt:videoId>([\w-]{11})</yt:videoId>")


async def youtube(channel_id: str, client: httpx.AsyncClient) -> Status:
    """
    RSS to find the recent videos (free), one videos call to ask which is live.

    Costs one quota unit per check rather than a hundred.
    """
    url = f"https://www.youtube.com/channel/{channel_id}/live"
    key = os.environ.get("SHRUTI_YOUTUBE_API_KEY", "")
    try:
        feed = await client.get(YT_FEED, params={"channel_id": channel_id}, timeout=8.0)
        feed.raise_for_status()
        ids = _ENTRY.findall(feed.text)[:5]
        if not ids or not key:
            return Status(OFFLINE if ids else UNKNOWN, url=url)

        r = await client.get(YT_VIDEOS, params={
            "part": "snippet,liveStreamingDetails", "id": ",".join(ids), "key": key},
            timeout=8.0)
        r.raise_for_status()
        for item in r.json().get("items", []):
            snippet = item.get("snippet", {})
            details = item.get("liveStreamingDetails") or {}
            # `actualEndTime` present means it HAS ended — a finished stream
            # still carries liveStreamingDetails, and reading only
            # `actualStartTime` would call every past broadcast live.
            if snippet.get("liveBroadcastContent") == "live" and not details.get("actualEndTime"):
                return Status(LIVE, title=snippet.get("title", ""),
                              url=f"https://www.youtube.com/watch?v={item['id']}")
        return Status(OFFLINE, url=url)
    except Exception as exc:                        # noqa: BLE001
        log.warning("youtube check for %s failed: %s", channel_id, type(exc).__name__)
        return Status(UNKNOWN, url=url)


def should_announce(previous: str, now: str) -> bool:
    """
    The whole of the announcing rule, in one place.

    Only an offline-to-live TRANSITION is worth saying out loud, and three
    cases have to be excluded or the bot becomes the thing people mute:

    - **`unknown` is not offline.** An API blip must not manufacture a
      transition when the next check succeeds.
    - **An empty previous state is not offline either.** That is a watch that
      has never been checked — announcing on it would mean every restart, and
      every newly added channel, shouting about a stream that has been running
      for six hours.
    - **live to live is nothing.** Obvious, and worth stating because a naive
      "if live: announce" is exactly the bug.
    """
    return previous == OFFLINE and now == LIVE
