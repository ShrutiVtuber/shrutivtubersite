# SPDX-License-Identifier: AGPL-3.0-only
"""
An instrument is a row and a page, and neither half is any use alone.

The `tool` table was in the admin from the beginning and nothing ever read it.
Six rows sat there — hidden, with names that no longer matched the pages, one
instrument that was never built, and four built afterwards and never added —
while the real copy lived as literals inside each .astro file. The admin screen
worked perfectly and changed nothing, which is the most expensive kind of
working: you only find out by editing something and watching the site ignore it.

Now the row is the source. That makes a new failure possible in exchange: a page
with no row renders headed by its own slug, and a row with no page puts a card
on /tools that 404s. Both look fine from the side you built.
"""
from __future__ import annotations

import re
from pathlib import Path


def _repo() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base
    return here.parents[1]


REPO = _repo()
TOOL_PAGES = REPO / "frontend" / "site" / "src" / "pages" / "tools"

MIGRATION = "a1c74e9d3b52_tools_become_content.py"


def _seed_file() -> Path:
    """
    In the test container alembic is mounted at /app/alembic; in a checkout it
    is at backend/alembic. Both, rather than whichever was tried first.
    """
    for candidate in (
        REPO / "alembic" / "versions" / MIGRATION,
        REPO / "backend" / "alembic" / "versions" / MIGRATION,
    ):
        if candidate.is_file():
            return candidate
    return REPO / "backend" / "alembic" / "versions" / MIGRATION


SEED = _seed_file()

# The one dynamic route: one file, two instruments, and the params are not
# derivable from the filename.
DYNAMIC = {"[kind]-stations.astro": {"solar-stations", "lunar-stations"}}


def _slugs_with_pages() -> set[str]:
    out: set[str] = set()
    for path in TOOL_PAGES.glob("*.astro"):
        if path.name == "index.astro":
            continue
        out |= DYNAMIC.get(path.name, {path.stem})
    return out


def _seeded_slugs() -> set[str]:
    text = SEED.read_text(encoding="utf-8")
    return set(re.findall(r'slug="([a-z0-9-]+)"', text))


def test_the_files_are_where_we_think() -> None:
    assert TOOL_PAGES.is_dir(), f"no tool pages at {TOOL_PAGES}"
    assert SEED.is_file(), f"no seed migration at {SEED}"
    assert len(_slugs_with_pages()) >= 9


def test_every_instrument_page_has_a_row() -> None:
    missing = _slugs_with_pages() - _seeded_slugs()
    assert not missing, (
        f"tool pages with no row seeded: {sorted(missing)}. Without one the page "
        f"is headed by its own slug and has no description at all."
    )


def test_every_seeded_row_has_a_page() -> None:
    missing = _seeded_slugs() - _slugs_with_pages()
    assert not missing, (
        f"rows seeded visible with no page behind them: {sorted(missing)}. Each "
        f"puts a card on /tools that leads to a 404."
    )


def test_the_copy_did_not_stay_behind_in_the_pages() -> None:
    """
    The point of the move was that there is now ONE place to edit this. A page
    that still passes its own title or description has quietly restored the
    second place, and the DB copy would be the one that stops being read.
    """
    for path in sorted(TOOL_PAGES.glob("*.astro")):
        if path.name == "index.astro":
            continue
        body = path.read_text(encoding="utf-8")
        block = re.search(r"<ToolLayout(.*?)\n>", body, re.S)
        if not block:
            continue
        for prop in ("title", "native", "description", "glyph", "reckoned"):
            assert not re.search(rf'\n\s+{prop}="', block.group(1)), (
                f"{path.name} passes {prop}= to ToolLayout again — that copy "
                f"belongs to the tool's row now, and two copies will drift."
            )


def test_the_landing_page_and_the_hub_read_the_rows() -> None:
    """
    There were three copies of the instrument list: the tool pages, the landing
    page and (briefly) the hub. Two of them are gone. This is the check that
    notices a fourth being written — a hard-coded array is so much easier to
    add than a fetch that it happens by reflex.
    """
    pages = TOOL_PAGES.parent
    for rel in ("index.astro", "tools/index.astro"):
        body = (pages / rel).read_text(encoding="utf-8")
        assert "instruments()" in body, (
            f"{rel} no longer reads the instrument rows — if it lists the "
            f"instruments from an array in the file, that is the second place "
            f"to edit them again."
        )
