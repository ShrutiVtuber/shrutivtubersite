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


# ── who may frame what ──────────────────────────────────────────────────────


def _both_caddies() -> list[tuple[str, str]]:
    """
    Production AND local.

    These two have diverged before, and it was expensive: local had no
    site-wide CSP at all, so `/admin/preview` framed the site perfectly here
    and was blocked in production. A framing rule proved on one machine and
    absent on the other is the same bug waiting.
    """
    root = SRC.parents[2]
    found = []
    for name, path in (("production", root / "deploy" / "shrutivtuber.caddy"),
                       ("local", root / "Caddyfile.internal")):
        if path.is_file():
            found.append((name, path.read_text(encoding="utf-8")))
    if not found:
        pytest.skip("no caddy config mounted")
    return found


def test_the_embed_is_the_only_path_anyone_may_frame() -> None:
    """
    Three tiers, and each is deliberate: the admin may be framed by nobody,
    because a transparent iframe over a one-click Delete is the whole
    clickjacking attack; the site by itself, because /admin/preview embeds the
    real page; and /embed by anybody, because another astrologer putting the
    wheel in their own post is the best inbound link this project has.

    That last one is safe because the embed has no authority to borrow — no
    session, no cookie, nothing to click. It stops being safe the moment it
    grows any of those.
    """
    for where, text in _both_caddies():
        assert "@embed path /embed /embed/*" in text, f"{where}: /embed is not matched"
        assert "frame-ancestors *" in text, f"{where}: /embed cannot be framed"
        assert "frame-ancestors 'none'" in text, f"{where}: the admin is framable"


def test_the_open_framing_is_scoped_to_the_embed_and_nothing_else() -> None:
    """
    `frame-ancestors *` must appear only on the embed's own header. Anywhere
    else it would let another page frame something that can act for a reader.
    """
    for where, text in _both_caddies():
        for line in text.splitlines():
            if "frame-ancestors *" in line:
                assert "@embed" in line, \
                    f"{where}: open framing on a line that is not the embed's: {line.strip()[:80]}"


def test_the_embed_carries_no_session_and_no_form() -> None:
    """
    A page other sites may frame must have nothing worth borrowing. `form-action
    'none'` on the production header says so in the policy as well as in the
    markup.
    """
    embed = SRC / "pages" / "embed" / "wheel.astro"
    assert embed.is_file()
    text = embed.read_text(encoding="utf-8")
    assert "<form" not in text, "the embed has a form"
    assert "account(" not in text and "cookies" not in text.lower().replace("no cookie", ""), \
        "the embed reads a session"
