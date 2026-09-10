# SPDX-License-Identifier: AGPL-3.0-only
"""
Every token-addressed page tells crawlers not to index it.

⚠ **`noindex` and robots.txt are a PAIR here, and the pairing is deliberate.**
`robots.txt` leaves `/chart/` crawlable on purpose — it says so at length — so
that a shared comparison unfurls a preview card on Discord and X. That choice
only works if each of those pages carries `noindex` itself: blocking the prefix
instead would stop the crawler fetching the page, so it could never read a
noindex, and the card would never build.

Which means the two halves have to stay in step, and nothing except this test
notices when they do not. A page added under a token-addressed prefix without
`noindex` is publicly crawlable and publicly indexable, and it draws somebody's
birth data. There is no error, no log line, and no way to tell from the page
itself — the first sign is the search result.

Found by a launch sweep: `/chart/compare/s/[token]` and `/chart/invite/[token]`
were both missing it, and the first of those is the share link robots.txt names
by path as the reason the prefix is open.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import SITE

PAGES = SITE / "src" / "pages"

#: Prefixes whose pages are addressed by an unguessable token rather than by a
#: name. Anything under one of these is somebody's private data.
PRIVATE = ("chart", "overlay")


def _token_pages() -> list[Path]:
    found = [
        p
        for prefix in PRIVATE
        for p in (PAGES / prefix).rglob("*.astro")
        if "[token]" in p.name
    ]
    assert found, "no token-addressed pages found — has the layout moved?"
    return sorted(found)


#: Comments, in each of the three flavours an .astro file can carry: a block
#: comment in the frontmatter, a JSX-style one in the markup, and an HTML one.
_COMMENTS = re.compile(r"\{/\*.*?\*/\}|/\*.*?\*/|<!--.*?-->", re.S)


def _without_comments(source: str) -> str:
    """
    The page with its prose removed.

    ⚠ Not decoration. The first draft of this test looked for "noindex"
    anywhere in the file, and the paragraph above each fix EXPLAINS noindex —
    so deleting the attribute left the word behind twice over and the test went
    on passing. A guard that reads its own documentation is worse than no
    guard, because it is green.
    """
    return _COMMENTS.sub(" ", source)


@pytest.mark.parametrize("page", _token_pages(), ids=lambda p: p.stem and str(p))
def test_a_token_page_is_not_indexable(page: Path) -> None:
    source = _without_comments(page.read_text(encoding="utf-8"))
    assert "noindex" in source, (
        f"{page.relative_to(SITE)} is addressed by a token and carries somebody's "
        "birth data, but sends no noindex. robots.txt deliberately leaves this "
        "prefix crawlable so share links unfurl, so noindex is the only thing "
        "keeping the page out of a search index."
    )


def test_robots_still_leaves_the_chart_prefix_open() -> None:
    """
    The other half of the pair.

    If somebody ever adds `Disallow: /chart` the test above stops meaning
    anything — and the share cards break at the same time, quietly.
    """
    robots = _without_comments((PAGES / "robots.txt.ts").read_text(encoding="utf-8"))
    body = robots[robots.index("Allow: /") :]
    assert "Disallow: /chart" not in body, (
        "robots.txt now blocks /chart. That breaks link previews on every "
        "platform the share feature exists for, and it stops crawlers reading "
        "the noindex that actually keeps these pages out of search."
    )
