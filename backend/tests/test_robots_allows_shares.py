# SPDX-License-Identifier: AGPL-3.0-only
"""
The share loop must survive robots.txt.

A comparison is shared as a link to `/chart/compare/s/<token>`, whose preview
image is `/api/charts/compare/s/<token>/card.png`. Twitter/X, Discord, Facebook
and Slack all read robots.txt before fetching a link to build its card.

`Disallow: /chart/` and `Disallow: /api/` used to cover both. The result was a
feature built to be shared that could not show its card on any platform worth
sharing it on — and the failure is completely silent. The page returns 200, the
card renders, the tags are right, and every test passes. It only shows up as a
grey link on somebody else's timeline.

This checks the rules as an actual crawler resolves them: RFC 9309 says the
most specific (longest) matching rule wins, and Allow wins a tie.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        candidate = base / "frontend" / "site" / "src"
        if candidate.is_dir():
            return candidate
    return here.parents[1] / "frontend" / "site" / "src"


ROBOTS = _src() / "pages" / "robots.txt.ts"


def _live_rules() -> list[tuple[str, str]]:
    """
    The rules served once the holding page is down.

    The file holds two bodies — the `Disallow: /` used while the site is behind
    the gate, and the real one. Only the real one is the subject here, and it is
    the block that names a Sitemap.
    """
    text = ROBOTS.read_text(encoding="utf-8")
    bodies = re.findall(r"`(User-agent:.*?)`", text, re.S)
    live = [b for b in bodies if "Sitemap:" in b]
    assert len(live) == 1, f"expected one live robots body, found {len(live)}"

    rules: list[tuple[str, str]] = []
    for line in live[0].splitlines():
        m = re.match(r"\s*(Allow|Disallow)\s*:\s*(\S*)\s*$", line, re.I)
        if m:
            rules.append((m.group(1).lower(), m.group(2)))
    assert rules, "no Allow/Disallow rules parsed"
    return rules


def _allowed(path: str) -> bool:
    """RFC 9309 resolution: longest matching rule wins, Allow breaks a tie."""
    best_len, best_verdict = -1, True          # no rule matches -> allowed
    for verb, pattern in _live_rules():
        if not path.startswith(pattern):
            continue
        if len(pattern) > best_len or (len(pattern) == best_len and verb == "allow"):
            best_len, best_verdict = len(pattern), verb == "allow"
    return best_verdict


# The two URLs the whole compatibility feature is delivered through, plus the
# plain chart share. If a crawler may not fetch these, the feature is invisible
# wherever it is posted.
@pytest.mark.parametrize("path", [
    "/chart/compare/s/abc123",
    "/api/charts/compare/s/abc123/card.png",
    "/chart/invite/abc123",
    "/api/charts/invite/abc123/card.png",
    "/chart/s/abc123",
])
def test_shared_paths_are_crawlable(path: str) -> None:
    assert _allowed(path), (
        f"{path} is blocked by robots.txt — a link to it will unfurl on X, "
        f"Discord and Slack as a bare URL with no image."
    )


# Still shut. These are not secrets — they are guarded server-side — but a
# crawler wandering into them produces sign-in pages in search results.
@pytest.mark.parametrize("path", [
    "/admin", "/admin/insight", "/account", "/signin", "/signup",
    "/api/content/site-state",
])
def test_private_paths_stay_blocked(path: str) -> None:
    assert not _allowed(path), f"{path} should not be crawlable"


def test_public_pages_are_crawlable() -> None:
    for path in ("/", "/today", "/tools/natal-chart", "/compatible", "/journal/"):
        assert _allowed(path), f"{path} must be crawlable"


def test_private_chart_pages_still_say_noindex() -> None:
    """
    robots.txt no longer hides these, so `noindex` is the only thing keeping
    somebody's birth data out of a search index. It is also the only mechanism
    that actually works, since a crawler must be allowed to read a page before
    it can read the tag telling it to forget the page.
    """
    pages = _src() / "pages" / "chart"
    private = [
        pages / "[token].astro",
        pages / "s" / "[token].astro",
        pages / "print" / "[token].astro",
        pages / "compare" / "[token].astro",
    ]
    for page in private:
        assert page.is_file(), f"missing {page}"
        body = page.read_text(encoding="utf-8")
        # Strip comments first: several of these files discuss noindex in prose.
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        body = re.sub(r"\{/\*.*?\*/\}", "", body, flags=re.S)
        assert "noindex" in body, f"{page.name} no longer sends noindex"
