# SPDX-License-Identifier: AGPL-3.0-only
"""
A share link must carry the real host.

Behind Caddy, the Node adapter reports `Astro.url.origin` as "http://localhost"
whatever Host and X-Forwarded-Host say. That is already documented in
astro.config.mjs, in robots.txt.ts and in sitemap.xml.ts, and it had to be
remembered a fifth time when share links were added.

For a canonical tag the failure is invisible until somebody opens the sitemap.
For a **share link** it is worse: the link is handed to another person, and
"http://localhost/chart/s/…" simply does not work for them. Nothing in a build,
a typecheck or a page render catches it, because localhost is a perfectly valid
URL.
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


SRC = _src()


def test_the_frontend_is_actually_mounted():
    """Otherwise every check below passes on a file that was never read."""
    assert (SRC / "lib" / "api.ts").is_file(), (
        f"{SRC} is not readable — the checks below would prove nothing"
    )


def test_there_is_one_place_that_knows_the_site_url():
    api = (SRC / "lib" / "api.ts").read_text()
    assert "export const SITE_URL" in api
    assert "SHRUTI_SITE_URL" in api


def test_the_share_link_is_not_built_from_the_request():
    """
    The one URL on the site that another person has to be able to open.
    """
    page = (SRC / "pages" / "chart" / "[token].astro").read_text()
    share = [ln for ln in page.splitlines() if "shareUrl" in ln and "=" in ln]
    assert share, "no share URL is built on the chart page any more"
    joined = " ".join(share)
    assert "SITE_URL" in joined, "a share link must come from the configured host"
    assert "Astro.url" not in joined, (
        "Astro.url reports localhost behind Caddy, so this link would be "
        "handed to somebody who cannot open it"
    )


@pytest.mark.parametrize("page", ["chart/[token].astro", "chart/s/[token].astro"])
def test_chart_pages_ask_not_to_be_indexed(page: str):
    """
    Every one of these carries somebody's birth data, drawn.
    """
    text = (SRC / "pages" / page).read_text()
    assert re.search(r"\bnoindex\b", text), f"{page} does not send noindex"


def test_robots_does_not_block_the_chart_pages():
    """
    This test used to assert the opposite, and the reversal is the point.

    Blocking `/chart/` in robots.txt looked like the careful choice — those
    pages carry birth data. It is in fact the weaker one. A disallowed URL can
    still be listed in a result from links alone, because the crawler is
    forbidden to FETCH it and so never reads the `noindex` that would have kept
    it out. `noindex` is the mechanism, and it only works on a page a crawler
    is allowed to read; the test above is the one doing the real work.

    It also broke the share loop, which is what made it visible: comparisons are
    posted as `/chart/compare/s/…`, and X, Discord, Facebook and Slack all read
    robots.txt before fetching a link to build its preview. Every shared card
    was a bare grey link.

    Full crawl rules in test_robots_allows_shares.py.
    """
    robots = (SRC / "pages" / "robots.txt.ts").read_text()
    live = robots[robots.index("Sitemap:") - 400:]
    assert "Disallow: /chart/" not in live, (
        "the chart pages are blocked again — every shared comparison will "
        "unfurl without its card"
    )


def test_the_shared_page_does_not_print_the_place_name():
    """
    The place name is the one part of a nativity that cannot be read back out
    of the drawing, so printing it gives away strictly more than the chart does.
    """
    page = (SRC / "pages" / "chart" / "s" / "[token].astro").read_text()
    assert "placeName" not in page, (
        "the shared view must not print the birth place — the API does not "
        "even send it"
    )


# ── structured data, which is the whole point of the journal ────────────────

def test_the_home_page_says_who_this_is():
    """
    Without a Person on the home page, nothing outside the site knows that the
    name, the Twitch channel and the GitHub account are one person — so the
    profiles compete in search results instead of reinforcing each other.
    """
    base = (SRC / "layouts" / "BaseLayout.astro").read_text()
    assert '"@type": "Person"' in base
    assert '"@type": "WebSite"' in base
    assert "sameAs" in base
    assert 'application/ld+json' in base


def test_the_person_block_is_built_after_the_links_it_reads():
    """
    It was written above `socials` and threw "Cannot access 'socials' before
    initialization" — a 500 on the front page, caused by a tag added to help
    search engines find it.
    """
    base = (SRC / "layouts" / "BaseLayout.astro").read_text()
    assert base.index("const socials") < base.index("const homeLd")


def test_the_journal_keeps_the_structured_data_it_is_given():
    """
    BeeRanked writes BlogPosting, BreadcrumbList and Organization, with URLs
    already pointing at shrutivtuber.com. The route read only <main> and threw
    all of it away, so the pages built to be found were the ones telling search
    engines least about themselves.
    """
    parse = (SRC / "lib" / "journal" / "parse.ts").read_text()
    assert 'script[type="application/ld+json"]' in parse
    assert "structuredData" in parse

    page = (SRC / "pages" / "journal" / "[...slug].astro").read_text()
    assert "page.structuredData.map" in page


def test_a_malformed_block_is_dropped_rather_than_emitted():
    """Invalid JSON-LD is worse than none — it can invalidate the whole page."""
    parse = (SRC / "lib" / "journal" / "parse.ts").read_text()
    window = parse[parse.index("structuredData: string[]"):][:700]
    assert "JSON.parse" in window and "catch" in window
