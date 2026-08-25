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


def test_robots_keeps_crawlers_out_of_chart_pages():
    robots = (SRC / "pages" / "robots.txt.ts").read_text()
    assert "Disallow: /chart/" in robots


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
