# SPDX-License-Identifier: AGPL-3.0-only
"""
The store badges go up on their own.

⚠ **Nobody should have to remember.** A badge put up by hand on submission day
is a dead link for two days; one put up on approval day waits for somebody to
notice an email. So the site asks Apple and Google directly and renders
whatever they say.

⚠ **A failed request is not an answer.** This is the same trap `core/videos.py`
records — it cached an empty result over a good one and told the world she had
never streamed. Here the equivalent would be a live App Store badge vanishing
for the length of an outage. A lookup that SUCCEEDS and says "no such app" is a
fact and is honoured; a lookup that throws is nothing and keeps the last answer.
"""
from __future__ import annotations

import asyncio
import inspect
import re

import pytest

from shruti.core import stores


def code_of(function) -> str:
    """Source with comments and docstring stripped — see the other guards."""
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def markup_of(text: str) -> str:
    """
    An Astro file with its comments taken out.

    ⚠ **Fourth time today.** A guard that greps for a phrase finds it in the
    paragraph explaining why the phrase is absent — so the code can say the
    opposite of what the comment promises and the test stays green. This one
    caught itself: the component's comment says why there is no "coming soon"
    band, which read as a "coming soon" band.
    """
    text = re.sub(r"\{/\*.*?\*/\}", " ", text, flags=re.S)
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


def setup_function() -> None:
    stores._CACHE.update({"at": None, "ios": None,
                          "androidAt": None, "android": None})


def test_a_dead_lookup_keeps_the_badge_up(monkeypatch) -> None:
    """The failure that would take a live badge off the site."""
    live = {"url": "https://apps.apple.com/x", "name": "Shruti's Astrolabe"}

    async def ok(_client):
        return live

    async def boom(_client):
        raise TimeoutError("apple is having a moment")

    monkeypatch.setattr(stores, "_ask_apple", ok)
    assert asyncio.run(stores.ios(force=True)) == live

    monkeypatch.setattr(stores, "_ask_apple", boom)
    assert asyncio.run(stores.ios(force=True)) == live, (
        "an outage emptied the badge instead of keeping the last good answer"
    )


def test_a_real_no_is_honoured(monkeypatch) -> None:
    """
    ⚠ The other half, and they are easy to conflate. "Apple answered, and the
    app is not there" must take the badge DOWN — that is a withdrawal or a
    release that has not happened, and pretending otherwise is a dead link.
    """
    async def ok(_client):
        return {"url": "https://apps.apple.com/x"}

    async def gone(_client):
        return None

    monkeypatch.setattr(stores, "_ask_apple", ok)
    assert asyncio.run(stores.ios(force=True)) is not None
    monkeypatch.setattr(stores, "_ask_apple", gone)
    assert asyncio.run(stores.ios(force=True)) is None


def test_android_is_asked_the_same_way(monkeypatch) -> None:
    live = {"url": "https://play.google.com/store/apps/details?id=x"}

    async def ok(_client):
        return live

    async def boom(_client):
        raise ConnectionError("play is unreachable")

    monkeypatch.setattr(stores, "_ask_google", ok)
    assert asyncio.run(stores.android(force=True)) == live
    monkeypatch.setattr(stores, "_ask_google", boom)
    assert asyncio.run(stores.android(force=True)) == live


def test_the_cache_actually_caches(monkeypatch) -> None:
    """A badge on every page must not be a request on every page."""
    calls = {"n": 0}

    async def counted(_client):
        calls["n"] += 1
        return {"url": "https://apps.apple.com/x"}

    monkeypatch.setattr(stores, "_ask_apple", counted)
    asyncio.run(stores.ios(force=True))
    for _ in range(5):
        asyncio.run(stores.ios())
    assert calls["n"] == 1, f"asked Apple {calls['n']} times for one answer"


def test_play_is_read_by_status_not_by_scraping() -> None:
    """
    ⚠ Play has no lookup endpoint, so the listing page is all there is — but
    reading anything out of its HTML would break the day Google renames a
    class. The status code and the package id are the only two things checked.
    """
    body = code_of(stores._ask_google)
    assert "status_code" in body
    assert "ANDROID_PACKAGE" in body
    for fragile in ("class=", "soup", "findall", "<div"):
        assert fragile not in body, f"parsing Play's markup ({fragile})"


def test_the_page_shows_nothing_until_a_store_carries_it() -> None:
    """
    ⚠ No "coming soon". That is a promise with a date in it, and the date
    belongs to Apple's reviewers — and, for Android, to a company that is not
    registered yet.
    """
    from conftest import SITE
    raw = (SITE / "src" / "components" / "brand" / "GetTheApp.astro").read_text()
    band = markup_of(raw)
    assert "any &&" in band, "the band renders even when no store has the app"
    assert "coming soon" not in band.lower()
    # ⚠ And it must never take the page down with it.
    assert "catch" in band, "a store outage would throw on the home page"


def test_it_is_under_the_hero_and_on_the_instruments_page() -> None:
    from conftest import SITE
    home = markup_of((SITE / "src" / "pages" / "index.astro").read_text())
    assert "<GetTheApp />" in home
    # Her words: a major feature, so directly under the hero.
    assert home.index("</Hero>") < home.index("<GetTheApp />")
    assert home.index("<GetTheApp />") < home.index("<SupportBand")

    tools = markup_of((SITE / "src" / "pages" / "tools" / "index.astro").read_text())
    assert "<GetTheApp compact />" in tools
