# SPDX-License-Identifier: AGPL-3.0-only
"""
The journal's feed.

A feed is how somebody follows a person without an algorithm deciding whether
they see them. The failure modes are all quiet: a feed that is invalid XML, or
that dates its items in a format strict readers drop, simply shows nothing and
looks like an empty journal.
"""
from __future__ import annotations

from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


FEED = _src() / "pages" / "journal" / "rss.xml.ts"


def test_the_feed_exists_and_is_readable():
    assert FEED.is_file(), f"{FEED} is unreadable — the checks below prove nothing"


def test_dates_are_rfc_822_not_iso():
    """
    RSS wants RFC 822. An ISO date is accepted by tolerant readers and silently
    dropped by strict ones, which is the worst of both.
    """
    text = FEED.read_text()
    assert "toUTCString" in text
    assert "rfc822" in text


def test_the_guid_is_the_link():
    """A guid that changed when a title was edited shows every subscriber the
    same entry twice."""
    text = FEED.read_text()
    assert 'isPermaLink="true"' in text


def test_urls_are_absolute_and_not_built_from_the_request():
    """
    Behind Caddy, Astro reports localhost. A feed full of localhost links is
    invisible until somebody subscribes and every item 404s.
    """
    text = FEED.read_text()
    assert "SITE_URL" in text
    assert "Astro.url" not in text


def test_everything_written_into_the_xml_is_escaped():
    """An ampersand in a title is an unparseable feed."""
    text = FEED.read_text()
    assert "const escape" in text
    for field in ("e.title", "link", "e.dek"):
        assert f"escape({field})" in text, f"{field} goes in unescaped"


def test_the_feed_is_discoverable():
    """A feed nobody can find is a feed nobody reads."""
    base = (_src() / "layouts" / "BaseLayout.astro").read_text()
    assert 'type="application/rss+xml"' in base
    assert "/journal/rss.xml" in base


def test_it_is_served_as_a_feed_not_as_html():
    text = FEED.read_text()
    assert "application/rss+xml" in text
