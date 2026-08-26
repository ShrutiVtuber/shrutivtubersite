# SPDX-License-Identifier: AGPL-3.0-only
"""
Finishing a section in private.

Each of shop, horoscopes and classes can be built out — products priced, twelve
horoscopes drafted, a course recorded — while the public gets a 404 and the
admin is untouched.

Three things here are quiet when broken, which is why each has a test rather
than a comment:

  - **A hidden section must return 404, not 200.** A rewrite keeps the status
    of the request it came from, so /404 rendered through one comes back 200 —
    a page that says "not found" with a success code is a lie told to a crawler
    as much as to a person, and it is how nonexistent pages get indexed.
  - **Nothing may link to a hidden section.** A nav item pointing at a 404 says
    the site is broken rather than that the thing is not ready.
  - **Hiding classes must not take away something somebody bought.**
"""
from __future__ import annotations

import inspect
from pathlib import Path

from shruti.api.routes import admin, content
from shruti.core import settings_store


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()


def test_the_frontend_is_mounted():
    assert (SRC / "middleware.ts").is_file(), (
        f"{SRC} is unreadable — every check below would pass on nothing"
    )


# ── the default is published ────────────────────────────────────────────────

def test_a_missing_setting_means_published():
    """
    A section that vanished because a settings row was missing would be the
    worst kind of surprise — and the failure would look like a bug in the page
    rather than in a default.
    """
    source = inspect.getsource(settings_store.sections_live)
    assert '"1"' in source, "the fallback should be the published state"
    assert 'get(key, "1") != "0"' in source


def test_all_three_sections_are_toggleable():
    assert set(settings_store.SECTIONS) == {"shop", "horoscopes", "classes"}


# ── the gate ────────────────────────────────────────────────────────────────

def test_a_hidden_section_answers_404_not_200():
    """
    `context.rewrite` keeps the incoming status. Without setting it explicitly
    the visitor gets a 200 whose body says "not found".
    """
    mw = (SRC / "middleware.ts").read_text()
    assert 'rewrite("/404")' in mw
    window = mw[mw.index('rewrite("/404")'):][:400]
    assert "status: 404" in window, (
        "the rewrite does not force a 404 status, so the page returns 200"
    )


def test_she_still_sees_a_hidden_section():
    """The whole point: build it in private, not blind."""
    mw = (SRC / "middleware.ts").read_text()
    # Wide enough to reach past the comment explaining the 404 status.
    gate = mw[mw.index("const section = sectionOf(path)"):][:1200]
    assert "isOperator(token)" in gate
    assert "previewingSection" in gate


def test_the_gate_covers_pages_beneath_the_section_too():
    """/shop/a-thing must not be reachable when /shop is not."""
    mw = (SRC / "middleware.ts").read_text()
    assert 'path.startsWith(prefix + "/")' in mw


# ── nothing links to a 404 ──────────────────────────────────────────────────

def test_the_header_and_footer_drop_hidden_sections():
    for name in ("chrome/SiteHeader.astro", "chrome/SiteFooter.astro"):
        text = (SRC / "components" / name).read_text()
        assert "sectionsLive" in text, f"{name} does not know what is hidden"
        assert "filter(" in text, f"{name} does not filter its links"


def test_the_nav_reads_what_the_gate_decided():
    """
    Two sources for one answer is how a nav ends up pointing at a 404. The
    middleware publishes its decision; the chrome reads it.
    """
    mw = (SRC / "middleware.ts").read_text()
    assert "context.locals.sectionsLive = state.sections" in mw


def test_the_home_page_drops_the_whole_horoscopes_block():
    """
    Not just its links. A heading promising twelve readings with no way to
    reach one reads as broken rather than as not-yet.
    """
    home = (SRC / "pages" / "index.astro").read_text()
    assert "sectionsLive.horoscopes !== false" in home


def test_the_sitemap_leaves_hidden_sections_out():
    """Listing a URL that 404s teaches a crawler to distrust the sitemap."""
    sm = (SRC / "pages" / "sitemap.xml.ts").read_text()
    assert "hiddenSections" in sm
    assert "SITE_API" in sm.split("\n")[0:40][-1] or "import { site, SITE_API }" in sm, (
        "SITE_API is used by the filter and must be imported — unimported, the "
        "fetch throws, the catch swallows it, and the filter silently does nothing"
    )


# ── the one that costs somebody something ───────────────────────────────────

def test_classes_cannot_be_hidden_while_anybody_holds_one():
    """
    Hiding the shop costs a visitor a browse page. Hiding classes would 404 the
    page a student watches on, and they paid for it. A section being "not
    ready" is a fact about the site, not about their purchase.
    """
    source = inspect.getsource(admin.write_settings)
    assert "Entitlement" in source
    assert "409" in source
    assert "revoked_at.is_(None)" in source, (
        "a revoked entitlement should not block hiding — only a live one"
    )


def test_the_state_travels_with_the_holding_page_answer():
    """One request per page load, not two."""
    source = inspect.getsource(content.site_state)
    assert "sections_live" in source
    assert "comingSoon" in source
