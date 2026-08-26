# SPDX-License-Identifier: AGPL-3.0-only
"""
A page nothing links to is a page nobody finds.

`/collab` and `/official` were built, tested, deployed, listed in the sitemap —
and reachable only by typing the address. Both were found by her asking why she
could not get to them, which is the expensive way.

It is the same shape as the half-built features the August audit turned up: two
working halves, nothing wrong with either, and no error anywhere. Grep finds
nothing, because nothing is marked incomplete.

This checks the sitemap against the links in the pages and the chrome, because
the sitemap is the list of pages we have promised the world exist.
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

# Reached by a token, a link somebody was sent, or a redirect — never by
# browsing, and deliberately so.
NOT_BROWSED = {
    "/chart", "/overlay", "/admin", "/signin", "/signup", "/account",
    "/newsletter/confirm", "/newsletter/unsubscribed", "/newsletter/preferences",
    "/coming-soon", "/nativity",
}


def _sitemap_paths() -> list[str]:
    text = (SRC / "pages" / "sitemap.xml.ts").read_text(encoding="utf-8")
    return [p for p in re.findall(r'\["(/[^"]*)"', text)]


def _seeded_instruments() -> set[str]:
    """
    The instruments are linked from ROWS, not from literal hrefs.

    `/tools` renders every visible instrument and the header and footer link
    `/tools`, so each one is reachable — but no `href="/tools/pancanga"` exists
    anywhere in the source to prove it. Reading the seed is how that stays
    honest: an instrument with no row would not appear on the hub either, and
    would correctly fail below.
    """
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        for candidate in (base / "alembic" / "versions",
                          base / "backend" / "alembic" / "versions"):
            seed = candidate / "a1c74e9d3b52_tools_become_content.py"
            if seed.is_file():
                slugs = re.findall(r'slug="([a-z0-9-]+)"', seed.read_text(encoding="utf-8"))
                return {f"/tools/{s}" for s in slugs}
    return set()


def _all_links() -> set[str]:
    """Every internal href written in the source, plus the data-driven ones."""
    found: set[str] = set()
    for path in SRC.rglob("*.astro"):
        for href in re.findall(r'href=(?:"|\{`)(/[^"`#?]*)', path.read_text(encoding="utf-8")):
            found.add(href.rstrip("/") or "/")
    # The primary navigation is an array of tuples rather than markup, so no
    # `href="/about"` exists anywhere either. Same reasoning as the
    # instruments: the links are real, they are just not literals.
    header = (SRC / "components" / "chrome" / "SiteHeader.astro").read_text(encoding="utf-8")
    nav = re.search(r"const NAV[^=]*=\s*\[(.*?)\];", header, re.S)
    if nav:
        for path in re.findall(r'\["(/[^"]*)"', nav.group(1)):
            found.add(path.rstrip("/") or "/")

    # Rendered from rows by the hub, which is itself linked from the chrome.
    found |= _seeded_instruments()
    return found


def test_the_sitemap_was_found() -> None:
    assert len(_sitemap_paths()) > 10


@pytest.mark.parametrize("path", _sitemap_paths())
def test_every_promised_page_is_linked_from_somewhere(path: str) -> None:
    """
    Being in the sitemap is a promise that the page exists and matters. If
    nothing on the site links to it, that promise is made only to crawlers.
    """
    clean = path.rstrip("/") or "/"
    if any(clean.startswith(skip) for skip in NOT_BROWSED):
        pytest.skip("reached by token or by a link somebody was sent")
    assert clean in _all_links(), (
        f"{path} is in the sitemap and nothing links to it — it can only be "
        f"reached by typing the address")
