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
# The three that redirect to Stripe. Allowed only because the CSP names those
# origins; adding a page here without adding its origin there reintroduces the
# silent failure.
PAYMENT_PAGES = {
    "pages/account.astro",
    "pages/shop/[slug].astro",
    "pages/support.astro",
}


def _pages() -> list[Path]:
    return sorted(SRC.rglob("*.astro"))


def _caddy() -> str:
    caddy = SRC.parents[2] / "deploy" / "shrutivtuber.caddy"
    if not caddy.is_file():
        pytest.skip("deploy config not mounted")
    return caddy.read_text()


def test_the_csp_names_stripe_or_nobody_can_pay() -> None:
    """
    Buying, supporting and managing a subscription are each a POST here
    answered with a redirect to Stripe. With `form-action 'self'` alone the
    browser blocks that redirect **after the session has been created** — the
    server logs a clean 303, Stripe logs a session, and the buyer sees a page
    that did nothing.

    This is the guard for a bug that shipped: it was found only because the
    same mechanism broke the Twitch button, which somebody happened to click.
    """
    caddy = _caddy()
    assert "checkout.stripe.com" in caddy, "nobody can buy anything"
    assert "billing.stripe.com" in caddy, "nobody can manage a subscription"


def test_form_action_is_still_restricted_to_a_named_list() -> None:
    """
    Widened, not removed. `form-action` with a wildcard would let any injected
    form post anywhere, which is the attack the directive exists to stop.
    """
    caddy = _caddy()
    assert "form-action 'self'" in caddy
    assert "form-action *" not in caddy


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
            # Payment redirects are allowed BECAUSE the CSP names their
            # destinations — asserted above. They cannot become links: creating
            # a Stripe session has side effects and its URL is single-use, so a
            # link would mint one on every page view.
            if page.relative_to(SRC).as_posix() in PAYMENT_PAGES:
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
