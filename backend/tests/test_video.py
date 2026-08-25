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


def test_a_token_lasts_hours_not_minutes_or_days():
    """
    Four hours. Not a rule so much as a balance, but a wrong edit here is the
    kind that is only noticed by a student mid-lecture, so it is pinned.
    """
    assert video.TOKEN_LIFE_SECONDS == 4 * 60 * 60


def test_expiry_limits_the_link_and_never_the_person(monkeypatch):
    """
    The thing she actually asked about.

    Access lives in the entitlement and the token is only the door opening, so
    opening the same lesson twice gives two different working links. A student
    who bought a class keeps it for good; only the plastic keycard expires.
    """
    from shruti.core.config import get_settings

    monkeypatch.setenv("SHRUTI_BUNNY_LIBRARY_ID", "123456")
    monkeypatch.setenv("SHRUTI_BUNNY_TOKEN_AUTH_KEY", "test-key")
    get_settings.cache_clear()

    first = video.playback("bunny", "lecture-01", life_seconds=60)
    second = video.playback("bunny", "lecture-01", life_seconds=120)

    assert first["src"] != second["src"]          # a fresh one each time
    assert second["expiresAt"] > first["expiresAt"]
    assert first["ready"] and second["ready"]
    get_settings.cache_clear()


# ── an unconfigured provider must refuse, not improvise ─────────────────────

def test_cloudflare_refuses_without_a_domain(monkeypatch):
    """
    It used to answer with "customer-placeholder.cloudflarestream.com".

    That is a real-looking URL resolving to nothing, returned with
    `ready: True`. A paid lesson would have shown an empty player and said
    nothing, and from the admin it looked identical to a video still encoding.
    The module's own docstring already promised the opposite: "an unknown or
    unconfigured provider returns ready: false with a reason rather than a
    broken URL".
    """
    from shruti.core import video

    class Fake:
        cloudflare_stream_domain = ""
        bunny_library_id = ""
        bunny_stream_api_key = ""
        bunny_token_auth_key = ""
        bunny_cdn_hostname = ""

    monkeypatch.setattr(video, "get_settings", lambda: Fake())
    answer = video.playback("cloudflare", "abc123")
    assert answer["ready"] is False
    assert "not set up" in answer["reason"]
    assert "placeholder" not in str(answer)


def test_no_provider_is_offered_that_is_not_configured(monkeypatch):
    """
    The admin dropdown reads this. An option that exists but cannot work looks
    exactly as real as one that can.
    """
    from shruti.core import video

    class Nothing:
        bunny_library_id = ""
        bunny_stream_api_key = ""
        bunny_token_auth_key = ""
        cloudflare_stream_domain = ""

    monkeypatch.setattr(video, "get_settings", lambda: Nothing())
    assert video.providers() == []

    class BunnyOnly(Nothing):
        bunny_library_id = "12345"
        bunny_stream_api_key = "key"
        bunny_token_auth_key = "signing"

    monkeypatch.setattr(video, "get_settings", lambda: BunnyOnly())
    got = video.providers()
    assert [p["key"] for p in got] == ["bunny"]
    assert got[0]["protected"] is True


def test_a_provider_that_cannot_sign_says_so(monkeypatch):
    """
    A course sold for money that plays from an unsigned URL is a course anybody
    can hotlink. She should see which is which before choosing, not after.
    """
    from shruti.core import video

    class Unsigned:
        bunny_library_id = "12345"
        bunny_stream_api_key = "key"
        bunny_token_auth_key = ""            # no signing key
        cloudflare_stream_domain = "example.cloudflarestream.com"

    monkeypatch.setattr(video, "get_settings", lambda: Unsigned())
    by_key = {p["key"]: p for p in video.providers()}
    assert by_key["bunny"]["protected"] is False
    assert by_key["cloudflare"]["protected"] is False


def test_the_provider_route_is_not_shadowed_by_a_catch_all():
    """
    FastAPI matches in declaration order, so a `/admin/{something}` declared
    earlier would swallow `/admin/video-providers` and the dropdown would go
    silently empty — which reads exactly like "no providers are configured".

    That has bitten this codebase four times, every time as silence rather than
    an error.
    """
    from shruti.api.routes.classes import router

    paths = [r.path for r in router.routes]
    here = paths.index("/api/classes/admin/video-providers")
    prefix = "/api/classes/admin/"
    for i, other in enumerate(paths):
        rest = other[len(prefix):] if other.startswith(prefix) else ""
        # A catch-all directly at the admin root is the one that would shadow.
        if rest.startswith("{") and rest.count("/") == 0:
            assert i > here, f"{other} is declared before video-providers and shadows it"
