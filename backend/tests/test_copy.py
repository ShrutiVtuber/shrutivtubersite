# SPDX-License-Identifier: AGPL-3.0-only
"""
Editable strings, and the one rule that makes them safe.

Page blocks cover sections. Most of the words on this site are not sections —
they are the line under a form, the label on a button, the sentence explaining
why a field is optional. About six thousand of them lived in templates, on a
site whose whole premise is that she edits it herself.
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
BACKEND = Path(__file__).resolve().parents[1]


def test_the_default_lives_in_the_template_and_always_renders() -> None:
    """
    The rule the whole design rests on. A row only ever OVERRIDES the words the
    page was written with, so an empty table renders a complete site, a page
    nobody has seeded reads exactly as written, and a string she has never
    touched cannot vanish because a query failed.
    """
    lib = (SRC / "lib" / "copy.ts").read_text(encoding="utf-8")
    assert "key in overrides ? overrides[key] : fallback" in lib

    # And the fetch failing must leave the written words standing, not throw.
    assert "catch" in lib
    assert "let overrides" in lib


def test_a_cleared_string_stays_cleared() -> None:
    """
    `in` rather than truthiness. A row set to an empty string is a deliberate
    blank — she deleted the sentence — and falling back to the default there
    would make a line impossible to remove. Deleting the ROW is how you go
    back, and the admin offers exactly that.
    """
    lib = (SRC / "lib" / "copy.ts").read_text(encoding="utf-8")
    assert "key in overrides" in lib
    assert "overrides[key] ||" not in lib, "an empty override falls back"


def test_seeding_never_overwrites_her_words() -> None:
    """
    The seeder reads the templates; the templates are never told what to say.
    It records the label, the default and the position — and for a row that
    already exists it updates only those.
    """
    import inspect

    from shruti.api.routes.admin import seed_copy

    src = inspect.getsource(seed_copy)
    body = src.split("row.label = ")[1]
    assert "row.value" not in body, "seeding writes over a value she has edited"


def test_the_copy_routes_sit_above_the_generic_collection_routes() -> None:
    """
    `/{kind}` matches any single segment, so registered after it "copy" is read
    as a collection name and answered with "unknown collection" — which is
    exactly what happened, and looked like the routes not existing at all.
    """
    admin = (BACKEND / "shruti" / "api" / "routes" / "admin.py").read_text(encoding="utf-8")
    assert admin.index('@router.post("/copy/seed")') < admin.index('@router.get("/{kind}")')
    assert admin.index('@router.get("/copy")') < admin.index('@router.get("/{kind}")')


def test_every_seeded_key_is_unique_per_page() -> None:
    """
    Without the constraint a double seed gives a page two answers for one key,
    and the winner is whichever the query happens to return first.
    """
    mig = next((BACKEND / "alembic" / "versions").glob("*_copy.py"))
    assert "uq_copy_page_key" in mig.read_text(encoding="utf-8")


def test_the_admin_groups_words_by_page() -> None:
    """
    Her words: "page blocks are not usable as they are just all thrown on the
    page blocks page with no way to see to which page they actually belong."
    Both screens group by page now, and both offer a filter.
    """
    for name in ("copy.astro", "blocks.astro"):
        page = (SRC / "pages" / "admin" / name).read_text(encoding="utf-8")
        assert "page-filter" in page, f"{name} has no page filter"
        assert "page-name" in page, f"{name} does not head its groups with the page"


def test_a_retrofitted_page_declares_its_own_page_name() -> None:
    """
    `copy("support")` on /support. A page reading another page's strings would
    silently show the wrong words, and nothing would look broken.
    """
    pages = SRC / "pages"
    for f in pages.rglob("*.astro"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'copy\(\s*["\']([^"\']+)["\']\s*\)', text)
        if not m:
            continue
        declared = m.group(1)
        rel = str(f.relative_to(pages)).removesuffix(".astro")
        if rel.endswith("/index"):
            rel = rel.removesuffix("/index")
        expected = "home" if rel == "index" else rel
        assert declared == expected, (
            f"{f.name} asks for copy(\"{declared}\") but is /{expected}")
