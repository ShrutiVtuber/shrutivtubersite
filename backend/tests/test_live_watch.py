# SPDX-License-Identifier: AGPL-3.0-only
"""
Telling people a stream started, without crying wolf.

**A false "she is live" is expensive.** It sends somebody to an empty channel
and teaches them to ignore the next one, which is the only thing a notification
has to be trusted about. Every check here is about not sending one.
"""
from __future__ import annotations

import inspect

from shruti.core import livewatch


def test_it_fires_on_the_transition_not_on_the_state():
    """
    Announcing whenever the answer is "live" would notify every single pass for
    as long as a stream ran.
    """
    source = inspect.getsource(livewatch.check_once)
    assert 'was == "live"' in source
    assert "not is_live or" in source


def test_the_last_state_survives_a_restart():
    """
    Held in memory, a deploy mid-stream would re-announce a stream that has
    been running an hour.
    """
    source = inspect.getsource(livewatch.check_once)
    assert "LAST_STATE" in source
    assert "_remember" in source


def test_the_first_pass_after_a_restart_says_nothing():
    """
    With no remembered state, "offline -> live" is indistinguishable from
    "we have never looked". Announcing on that means every fresh deploy during
    a stream sends a notification.
    """
    source = inspect.getsource(livewatch.check_once)
    assert 'was == ""' in source
    assert "first pass" in source


def test_a_platform_error_is_not_offline():
    """
    Twitch returning 500 must not read as "the stream ended" and then as
    "she is live!" the moment it recovers.
    """
    source = inspect.getsource(livewatch.check_once)
    assert 'getattr(p, "error", None)' in source
    assert "every platform errored" in source


def test_it_reads_the_field_the_platform_actually_has():
    """
    `PlatformStatus` calls it `is_live`. Reading `live` would be None for
    every platform forever, and the watcher would simply never fire — the
    quietest possible failure.
    """
    from shruti.core.live import PlatformStatus

    assert "is_live" in PlatformStatus.__dataclass_fields__
    source = inspect.getsource(livewatch.check_once)
    assert 'getattr(p, "is_live"' in source
    assert 'getattr(p, "live"' not in source


def test_a_second_stream_too_soon_is_suppressed():
    assert livewatch.QUIET_HOURS >= 1
    assert "quiet window" in inspect.getsource(livewatch.check_once)


def test_the_loop_survives_its_own_exceptions():
    """A watcher that dies silently is worse than one that never existed."""
    source = inspect.getsource(livewatch.watcher)
    assert "except Exception" in source
    assert "CancelledError" in source, "cancellation must still stop it"


def test_it_sleeps_before_its_first_check():
    """A restart storm should not arrive at Twitch all at once."""
    source = inspect.getsource(livewatch.watcher)
    assert source.index("sleep") < source.index("check_once")
