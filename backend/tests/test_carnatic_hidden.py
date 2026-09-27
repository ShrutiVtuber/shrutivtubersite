# SPDX-License-Identifier: AGPL-3.0-only
"""
While Swara Studio is unpublished, its API answers only her and the site's own
server. The pages already 404 for everyone else; these tests hold the API to
the same rule, so an address someone guessed shows nothing either.
"""
from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from shruti.api import deps
from shruti.api.routes import carnatic, carnatic_community, carnatic_course, carnatic_studio


class _Request:
    def __init__(self, headers: dict[str, str] | None = None) -> None:
        self.headers = headers or {}
        self.cookies: dict[str, str] = {}


def _hidden(monkeypatch, *, live: bool, admin: bool, secret: str = "s3cret") -> None:
    async def sections_live(session):
        return {"carnatic": live}

    async def require_admin(request, session):
        if not admin:
            raise HTTPException(401, "not authenticated")
        return "her@example.com"

    import shruti.core.settings_store as store
    monkeypatch.setattr(store, "sections_live", sections_live)
    monkeypatch.setattr(deps, "require_admin", require_admin)
    monkeypatch.setenv("SHRUTI_INTERNAL_SECRET", secret)


def _call(request: _Request) -> None:
    asyncio.run(deps.school_open(request, session=None))


def test_a_published_school_is_open_to_everyone(monkeypatch) -> None:
    _hidden(monkeypatch, live=True, admin=False)
    _call(_Request())


def test_a_hidden_school_is_not_found_for_a_stranger(monkeypatch) -> None:
    _hidden(monkeypatch, live=False, admin=False)
    with pytest.raises(HTTPException) as e:
        _call(_Request())
    assert e.value.status_code == 404


def test_a_hidden_school_answers_her(monkeypatch) -> None:
    _hidden(monkeypatch, live=False, admin=True)
    _call(_Request())


def test_a_hidden_school_answers_the_site_rendering_her_preview(monkeypatch) -> None:
    _hidden(monkeypatch, live=False, admin=False)
    _call(_Request({"X-Shruti-Internal": "s3cret"}))


@pytest.mark.parametrize("given", ["", "wrong", "s3cre"])
def test_a_wrong_secret_is_a_stranger(monkeypatch, given) -> None:
    _hidden(monkeypatch, live=False, admin=False)
    with pytest.raises(HTTPException) as e:
        _call(_Request({"X-Shruti-Internal": given}))
    assert e.value.status_code == 404


def test_no_secret_configured_opens_nothing(monkeypatch) -> None:
    _hidden(monkeypatch, live=False, admin=False, secret="")
    with pytest.raises(HTTPException) as e:
        _call(_Request({"X-Shruti-Internal": ""}))
    assert e.value.status_code == 404


@pytest.mark.parametrize("module", [carnatic, carnatic_course, carnatic_community])
def test_every_public_school_router_is_behind_the_gate(module) -> None:
    calls = [d.dependency for d in module.router.dependencies]
    assert deps.school_open in calls


def test_the_studio_is_hers_alone_whatever_the_setting() -> None:
    assert deps.require_admin in [d.dependency for d in carnatic_studio.router.dependencies]
