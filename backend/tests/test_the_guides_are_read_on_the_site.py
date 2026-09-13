# SPDX-License-Identifier: AGPL-3.0-only
"""
Shruti's Guides are read on the site: the front door, a game's almanac, and
the reader — boards W1, W2 and W3 of the 13 September 2026 handoff.

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
GAME = (SRC / "pages" / "guides" / "[game]" / "index.astro").read_text(encoding="utf-8")
PAGE = (SRC / "pages" / "guides" / "[game]" / "[slug].astro").read_text(encoding="utf-8")
READER = (SRC / "components" / "guides" / "Reader.astro").read_text(encoding="utf-8")
PREVIEW = (SRC / "pages" / "guides" / "write" / "[version]" / "preview.astro").read_text(encoding="utf-8")
LIB = (SRC / "lib" / "guides.ts").read_text(encoding="utf-8")


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
    assert '"guides": ("/guides", "/groups")' in store, "groups are part of the guides section"
    middleware = (SRC / "middleware.ts").read_text(encoding="utf-8")
    assert '"/guides": "guides"' in middleware and '"/groups": "guides"' in middleware
    admin = (SRC / "pages" / "admin" / "settings.astro").read_text(encoding="utf-8")
    assert '["guides", ' in admin


def test_guides_start_hidden_without_overriding_her_choice() -> None:
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
    assert 'reachable("/guides")' in sitemap
    assert "/api/guides?sort=new&limit=500" in sitemap
    assert "add(`/guides/${g.game.slug}/${g.slug}`" in sitemap
    assert "add(`/guides/${g.slug}`" in sitemap             # each game's almanac


# ── the front door (W1) ──────────────────────────────────────────────────────

def test_the_front_door_is_the_boards_front_door() -> None:
    """One sky, three featured by hand, two almanac indices, a by-game grid."""
    body = without_comments(INDEX)
    assert body.count('class="sky gd-hero"') == 1 and body.count("sky-horizon") == 1, "the page has exactly one sky"
    assert ".filter((g) => g.featured).slice(0, 3)" in body
    assert '"/api/guides?sort=top&limit=5"' in body and '"/api/guides?sort=new&limit=5"' in body
    assert 'class="gd-leader"' in body                         # dotted leaders, not cards
    assert "href={`/guides/${g.slug}`}" in body                # the by-game tiles
    assert """say("games.yours", "Your game isn't here")""" in body


def test_the_front_door_is_fetched_as_the_reader() -> None:
    """A blocked author's guides leave your lists — so the lists need the session."""
    body = without_comments(INDEX)
    assert body.count("asReader(Astro, \"/api/guides?") == 3


def test_nothing_on_the_front_door_is_ranked_by_an_algorithm() -> None:
    body = without_comments(INDEX)
    assert "nothing on this page is ranked by an algorithm" in body
    assert "/guides/write" not in body                          # the desk is not advertised here


# ── a game's almanac (W2) ────────────────────────────────────────────────────

def test_a_games_page_is_an_almanac_table() -> None:
    body = without_comments(GAME)
    assert re.search(r"/\^\[a-z0-9-\]\{1,80\}\$/\.test\(slug\)", body)
    assert 'return Astro.rewrite("/404")' in body
    for col in ("col.guide", "col.author", "col.published", "col.patch", "col.path", "col.votes"):
        assert f'say("{col}"' in body
    assert "the patch it was written for is a column, and you decide" in body


# ── the reader (W3) ──────────────────────────────────────────────────────────

def test_the_reader_is_one_component_for_the_page_and_the_preview() -> None:
    """A preview that is a lookalike drifts."""
    assert "<Reader guide={guide} signedIn={!!me} trackHref=" in PAGE
    assert "<Reader guide={guide} signedIn preview />" in PREVIEW
    assert "const actions = !preview;" in READER


def test_the_reader_renders_text_never_html() -> None:
    for body in (without_comments(READER), without_comments(PAGE), without_comments(PREVIEW)):
        assert "set:html" not in body
        assert "renderMarkdown" not in body


def test_a_link_in_a_guide_is_only_drawn_for_http() -> None:
    assert re.search(r"/\^https\?:\\/\\/", LIB), "safeUrl does not pin the scheme"
    body = without_comments(READER)
    assert "href={safeUrl(l.url)}" in body
    assert "href={l.url}" not in body


def test_the_reader_has_no_state_dots() -> None:
    """Nothing has a state until there is a run: a document, not a checklist."""
    body = without_comments(READER)
    assert "state-dot" not in body and "data-state" not in body and 'type="checkbox"' not in body


def test_the_route_parameters_are_slugs_or_nothing() -> None:
    assert re.search(r"/\^\[a-z0-9-\]\{1,80\}\$/\.test\(game\)", PAGE)
    assert re.search(r"/\^\[a-z0-9-\]\{1,160\}\$/\.test\(slug\)", PAGE)
    assert 'return Astro.rewrite("/404")' in PAGE


def test_a_hidden_or_unpublished_guide_is_not_indexed() -> None:
    assert "noindex={guide.hidden || !guide.publishedAt}" in PAGE
    assert "guide.publishedAt && !guide.hidden" in PAGE       # and asserts no HowTo


def test_the_reader_is_fetched_as_the_reader() -> None:
    assert "asReader(Astro, `/api/guides/${game}/${slug}`)" in PAGE
    assert "asReader(Astro, `/api/guides/mine/by-id/${id}`)" in PREVIEW


def test_the_gates_are_worded_from_the_components_copy() -> None:
    """⚠ No English in lib/guides.ts; the reader's "opens at level 15" is editable."""
    lib = without_comments(LIB)
    assert not re.search(r"[\"'`][^\"'`]*\b(or later|at most|or more|only)\b[^\"'`]*[\"'`]", lib)
    assert 'say("gate.min", "at {what} {n}")' in READER
    assert "gateWords(g, lowered, words)" in READER


def test_the_actions_follow_the_practice_room() -> None:
    body = without_comments(READER)
    assert "/api/guides/by-id/${vote.dataset.vote}/vote" in body
    assert "/api/guides/by-id/${report.dataset.report}/report" in body
    assert "/api/guides/by-id/${withdraw.dataset.withdraw}/withdraw" in body
    assert '"/api/practice/blocks"' in body                    # a block is a block
    assert body.count("it has gone to Shruti") == 1            # the same words, first or fourth


def test_tracking_is_offered_only_where_it_exists() -> None:
    """A published, visible guide can be tracked; a draft or a hidden one says nothing about it."""
    assert "trackHref={guide.publishedAt && !guide.hidden ? `/guides/${game}/${slug}/track` : \"\"}" in PAGE
    body = without_comments(READER)
    assert "{actions && trackHref && (" in body               # the rail block and the end card
    assert body.count("trackHref && (") == 2
    assert "/download" in body


def test_the_licence_is_stated_or_said_to_be_missing() -> None:
    """Never guessed: a guide with no licence says "not stated"."""
    body = without_comments(READER)
    assert 'say("licence.unsaid", "not stated")' in body
    assert "CC-BY-SA-4.0" in body
