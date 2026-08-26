# SPDX-License-Identifier: AGPL-3.0-only
"""
Anything that sends somebody to another site must be a LINK, not a form.

The site's CSP carries `form-action 'self'`, and that directive governs the
whole redirect chain following a form submission — not merely where the form
points. So a form that posts here and is answered with a redirect to another
origin is blocked by the browser, silently: nothing in the network tab, nothing
in the server log, because the server answered perfectly.

It cost an afternoon on the Twitch authorisation, and `curl` reproduces none of
it — curl does not implement CSP. So the guard is structural instead.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()

# Somewhere a person is deliberately sent off-site.
OFF_SITE = ("id.twitch.tv", "discord.com/oauth2", "accounts.google.com",
            "connect.stripe.com")


def _pages() -> list[Path]:
    return sorted(SRC.rglob("*.astro"))


def test_the_csp_still_restricts_form_action() -> None:
    """
    If this ever stops being true the guard below is unnecessary — but it is
    also a security property worth keeping, so it should be a decision rather
    than a drift.
    """
    caddy = SRC.parents[2] / "deploy" / "shrutivtuber.caddy"
    if not caddy.is_file():
        pytest.skip("deploy config not mounted")
    assert "form-action 'self'" in caddy.read_text()


def test_nothing_redirects_off_site_from_a_form_post() -> None:
    """
    The specific failure: `Astro.redirect(<another origin>)` reached from a
    POST handler. Allowed by the server, refused by the browser, invisible to
    both.
    """
    offenders = []
    for page in _pages():
        body = page.read_text(encoding="utf-8")
        if "Astro.request.method === \"POST\"" not in body:
            continue
        for match in re.finditer(r"Astro\.redirect\(([^)]*)\)", body):
            target = match.group(1)
            # A redirect to a path on this site is fine — that is 'self'.
            if target.strip().startswith(('"/', "'/", "`/")):
                continue
            # A variable holding a URL is the dangerous case. Flag it unless the
            # file says why it is safe.
            if "safeNext" in target or "next" in target.lower():
                continue
            offenders.append(f"{page.relative_to(SRC)}: Astro.redirect({target})")
    assert not offenders, (
        "these redirect somewhere unknown from a form POST, which the CSP's "
        "form-action will block in a browser while working perfectly in "
        "curl:\n  " + "\n  ".join(offenders))


def test_the_twitch_authorisation_is_a_link() -> None:
    """The one this was found on."""
    body = (SRC / "pages" / "admin" / "twitch.astro").read_text(encoding="utf-8")
    assert "auth.url" in body
    assert "<Button href={auth.url}" in body, (
        "the authorise control must be a link — a form is blocked by "
        "form-action 'self' and fails silently")
