# SPDX-License-Identifier: AGPL-3.0-only
"""
Live status. Every test here is about a failure mode, because the success path
is two HTTP calls and the failure paths are where a site starts lying.
"""

import pytest

from shruti.core import live as L


def _settings(monkeypatch, **env):
    from shruti.core.config import get_settings

    get_settings.cache_clear()
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return get_settings


def _reset_cache():
    L._cache._value = None
    L._twitch_token["token"] = None


@pytest.mark.asyncio
async def test_unconfigured_reports_offline_on_both(monkeypatch):
    get_settings = _settings(
        monkeypatch, SHRUTI_TWITCH_CLIENT_ID="", SHRUTI_TWITCH_CLIENT_SECRET="",
        SHRUTI_YOUTUBE_CHANNEL_ID="", SHRUTI_YOUTUBE_API_KEY="",
    )
    _reset_cache()
    s = await L.status()
    assert s.any_live is False
    assert {p.platform for p in s.platforms} == {"twitch", "youtube"}
    assert all(p.error for p in s.platforms)
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_one_platform_failing_does_not_take_the_other_down(monkeypatch):
    """
    The whole reason the two checks run independently. A Twitch outage must not
    make a live YouTube stream invisible.
    """
    get_settings = _settings(monkeypatch, SHRUTI_YOUTUBE_CHANNEL_ID="UC_x")
    _reset_cache()

    async def boom(client):
        raise RuntimeError("twitch is down")

    async def fine(client):
        return L.PlatformStatus(platform="youtube", is_live=True, title="live now",
                                watch_url="https://youtu.be/x")

    monkeypatch.setattr(L, "_check_twitch", boom)
    monkeypatch.setattr(L, "_check_youtube", fine)

    s = await L.status()
    assert s.any_live is True
    twitch = next(p for p in s.platforms if p.platform == "twitch")
    youtube = next(p for p in s.platforms if p.platform == "youtube")
    assert twitch.is_live is False and twitch.error == "RuntimeError"
    assert youtube.is_live is True
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_a_degraded_check_is_distinguishable_from_being_offline(monkeypatch):
    """
    "Offline" and "we could not tell" are different facts. Collapsing them hides
    an outage behind a plausible answer.
    """
    get_settings = _settings(monkeypatch)
    _reset_cache()

    async def broken(client):
        return L.PlatformStatus(platform="twitch", error="TimeoutError")

    async def quiet(client):
        return L.PlatformStatus(platform="youtube")

    monkeypatch.setattr(L, "_check_twitch", broken)
    monkeypatch.setattr(L, "_check_youtube", quiet)
    s = await L.status()
    errs = {p.platform: p.error for p in s.platforms}
    assert errs["twitch"] == "TimeoutError"
    assert errs["youtube"] == ""
    get_settings.cache_clear()


def test_primary_prefers_the_configured_platform_during_a_simulcast():
    """
    Simulcasting is the normal case, not an edge case. Both live means one
    stream, so the call to action must pick one rather than offer two.
    """
    s = L.LiveStatus(platforms=[
        L.PlatformStatus(platform="twitch", is_live=True),
        L.PlatformStatus(platform="youtube", is_live=True),
    ])
    assert s.primary("youtube").platform == "youtube"
    assert s.primary("twitch").platform == "twitch"


def test_primary_falls_back_to_whichever_is_live():
    s = L.LiveStatus(platforms=[
        L.PlatformStatus(platform="twitch", is_live=False),
        L.PlatformStatus(platform="youtube", is_live=True),
    ])
    assert s.primary("twitch").platform == "youtube"


def test_primary_is_none_when_nothing_is_live():
    s = L.LiveStatus(platforms=[L.PlatformStatus(platform="twitch")])
    assert s.primary("twitch") is None


@pytest.mark.asyncio
async def test_youtube_without_a_key_says_so_rather_than_guessing(monkeypatch):
    """
    The RSS feed lists uploads, not streams. Inferring "live" from a recent
    upload would be a guess dressed as a fact.
    """
    get_settings = _settings(monkeypatch, SHRUTI_YOUTUBE_CHANNEL_ID="UC_x",
                             SHRUTI_YOUTUBE_API_KEY="")
    _reset_cache()

    class Feed:
        status_code = 200
        text = "<feed><yt:videoId>abcdefghijk</yt:videoId></feed>"
        def raise_for_status(self): pass

    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def get(self, url, **kw): return Feed()
        async def post(self, url, **kw): raise AssertionError("should not post")

    monkeypatch.setattr(L.httpx, "AsyncClient", lambda **kw: Client())
    result = await L._check_youtube(Client())
    assert result.is_live is False
    assert "api key" in result.error
    get_settings.cache_clear()


def test_the_video_id_pattern_matches_real_feed_markup():
    ids = L._VIDEO_ID.findall(
        "<entry><yt:videoId>8cOyaB86LRY</yt:videoId></entry>"
        "<entry><yt:videoId>dQw4w9WgXcQ</yt:videoId></entry>"
    )
    assert ids == ["8cOyaB86LRY", "dQw4w9WgXcQ"]
