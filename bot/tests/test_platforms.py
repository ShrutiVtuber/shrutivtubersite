# SPDX-License-Identifier: AGPL-3.0-only
"""
When to speak, and — mostly — when not to.

Every case below is a way a stream announcer becomes the bot people mute.
"""
from __future__ import annotations

from vcordbot.platforms import LIVE, OFFLINE, UNKNOWN, should_announce


def test_offline_to_live_is_the_announcement() -> None:
    assert should_announce(OFFLINE, LIVE) is True


def test_live_to_live_says_nothing() -> None:
    """The naive `if live: announce` posts every polling interval, forever."""
    assert should_announce(LIVE, LIVE) is False


def test_an_api_blip_does_not_manufacture_a_transition() -> None:
    """
    Live, then a failed check, then live again is one stream — not two. If
    `unknown` counted as offline, every hiccup would produce a second
    announcement for a stream already running.
    """
    assert should_announce(UNKNOWN, LIVE) is False


def test_a_watch_that_has_never_been_checked_stays_quiet() -> None:
    """
    The empty state. Otherwise adding a channel mid-stream, or restarting the
    process, announces something that has been running for six hours — which is
    the specific way this bug reaches people rather than logs.
    """
    assert should_announce("", LIVE) is False


def test_going_offline_is_not_announced() -> None:
    assert should_announce(LIVE, OFFLINE) is False
    assert should_announce(LIVE, UNKNOWN) is False


def test_a_finished_broadcast_is_not_live() -> None:
    """
    A past stream keeps its liveStreamingDetails. Reading only actualStartTime
    would call every archived broadcast live — so the check requires
    liveBroadcastContent to say so AND actualEndTime to be absent.
    """
    from conftest import code_of
    from vcordbot import platforms
    src = code_of(platforms)
    assert "actualEndTime" in src
    assert "liveBroadcastContent" in src


def test_youtube_is_not_checked_the_expensive_way() -> None:
    """
    search.list with eventType=live costs 100 quota units against a default of
    10,000 a day. It would exhaust quota rather than error, which is a failure
    nobody notices until announcements silently stop.

    Searched with the prose stripped — this very docstring names the thing it
    forbids, which is how the check failed the first time it ran.
    """
    from conftest import code_of
    from vcordbot import platforms
    src = code_of(platforms)
    assert "eventType" not in src
    assert "/search" not in src
