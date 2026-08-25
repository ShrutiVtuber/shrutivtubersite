# SPDX-License-Identifier: AGPL-3.0-only
"""
The live room a workshop happens in.

Daily.co, chosen because chat and raised hands come with their prebuilt call
UI rather than needing to be built, and because recording is a flag rather than
a project.

**A room is made when she launches it, not when the workshop is created.** A
room that exists for weeks before anybody uses it is a URL circulating with
nothing to stop somebody wandering in; one made on the day, with an expiry, is
a door that opens once.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from shruti.core.config import get_settings

log = logging.getLogger(__name__)

API = "https://api.daily.co/v1"

# How long after the start a room stays open. Generous: a workshop that runs
# over should not throw everybody out, and a room nobody is in costs nothing.
ROOM_LIFE_HOURS = 12


class RoomUnavailable(RuntimeError):
    """Daily is not configured, or would not answer."""


def _headers() -> dict[str, str]:
    key = get_settings().daily_api_key
    if not key:
        raise RoomUnavailable("the live room service is not set up yet")
    return {"Authorization": f"Bearer {key}", "content-type": "application/json"}


async def create(name: str, starts_at: datetime | None, minutes: int | None) -> dict:
    """
    Make the room. Returns what the admin needs to show and to send.

    Recording is switched on here rather than left to be remembered on the day:
    a workshop whose recording nobody started is a promise broken to everybody
    who paid for one.
    """
    settings = get_settings()
    begins = starts_at or datetime.now(timezone.utc)
    expires = begins + timedelta(hours=ROOM_LIFE_HOURS)

    payload: dict[str, Any] = {
        "name": name,
        "privacy": "private",          # a token gets you in, a URL does not
        "properties": {
            "exp": int(expires.timestamp()),
            "enable_chat": True,
            "enable_hand_raising": True,
            "enable_screenshare": True,
            "enable_knocking": False,   # tokens decide, not a queue she watches
            "start_video_off": True,    # arriving on camera unasked is unkind
            "start_audio_off": True,
            "enable_recording": "cloud",
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{API}/rooms", headers=_headers(), json=payload)
        if r.status_code == 400 and "already exists" in r.text:
            # Launching twice is the ordinary accident, not an error. The room
            # that exists is the room she wanted.
            got = await client.get(f"{API}/rooms/{name}", headers=_headers())
            got.raise_for_status()
            return got.json()
        r.raise_for_status()
        return r.json()


async def token(room: str, *, owner: bool, name: str = "") -> str:
    """
    A key to one room, for one person.

    The room is private, so this is the only way in. Hers carries owner rights
    — starting the recording, removing somebody — and a guest's does not.
    """
    payload: dict[str, Any] = {
        "properties": {
            "room_name": room,
            "is_owner": owner,
            **({"user_name": name} if name else {}),
        }
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{API}/meeting-tokens", headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()["token"]


def url(room: str, meeting_token: str = "") -> str:
    domain = get_settings().daily_domain
    base = f"https://{domain}.daily.co/{room}"
    return f"{base}?t={meeting_token}" if meeting_token else base


async def recordings(room: str) -> list[dict]:
    """
    What was recorded in a room.

    Asked of Daily rather than tracked here: they know when a recording
    finished processing and this side would only be guessing.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{API}/recordings", headers=_headers(),
                             params={"room_name": room, "limit": 50})
        if r.status_code != 200:
            return []
        return r.json().get("data", [])


async def download_link(recording_id: str) -> str:
    """
    A link to one recording, from Daily, valid for a while.

    Not stored: these are large, they already live somewhere durable, and
    copying them here would mean paying twice to hold the same hours.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{API}/recordings/{recording_id}/access-link",
                             headers=_headers())
        if r.status_code != 200:
            return ""
        return r.json().get("download_link", "")
