# SPDX-License-Identifier: AGPL-3.0-only
"""
One account, two places.

She asked that somebody be able to sign up on their phone — "not the website,
so we can make it easier" — and that the same account work in both. A phone has
no cookie jar worth relying on, so the app holds the session itself and sends it
as a bearer token; the website carries on with the httpOnly cookie it has always
had, and neither knows about the other.

Two things are worth guarding here and both are about the browser, not the app:
the cookie must win when both are present, and the website must never ask for a
token in the body — the httpOnly flag exists to keep that value away from any
script running on the page.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from shruti.api.routes.accounts import SignInIn, SignUpIn, session_token
from shruti.core.sessions import SESSION_COOKIE


class _Request:
    """Enough of a Request for the chooser: cookies and headers."""

    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {}
        self.headers = headers or {}


def test_the_app_is_read_from_the_authorization_header() -> None:
    r = _Request(headers={"authorization": "Bearer abc.def.ghi"})
    assert session_token(r) == "abc.def.ghi"


def test_the_scheme_is_matched_whatever_its_case() -> None:
    for scheme in ("Bearer", "bearer", "BEARER", "BeArEr"):
        r = _Request(headers={"authorization": f"{scheme} tok"})
        assert session_token(r) == "tok", scheme


def test_the_browsers_cookie_wins_over_any_header() -> None:
    """
    The one that would be a real hole.

    A script on the page cannot read an httpOnly cookie — that is the whole
    point of the flag. If a header could override it, that script could pick
    whose account the request runs as without ever reading anything.
    """
    r = _Request(cookies={SESSION_COOKIE: "the-browsers"},
                 headers={"authorization": "Bearer someone-elses"})
    assert session_token(r) == "the-browsers"


@pytest.mark.parametrize("header", [
    "Basic dXNlcjpwYXNz",       # a different scheme entirely
    "Bearer",                    # the scheme with nothing after it
    "Bearer   ",                 # and with only space after it
    "",
])
def test_anything_that_is_not_a_bearer_token_is_nothing(header: str) -> None:
    assert session_token(_Request(headers={"authorization": header})) is None


def test_a_request_carrying_neither_is_nobody() -> None:
    assert session_token(_Request()) is None


def test_asking_for_a_token_is_opt_in() -> None:
    """Default off, so the website's replies are unchanged by any of this."""
    assert SignUpIn(email="a@b.com").bearer is False
    assert SignInIn(email="a@b.com").bearer is False
    assert SignUpIn(email="a@b.com", bearer=True).bearer is True
    assert SignInIn(email="a@b.com", bearer=True).bearer is True


def test_the_website_never_asks_for_one() -> None:
    """
    A token in a JSON reply is readable by any script on the page, which is
    exactly what the httpOnly cookie is for. The site's own forms must not ask.
    """
    site = Path(__file__).resolve().parents[2] / "frontend" / "site" / "src"
    offenders = [
        str(p.relative_to(site))
        for p in site.rglob("*.astro")
        if "bearer" in p.read_text().lower() and "/api/account/sign" in p.read_text()
    ]
    assert not offenders, (
        "these pages ask the account API for a bearer token: "
        f"{offenders}. The browser has a cookie; only the app should ask."
    )
