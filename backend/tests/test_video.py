# SPDX-License-Identifier: AGPL-3.0-only
"""
Where a lesson's video plays from, and whether the link can be shared.

The failure this guards against is quiet: an unsigned URL plays perfectly for
the person who paid and equally perfectly for everybody they send it to. It
looks like it works right up until the course is free.
"""
from __future__ import annotations

import hashlib
import inspect

from shruti.core import video


def test_nothing_is_offered_for_a_lesson_with_no_video():
    got = video.playback("bunny", "")
    assert got["ready"] is False
    assert "no video" in got["reason"]


def test_an_unknown_provider_says_so_rather_than_guessing():
    """
    A wrong URL that half-works is harder to diagnose than a refusal. It also
    names the provider, because the usual cause is a typo in one field.
    """
    got = video.playback("vimeo", "abc")
    assert got["ready"] is False
    assert "vimeo" in got["reason"]


def test_bunny_signs_with_the_documented_recipe(monkeypatch):
    """
    SHA-256 of key + video id + expiry. Getting this wrong gives a token
    Bunny rejects, which looks like "the video is broken" rather than like a
    signature problem.
    """
    from shruti.core.config import get_settings

    monkeypatch.setenv("SHRUTI_BUNNY_LIBRARY_ID", "123456")
    monkeypatch.setenv("SHRUTI_BUNNY_TOKEN_AUTH_KEY", "test-key")
    get_settings.cache_clear()

    got = video.playback("bunny", "vid-1", life_seconds=60)
    assert got["ready"] is True
    assert got["unprotected"] is False

    expires = got["expiresAt"]
    expected = hashlib.sha256(f"test-key{'vid-1'}{expires}".encode()).hexdigest()
    assert f"token={expected}" in got["src"]
    get_settings.cache_clear()


def test_an_unprotected_link_says_that_it_is_unprotected(monkeypatch):
    """
    Configured without a token key, Bunny still plays — and that is the
    dangerous state, because it works. It has to announce itself so the admin
    can show it rather than leaving a paid course quietly open.
    """
    from shruti.core.config import get_settings

    monkeypatch.setenv("SHRUTI_BUNNY_LIBRARY_ID", "123456")
    monkeypatch.delenv("SHRUTI_BUNNY_TOKEN_AUTH_KEY", raising=False)
    get_settings.cache_clear()

    got = video.playback("bunny", "vid-1")
    assert got["ready"] is True
    assert got["unprotected"] is True
    assert got["expiresAt"] is None
    get_settings.cache_clear()


def test_bunny_without_a_library_is_not_ready(monkeypatch):
    from shruti.core.config import get_settings

    monkeypatch.delenv("SHRUTI_BUNNY_LIBRARY_ID", raising=False)
    get_settings.cache_clear()
    assert video.playback("bunny", "vid-1")["ready"] is False
    get_settings.cache_clear()


def test_both_providers_are_reachable_so_a_migration_can_be_gradual():
    """
    Courses start on Bunny and move to Cloudflare when they are worth more.
    That is a planned migration, so both must be live at once — a lesson at a
    time, not a big bang.
    """
    source = inspect.getsource(video.playback)
    assert "bunny" in source and "cloudflare" in source


def test_the_lesson_only_ever_knows_a_provider_and_an_id():
    """
    Everything provider-shaped lives in this module. If a URL or a library id
    ever leaks onto the model, switching stops being a field and becomes a
    migration.
    """
    from shruti.models import Lesson

    fields = set(Lesson.model_fields)
    assert {"video_provider", "video_id"} <= fields
    assert not {"video_url", "library_id", "bunny_id", "embed"} & fields
