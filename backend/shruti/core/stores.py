# SPDX-License-Identifier: AGPL-3.0-only
"""
Whether the app is actually buyable yet, asked of the stores themselves.

⚠ **Nobody has to remember to switch this on.** A link put up by hand the day
an app is submitted is a dead link for two days; a link put up by hand the day
it is approved is a link that waits for somebody to notice the approval email.
Both were avoidable by asking Apple, which will say.

The App Store's lookup endpoint is public and needs no key: it answers with the
app when it is live and with nothing when it is not, which is exactly the
question a badge on a page is asking.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

log = logging.getLogger(__name__)

LOOKUP = "https://itunes.apple.com/lookup"

#: Apple's id for Shruti's Astrolabe. Overridable so a second app needs no code.
IOS_APP_ID = os.environ.get("SHRUTI_IOS_APP_ID", "6811031925").strip()

#: The Android package. Play has no lookup endpoint, so its listing page is
#: the only public thing that knows — see `android()`.
ANDROID_PACKAGE = os.environ.get(
    "SHRUTI_ANDROID_PACKAGE", "com.shrutivtuber.astrolabe").strip()
PLAY = "https://play.google.com/store/apps/details"

#: An approval is a once-ever event, so this can be slow. Half an hour means a
#: release shows up within half an hour of Apple flipping it, which is soon
#: enough for something nobody is watching the clock on.
CACHE_MINUTES = 30

_CACHE: dict[str, Any] = {"at": None, "ios": None,
                          "androidAt": None, "android": None}


async def _ask_apple(client: httpx.AsyncClient) -> dict | None:
    """What the App Store says, or None if it says the app is not there."""
    r = await client.get(
        LOOKUP,
        params={"id": IOS_APP_ID, "country": "us", "entity": "software"},
        timeout=10,
    )
    r.raise_for_status()
    # ⚠ Apple serves this as text/javascript, so .json() has to be told not to
    # care about the content type.
    body = r.json()
    results = body.get("results") or []
    if not results:
        return None
    app = results[0]
    return {
        "url": app.get("trackViewUrl"),
        "name": app.get("trackName"),
        "version": app.get("version"),
        "released": app.get("currentVersionReleaseDate"),
    }


async def ios(force: bool = False) -> dict | None:
    """
    The iPhone app if it is live, None if it is not. Never raises.

    ⚠ **A failed request is not an answer.** A lookup that succeeds and says
    "no such app" is a fact — it is not released, or it has been taken down —
    and is honoured. A lookup that times out is nothing at all, and returning
    None for it would take a live badge off the site for as long as the outage
    lasted. The same trap videos.py documents, met a second time.
    """
    now = datetime.now(timezone.utc)
    fresh = _CACHE["at"] and now - _CACHE["at"] < timedelta(minutes=CACHE_MINUTES)
    if not force and fresh:
        return _CACHE["ios"]

    try:
        async with httpx.AsyncClient() as client:
            answer = await _ask_apple(client)
    except Exception as exc:                                   # noqa: BLE001
        log.warning("the App Store could not be asked: %s", type(exc).__name__)
        return _CACHE["ios"]

    _CACHE["at"] = now
    _CACHE["ios"] = answer
    return answer


async def _ask_google(client: httpx.AsyncClient) -> dict | None:
    """
    Whether Play carries the app.

    ⚠ Play has no lookup endpoint. The listing page is the only public thing
    that knows, and it answers 404 for a package it does not carry — which
    covers both "never published" and "taken down". So this asks for the page
    and reads the status, and nothing else about it: no parsing, no scraping,
    nothing that breaks when Google changes a class name.
    """
    url = f"{PLAY}?id={ANDROID_PACKAGE}&hl=en"
    r = await client.get(url, timeout=10, follow_redirects=True)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    # ⚠ A 200 that does not mention the package is not the app — Play serves a
    # generic page in some regions rather than a 404.
    if ANDROID_PACKAGE not in r.text:
        return None
    return {"url": f"{PLAY}?id={ANDROID_PACKAGE}", "package": ANDROID_PACKAGE}


async def android(force: bool = False) -> dict | None:
    """
    The Android app if Play carries it, None if it does not. Never raises.

    ⚠ Same rule as `ios`: a request that fails is not an answer, and must not
    take a live badge off the site for the length of an outage.
    """
    now = datetime.now(timezone.utc)
    fresh = (_CACHE["androidAt"]
             and now - _CACHE["androidAt"] < timedelta(minutes=CACHE_MINUTES))
    if not force and fresh:
        return _CACHE["android"]

    try:
        async with httpx.AsyncClient() as client:
            answer = await _ask_google(client)
    except Exception as exc:                                   # noqa: BLE001
        log.warning("Play could not be asked: %s", type(exc).__name__)
        return _CACHE["android"]

    _CACHE["androidAt"] = now
    _CACHE["android"] = answer
    return answer
