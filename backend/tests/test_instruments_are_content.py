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

# Rows are seeded by migrations — plural, deliberately. This used to name one
# of them and read only that file, which quietly meant a NEW instrument could
# never satisfy the check: you do not edit an applied migration, so its row
# lands in a new one the test was not looking at. It reads all of them now, and
# `seed.py` too, which is where a fresh install gets its rows.
def _versions() -> Path:
    for candidate in (REPO / "alembic" / "versions",
                      REPO / "backend" / "alembic" / "versions"):
        if candidate.is_dir():
            return candidate
    return REPO / "backend" / "alembic" / "versions"


def _seed_files() -> list[Path]:
    out = sorted(_versions().glob("*.py"))
    for candidate in (REPO / "shruti" / "seed.py", REPO / "backend" / "shruti" / "seed.py"):
        if candidate.is_file():
            out.append(candidate)
    return out


SEED_FILES = _seed_files()

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
    """
    Every slug a seeding step creates **as a tool**, and only those.

    Scoping matters both ways. Reading one named migration meant a new
    instrument could never satisfy the check, because you do not edit an
    applied migration and its row lands in a new one. Reading every `slug="…"`
    in every file goes too far the other way and sweeps up projects and link
    groups, which are not tools and have no page on /tools by design.

    So: migrations that touch the `tool` table, and the `TOOLS` list in
    `seed.py` — nothing else in either place.
    """
    found: set[str] = set()
    for path in SEED_FILES:
        text = path.read_text(encoding="utf-8")
        if path.name == "seed.py":
            block = re.search(r"^TOOLS = \[(.*?)^\]", text, re.M | re.S)
            if block:
                found |= set(re.findall(r'\("([a-z0-9-]+)",', block.group(1)))
            continue
        # Touching the tool table has three spellings too: an ORM insert
        # (`Tool(`), a table object (`tool_table`), and plain SQL, which says
        # `INSERT INTO tool` with no quotes at all. Missing the third meant a
        # migration that really did seed a row was invisible here.
        touches_tools = re.search(
            r'"tool"|\btool_table\b|Tool\(|(?i:INTO|UPDATE|FROM)\s+tool\b',
            text,
        )
        if touches_tools:
            # Two spellings, because a migration writes it either way. An
            # ORM insert says `slug="…"`; a plain INSERT binds a parameter and
            # names the value in a constant at the top of the file. Reading
            # only the first form meant a migration that genuinely seeded a row
            # still failed this check, which sends the next person editing the
            # migration to satisfy a regex rather than fixing anything.
            found |= set(re.findall(r'slug="([a-z0-9-]+)"', text))
            found |= set(re.findall(r'^SLUG = "([a-z0-9-]+)"', text, re.M))
    return found


def test_the_files_are_where_we_think() -> None:
    assert TOOL_PAGES.is_dir(), f"no tool pages at {TOOL_PAGES}"
    assert SEED_FILES, "no seeding step found at all"
    assert all(p.is_file() for p in SEED_FILES)
    assert len(_slugs_with_pages()) >= 9


def test_every_instrument_page_has_a_row() -> None:
    missing = _slugs_with_pages() - _seeded_slugs()
    assert not missing, (
        f"tool pages with no row seeded: {sorted(missing)}. Without one the page "
        f"is headed by its own slug and has no description at all."
    )


def _seeded_visible() -> set[str]:
    """
    Only the rows a seeding step makes VISIBLE.

    The two directions of this check are not about the same set, and conflating
    them fails on rows that are deliberately hidden. `seed.py` seeds its tools
    `visible=False` precisely so a row can exist as a statement of intent
    before the page does — the comment in the migration says as much. Those
    need a row-with-no-page allowance; a row that shows a card on /tools does
    not.
    """
    found: set[str] = set()
    for path in SEED_FILES:
        if path.name == "seed.py":
            continue                    # seeded hidden, on purpose
        text = path.read_text(encoding="utf-8")
        if re.search(r'visible=True|"visible": True|visible\s*=\s*True', text):
            found |= set(re.findall(r'slug="([a-z0-9-]+)"', text))
    return found


def test_every_seeded_row_has_a_page() -> None:
    missing = _seeded_visible() - _slugs_with_pages()
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
