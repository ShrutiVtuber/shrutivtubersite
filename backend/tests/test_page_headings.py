# SPDX-License-Identifier: AGPL-3.0-only
"""
Every page names itself once, at the top level.

`SectionHeader` renders an `<h2>` unless it is told `as="h1"`. A page whose only
heading is that component therefore has no `<h1>` at all — its outline starts at
level two, under a heading that does not exist.

That is what happened to /shop. It looks completely correct: the title is the
right size, in the right place, in the right font, because the size comes from a
class and not from the tag. What is lost is invisible on the page and only
visible to the two audiences that read structure instead of pixels — a screen
reader building its rotor, and a crawler deciding what the page is about.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


def _pages_dir() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        candidate = base / "frontend" / "site" / "src" / "pages"
        if candidate.is_dir():
            return candidate
    return here.parents[1] / "frontend" / "site" / "src" / "pages"


PAGES = _pages_dir()

# The admin is not indexed and not public; the journal is rendered from a feed
# whose markup is not ours to shape here.
NOT_OURS = ("admin/", "journal/")

# Pages that legitimately carry no heading of their own: they hand off to a
# component that supplies the whole document, or they redirect.
NO_HEADING_OF_ITS_OWN = {
    "index.astro",                 # the landing hero names the site
    "404.astro",
    "500.astro",
}


def _pages() -> list[Path]:
    out = []
    for path in sorted(PAGES.rglob("*.astro")):
        rel = path.relative_to(PAGES).as_posix()
        if rel.startswith(NOT_OURS) or rel in NO_HEADING_OF_ITS_OWN:
            continue
        out.append(path)
    return out


def _strip_comments(text: str) -> str:
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return text


def test_there_are_pages_to_check() -> None:
    """A guard that reads no files passes, which is the way this kind lies."""
    assert len(_pages()) > 20, f"only found {len(_pages())} pages under {PAGES}"


@pytest.mark.parametrize("page", _pages(), ids=lambda p: p.name)
def test_page_has_a_top_level_heading(page: Path) -> None:
    body = _strip_comments(page.read_text(encoding="utf-8"))
    rel = page.relative_to(PAGES).as_posix()

    # A page that renders no document at all — a redirect or a download — has
    # nothing to head. Checked by what it renders, not by a list of filenames,
    # so a new one is exempt for the right reason rather than by being forgotten.
    if "<BaseLayout" not in body and "<ToolLayout" not in body:
        pytest.skip(f"{rel} renders no document")

    has_literal = "<h1" in body
    # A shared header component promoted to the top level.
    has_promoted = re.search(r'as=\{?"h1"\}?', body) is not None
    # Or the page delegates its whole head-and-title to another page component.
    delegates = re.search(r"<(ToolLayout|ClassLayout)\b", body) is not None

    assert has_literal or has_promoted or delegates, (
        f"{rel} renders no <h1>. If its title comes from SectionHeader, pass "
        f'as="h1" — the default is h2 and the page silently loses its outline.'
    )
