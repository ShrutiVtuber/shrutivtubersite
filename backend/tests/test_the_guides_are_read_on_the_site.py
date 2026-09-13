# SPDX-License-Identifier: AGPL-3.0-only
"""
Shruti's Guides are read on the site: the catalogue and the reader.

Source-level guards, as everywhere in this suite. The routes have their own
file (test_a_guide_is_a_path.py); these hold the pages, the section gate that
keeps /guides dark until she turns it on, and the places a new section has to
be declared — which are four, in three languages, and drift by nature.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "site" / "src"
INDEX = (SRC / "pages" / "guides" / "index.astro").read_text(encoding="utf-8")
READER = (SRC / "pages" / "guides" / "[game]" / "[slug].astro").read_text(encoding="utf-8")
LIB = (SRC / "lib" / "guides.ts").read_text(encoding="utf-8")
CARD = (SRC / "components" / "cards" / "GuideCard.astro").read_text(encoding="utf-8")


def without_comments(text: str) -> str:
    """The trap this suite knows well: a guard matching its own explanation."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


# ── the section gate ─────────────────────────────────────────────────────────

def test_the_section_is_declared_everywhere_a_section_must_be() -> None:
    """
    ⚠ Four registries, three languages. Missing the backend one means the
    admin cannot hide it; missing the middleware means hiding it does nothing;
    missing the admin list means she has no switch; and the header reads the
    backend's answer by name.
    """
    store = (ROOT / "backend" / "shruti" / "core" / "settings_store.py").read_text(encoding="utf-8")
    assert '"guides": "page.guides"' in store
    assert '"guides": ("/guides",)' in store
    middleware = (SRC / "middleware.ts").read_text(encoding="utf-8")
    assert '"/guides": "guides"' in middleware
    admin = (SRC / "pages" / "admin" / "settings.astro").read_text(encoding="utf-8")
    assert '["guides", ' in admin


def test_guides_start_hidden_without_overriding_her_choice() -> None:
    """
    Absent means live is the rule, and it is the wrong default for a section
    that is new — so a migration writes the hiding row once, and only once.
    """
    migration = next((ROOT / "backend" / "alembic" / "versions").glob("*_guides_start_hidden.py"))
    body = migration.read_text(encoding="utf-8")
    assert "'page.guides', '0'" in body
    assert "ON CONFLICT (key) DO NOTHING" in body
    assert 'down_revision = "c4e9b3a7d216"' in body


def test_the_nav_and_the_sitemap_carry_the_catalogue() -> None:
    header = (SRC / "components" / "chrome" / "SiteHeader.astro").read_text(encoding="utf-8")
    footer = (SRC / "components" / "chrome" / "SiteFooter.astro").read_text(encoding="utf-8")
    sitemap = (SRC / "pages" / "sitemap.xml.ts").read_text(encoding="utf-8")
    assert '["/guides", "Guides"]' in header
    assert '["/guides", "Guides"]' in footer
    assert '["/guides", "0.8", "weekly"]' in sitemap
    # Every published guide, and only when the section is reachable.
    assert 'reachable("/guides")' in sitemap
    assert "/api/guides?sort=new&limit=500" in sitemap
    assert "add(`/guides/${g.game.slug}/${g.slug}`" in sitemap


# ── the reader ───────────────────────────────────────────────────────────────

def test_the_reader_renders_text_never_html() -> None:
    """A guide is other people's writing. Text nodes, no markdown, no set:html."""
    body = without_comments(READER)
    assert "set:html" not in body
    assert "renderMarkdown" not in body


def test_a_link_in_a_guide_is_only_drawn_for_http() -> None:
    assert re.search(r"/\^https\?:\\/\\/", LIB), "safeUrl does not pin the scheme"
    body = without_comments(READER)
    # Every anchor whose href comes from the document goes through safeUrl.
    assert "href={safeUrl(l.url)}" in body
    assert "href={l.url}" not in body


def test_the_route_parameters_are_slugs_or_nothing() -> None:
    assert re.search(r"/\^\[a-z0-9-\]\{1,80\}\$/\.test\(game\)", READER)
    assert re.search(r"/\^\[a-z0-9-\]\{1,160\}\$/\.test\(slug\)", READER)
    assert 'return Astro.rewrite("/404")' in READER
    assert re.search(r"/\^\[a-z0-9-\]\{1,80\}\$/\.test\(wantedGame\)", INDEX)


def test_a_hidden_or_unpublished_guide_is_not_indexed() -> None:
    assert "noindex={guide.hidden || !guide.publishedAt}" in READER
    # And asserts nothing to a search engine either.
    assert "guide.publishedAt && !guide.hidden" in READER


def test_the_reader_is_fetched_as_the_reader() -> None:
    """
    Hidden is 404 except for the author, and `mine`/`voted` need the session —
    so the page forwards it rather than asking anonymously.
    """
    assert "asReader(Astro, `/api/guides/${game}/${slug}`)" in READER
    assert "asReader(Astro, `/api/guides?${query.toString()}`)" in INDEX


def test_the_gates_are_worded_from_the_pages_copy() -> None:
    """
    ⚠ No English in lib/guides.ts. The vocabulary comes from the page's own
    say(), so "or later" is editable like every other sentence a reader sees.
    """
    lib = without_comments(LIB)
    assert not re.search(r"[\"'`][^\"'`]*\b(or later|at most|or more|only)\b[^\"'`]*[\"'`]", lib), \
        "gate wording is hard-coded in the library"
    assert 'say("gate.at_least", ' in READER
    assert "gateWords(g, doc, words)" in READER


def test_the_actions_follow_the_practice_room() -> None:
    body = without_comments(READER)
    assert "/api/guides/by-id/${vote.dataset.vote}/vote" in body
    assert "/api/guides/by-id/${report.dataset.report}/report" in body
    assert "/api/guides/by-id/${withdraw.dataset.withdraw}/withdraw" in body
    # A block is a block whatever they were reading: the room's endpoint.
    assert '"/api/practice/blocks"' in body
    # The same words for the first report and the fourth.
    assert body.count("it has gone to Shruti") == 1


def test_the_reader_does_not_promise_tracking() -> None:
    """
    Nothing on the page claims progress can be kept until it can. The download
    link is the honest version of that promise — the file the tracker reads.
    """
    body = without_comments(READER)
    assert "/download" in body
    assert "data-track" not in body and "Track this" not in body


def test_the_catalogue_does_not_link_to_the_desk_yet() -> None:
    """A link to a page that is not there is the worst kind of promise."""
    body = without_comments(INDEX)
    assert "/guides/write" not in body


def test_the_featured_band_only_on_the_default_view() -> None:
    assert 'sort === "featured" && !gameSlug ? all.filter((g) => g.featured) : []' in INDEX


def test_the_card_takes_its_words_from_the_page() -> None:
    """
    Drawn many times; the page's copy() is where the words are edited.

    ⚠ Comments stripped first: the card's own doc comment says "copy()" while
    explaining why it does not call it, and this guard matched that sentence
    the first time it ran.
    """
    card = without_comments(CARD)
    assert "copy(" not in card
    assert "words: {" in card
