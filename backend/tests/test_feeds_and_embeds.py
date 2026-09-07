# SPDX-License-Identifier: AGPL-3.0-only
"""
The machine-readable surfaces of the horoscopes: feeds, oEmbed, canonical URLs.

Every check here guards a bug that was actually made while writing them.

The first is the sharpest. `/api/horoscopes/archive` groups readings by the
period they cover and carries NO timestamp, because it exists to answer "what
months are there" for a human browsing. Both the per-sign feed and the sitemap
were written against it, and both would have shipped: the feed would have
rendered items with an empty <pubDate>, and the sitemap a <lastmod> read off a
field that is not in the response. Neither is a crash and neither shows up in a
typecheck — a feed reader simply treats undated items as arriving now, forever.
`/api/horoscopes/published` is the flat one with `publishedAt`, and these two
callers must use it.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        candidate = base / "frontend" / "site" / "src"
        if candidate.is_dir():
            return candidate
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()


def code_of(path: Path) -> str:
    """
    Source with comments and strings-in-comments removed.

    Written the fifth time a check like this passed or failed on its own
    explanatory prose rather than on the code: this very file talks about
    `/archive` at length, and a naive `"archive" in text` would match the
    paragraph above instead of a fetch.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"(?m)//.*$", " ", text)
    return text


def test_the_frontend_is_actually_mounted():
    """Otherwise every check below passes on a file that was never read."""
    assert (SRC / "lib" / "api.ts").is_file(), (
        f"{SRC} is not readable — the checks below would prove nothing"
    )


# ── feeds ────────────────────────────────────────────────────────────────────

FEED = SRC / "pages" / "horoscopes" / "[sign]" / "feed.xml.ts"
SITEMAP = SRC / "pages" / "sitemap.xml.ts"


def test_there_is_a_feed_per_sign():
    assert FEED.is_file(), "a Leo reader should be able to subscribe to Leo"


def test_the_feed_reads_the_endpoint_that_has_timestamps():
    code = code_of(FEED)
    assert "/api/horoscopes/published" in code, (
        "the feed must read /published — /archive has no publishedAt, so every "
        "<pubDate> would be empty"
    )
    assert "/api/horoscopes/archive" not in code


def test_the_sitemap_reads_the_endpoint_that_has_timestamps():
    code = code_of(SITEMAP)
    assert "/api/horoscopes/published" in code, (
        "<lastmod> must come from /published; /archive carries no timestamp"
    )


def test_the_feed_links_the_dated_form():
    """
    A feed entry that moves is an entry read twice.

    Pointing at /horoscopes/leo/monthly would give every subscriber the same
    URL every month, with different words behind it each time.
    """
    code = code_of(FEED)
    assert "${r.period}/${r.covers}" in code, (
        "feed items must link the dated, canonical URL"
    )


def test_the_sitemap_lists_dated_readings():
    code = code_of(SITEMAP)
    assert "${r.sign}/${r.period}/${r.covers}" in code


# ── oEmbed ───────────────────────────────────────────────────────────────────

OEMBED = SRC / "pages" / "oembed.json.ts"


def test_there_is_an_oembed_endpoint():
    assert OEMBED.is_file()


def test_oembed_refuses_urls_that_are_not_ours():
    """
    The whole risk of an oEmbed endpoint.

    It answers with HTML that another site pastes into its own page under our
    provider name. One that echoes back whatever URL it is handed is a way to
    place an iframe of an attacker's choosing into somebody else's article and
    have it attributed to this domain.
    """
    code = code_of(OEMBED)
    assert ".origin !==" in code or ".origin !=" in code, (
        "oEmbed must compare the asked-for URL's origin against this site's"
    )
    assert "SITE_URL" in code


def test_oembed_only_answers_for_paths_that_have_an_embed():
    code = code_of(OEMBED)
    assert "/tools/events" in code
    assert "daily|weekly|monthly|yearly" in code, (
        "the reading path must be matched by shape, not merely by prefix"
    )


def test_oembed_draws_the_period_being_shared_not_today():
    """
    Sharing last month's reading must not show this month's sky.

    The card sits directly above the words, and a wheel of a different date is
    a picture contradicting the text it illustrates.
    """
    code = code_of(OEMBED)
    assert "instantFor(" in code
    assert "864e5" in code, "the ISO-week arithmetic should be here"


# ── canonical URLs and soft 404s ─────────────────────────────────────────────

COVERS = SRC / "pages" / "horoscopes" / "[sign]" / "[period]" / "[covers].astro"
UNDATED = SRC / "pages" / "horoscopes" / "[sign]" / "[period].astro"
READING = SRC / "components" / "horoscope" / "Reading.astro"


def test_the_dated_route_exists():
    assert COVERS.is_file(), "the canonical form is /<sign>/<period>/<covers>"


def test_the_dated_route_validates_the_id_shape():
    """
    Unchecked, every string renders a page saying "not written yet".

    That is a soft 404: indexable, infinite, and indistinguishable to a crawler
    from a real reading that simply has not been written.
    """
    code = code_of(COVERS)
    assert "SHAPE" in code and "rewrite" in code
    for period in ("daily", "weekly", "monthly", "yearly"):
        assert period in code, f"{period} needs an id shape"


def test_both_routes_point_at_the_dated_form():
    code = code_of(READING)
    assert "canonical=" in code, (
        "the undated route renders this too, and must name the dated URL as "
        "canonical or the two compete in an index"
    )


def test_an_unwritten_reading_is_not_indexed():
    code = code_of(READING)
    assert "noindex={!data.published}" in code, (
        "twelve signs x four periods x any valid date is an unbounded number "
        "of 'not written yet' pages; none of them should be indexed"
    )


def test_the_reading_describes_itself_with_its_own_words():
    """
    A description repeated on forty-eight pages is forty-eight near-duplicates.
    """
    code = code_of(READING)
    assert "const summary" in code
    assert "description={summary}" in code
