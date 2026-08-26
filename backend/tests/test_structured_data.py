# SPDX-License-Identifier: AGPL-3.0-only
"""
What each kind of page tells a crawler about itself.

Read from the source rather than from a rendered page, because every one of
these is conditional on the page having something to describe — an empty shop
correctly emits nothing, so a test against a running site with no data would
pass while the markup was missing entirely.

The rule these all follow: **markup describes the page, and only when the page
has contents.** An ItemList on an empty listing claims a set that is not there,
which is worse than saying nothing.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()
PAGES = SRC / "pages"


def _types(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r'"@type":\s*"([A-Za-z]+)"', text))


def test_the_shop_describes_itself_as_a_set() -> None:
    """
    Product pages already carry an offer each. Without a listing, a crawler
    sees nine unrelated pages rather than a shop.
    """
    assert "ItemList" in _types(PAGES / "shop" / "index.astro")
    assert "Product" in _types(PAGES / "shop" / "[slug].astro")


def test_classes_describe_themselves_as_a_set() -> None:
    assert "ItemList" in _types(PAGES / "classes" / "index.astro")
    assert {"Course", "Offer"} <= _types(PAGES / "classes" / "[slug].astro")


def test_the_journal_index_says_it_is_a_blog() -> None:
    """
    The gap the SEO audit flagged and could not confirm: the engine marks up an
    ARTICLE as a BlogPosting, but a section index got nothing at all — a
    crawler saw a list of links with no statement of what they were.
    """
    types = _types(PAGES / "journal" / "[...slug].astro")
    assert "Blog" in types
    assert "BlogPosting" in types


def test_the_schedule_publishes_events() -> None:
    assert {"Event", "VirtualLocation"} <= _types(PAGES / "schedule.astro")


def test_no_listing_claims_contents_it_does_not_have() -> None:
    """
    Every listing's markup is guarded on being non-empty. An ItemList of zero
    items is a lie about the page in a machine-readable format.
    """
    for page, guard in (
        (PAGES / "shop" / "index.astro", "products.length === 0"),
        (PAGES / "classes" / "index.astro", "courses.length === 0"),
        (PAGES / "journal" / "[...slug].astro", "listed.length === 0"),
    ):
        assert guard in page.read_text(encoding="utf-8"), (
            f"{page.name} builds its markup without checking there is anything "
            f"to describe")


def test_an_instrument_page_carries_its_questions() -> None:
    """
    FAQPage is only honest where real questions and answers exist, and they do:
    the instrument rows carry `faq_md`, which is where the answers live and
    where she edits them.
    """
    layout = (SRC / "layouts" / "ToolLayout.astro").read_text(encoding="utf-8")
    assert "FAQPage" in layout
    assert "BreadcrumbList" in layout
