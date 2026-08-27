# SPDX-License-Identifier: AGPL-3.0-only
"""
Who may put this site in an iframe.

Two requirements that pull against each other:

  - **/admin/preview frames the real page**, which is the whole point of it —
    edit the words with the page in front of you.
  - **The admin itself must never be framed.** It has one-click destructive
    controls, and a transparent iframe over a "Delete" button is the entire
    clickjacking attack.

So the site is `frame-ancestors 'self'` and the admin is `'none'`, and the
distinction has to be made with a MATCHER: a site-wide header overwrites the
admin handler's own policy. That is not theoretical — it is what happened, and
the admin's `'none'` never reached a browser.
"""
from __future__ import annotations

import re
from pathlib import Path

# The runner mounts the two proxy configs beside the app, not a whole repo.
ROOT = Path("/app") if Path("/app/Caddyfile.internal").exists() \
    else Path(__file__).resolve().parents[2]


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_the_site_may_be_framed_by_itself_only() -> None:
    for rel in ("Caddyfile.internal", "deploy/shrutivtuber.caddy"):
        conf = _text(rel)
        assert "frame-ancestors 'self'" in conf, f"{rel} does not allow the preview"


def test_the_admin_may_not_be_framed_at_all() -> None:
    for rel in ("Caddyfile.internal", "deploy/shrutivtuber.caddy"):
        conf = _text(rel)
        assert "frame-ancestors 'none'" in conf, f"{rel} lets the admin be framed"


def test_the_two_are_separated_by_a_matcher() -> None:
    """
    Without one, whichever header is set last wins for every path — and the
    admin quietly inherits the site's looser policy.
    """
    internal = _text("Caddyfile.internal")
    assert "@framable not path /admin /admin/*" in internal
    prod = _text("deploy/shrutivtuber.caddy")
    assert "@admin path /admin /admin/*" in prod


def test_the_admin_may_embed_the_site() -> None:
    """
    `frame-src` is the OPPOSITE of `frame-ancestors` and the two are easy to
    confuse: frame-ancestors is who may embed us, frame-src is what we may
    embed. The preview was blocked for a second round because only the first
    had been fixed — the admin was allowed to embed YouTube and Twitch and
    nothing else, including nothing from its own origin.
    """
    for rel in ("Caddyfile.internal", "deploy/shrutivtuber.caddy"):
        conf = _text(rel)
        assert "frame-src 'self'" in conf, f"{rel} will not let the admin embed the page"


def test_production_and_local_agree() -> None:
    """
    The local proxy set NEITHER directive, so the preview worked here and was
    blocked on the live site — twice, for two different directives, and each
    time the local check said fine.

    Both halves are compared now, not just the one that broke first.
    """
    def policy(conf: str) -> tuple[set[str], set[str]]:
        return (set(re.findall(r"frame-ancestors '([\w-]+)'", conf)),
                set(re.findall(r"frame-src '([\w-]+)'", conf)))

    local = policy(_text("Caddyfile.internal"))
    prod = policy(_text("deploy/shrutivtuber.caddy"))
    assert local == prod, f"local {local} and production {prod} disagree"
    assert local == ({"self", "none"}, {"self"})
