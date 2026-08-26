# SPDX-License-Identifier: AGPL-3.0-only
"""
Every page sits in the same wrapper.

`.page` is what gives a page its maximum width and its padding. Writing
`class="container"` instead — a name that sounds right and does not exist —
produces a page whose content runs flush to the left edge with the eyebrow
glyph clipped off, and it looks fine in a build, in a typecheck, and in every
test that is not this one.

That happened to /shop and /classes, and it reached production. This is the
check that would have caught it.
"""
from __future__ import annotations

import re
from pathlib import Path

def _pages_dir() -> Path:
    """
    Where the site's pages are, in the container and out of it.

    Mounted at /app/frontend by scripts/test.sh; two levels up from here when
    the suite is run straight from a checkout.
    """
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        candidate = base / "frontend" / "site" / "src" / "pages"
        if candidate.is_dir():
            return candidate
    return here.parents[1] / "frontend" / "site" / "src" / "pages"


PAGES = _pages_dir()

# Pages that lay themselves out and mean to: the reader carries an outline
# beside the lesson and is deliberately wider than a column of prose.
LAYS_ITSELF_OUT = {
    "classes/[slug]/[lesson].astro",
    # The compatibility page opens on a full-bleed sky panel that has to reach
    # both edges of the window, so it cannot sit inside a fixed-width wrapper.
    # It supplies its own `.cx-in` column at the same `--page-max` for every
    # section below the panel — it is laid out, not unwrapped.
    "compatible.astro",
}

# Sections with their own established idiom, which is not this one.
NOT_OURS = (
    "journal/", "admin/", "tools/",
    # Overlays are not pages for readers. They are her own OBS surfaces, seen
    # by nobody but her while she sets them up, and their idle state is
    # deliberately an instruction TO HER — "Overlay connected · pick a counter
    # in the admin" — because the alternative on a live stream is a blank
    # rectangle nobody can interpret.
    "overlay/",
)


def _pages() -> list[Path]:
    return [
        p for p in PAGES.rglob("*.astro")
        if not p.name.startswith("_")
        and not any(part in str(p.relative_to(PAGES)).replace("\\", "/") for part in NOT_OURS)
    ]


def test_the_pages_are_actually_being_read():
    """
    The check on the check.

    This test suite runs in a container with only the backend mounted, so an
    earlier version of these tests found no files and passed on an empty list
    — green, and looking at nothing. That is worse than a failure, because a
    failure gets fixed.
    """
    found = _pages()
    assert PAGES.is_dir(), f"the site's pages are not where this expects: {PAGES}"
    assert len(found) > 5, f"only found {len(found)} pages; something is not mounted"


def test_no_page_uses_a_wrapper_class_that_does_not_exist():
    """
    `container` is the one that sounds right. There are others.

    Anything a page wraps itself in has to be a class the stylesheets actually
    define, or it is decoration on an element doing nothing.
    """
    invented = ("container", "wrapper", "inner", "content-wrap")
    offenders: list[str] = []

    for page in _pages():
        text = page.read_text(encoding="utf8")
        body = text.split("---", 2)[-1]
        # Only what the page declares itself; a class it also styles locally
        # is its own business.
        styled = set(re.findall(r"\.([a-z][a-z0-9-]*)\s*\{", text))
        for name in invented:
            if re.search(rf'class="{name}(?:[ "])', body) and name not in styled:
                offenders.append(f"{page.relative_to(PAGES)} uses .{name}")

    assert not offenders, (
        "these wrap themselves in a class nothing defines, so they get no "
        "width and no padding: " + "; ".join(offenders)
    )


def test_ordinary_pages_wrap_themselves_in_page():
    """
    The positive half. A page with no wrapper at all has the same symptom as
    one with an invented wrapper, and the same invisibility in every check
    except somebody opening it.
    """
    missing: list[str] = []

    for page in _pages():
        rel = str(page.relative_to(PAGES)).replace("\\", "/")
        if rel in LAYS_ITSELF_OUT:
            continue
        text = page.read_text(encoding="utf8")
        body = text.split("---", 2)[-1]
        if "<BaseLayout" not in body:
            continue
        if not re.search(r'class="[^"]*\bpage\b', body):
            missing.append(rel)

    assert not missing, (
        "these render inside BaseLayout without .page, so their content runs "
        "to the edge of the window: " + ", ".join(sorted(missing))
    )


# ── copy meant for the operator, printed for everybody ──────────────────────

def test_no_public_page_tells_a_reader_about_the_admin():
    """
    Empty states are the site's honest answer to missing content, and they are
    shown to READERS. Four of them explained where the content is entered —
    "This page is edited in the admin", "Projects are added in the admin" —
    which is a note to the operator printed on a page for everybody else.

    They only appear when something is empty, which is exactly the state a site
    is in on the day it launches.
    """
    import re

    # Comment blocks are stripped WHOLE rather than line by line: a multi-line
    # comment's continuation lines do not start with a marker, and checking
    # per-line flags them as copy. That is how this test first failed on three
    # of its own explanatory comments.
    def prose(text: str) -> str:
        text = re.sub(r"\{/\*.*?\*/\}", " ", text, flags=re.S)
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        return re.sub(r"(?m)^\s*//.*$", " ", text)

    offenders = []
    for page in _pages():
        if page.name.startswith(".") or "admin" in str(page):
            continue
        for line in prose(page.read_text()).splitlines():
            stripped = line.strip()
            if re.search(r"\b(in|to|from) the admin\b|admin panel", stripped, re.I):
                offenders.append(f"{page.name}: {stripped[:80]}")
    assert not offenders, (
        "operator-facing copy on a public page:\n  " + "\n  ".join(offenders)
    )
