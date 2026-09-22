# SPDX-License-Identifier: AGPL-3.0-only
"""
A chart may not depend on what a reader has installed.

⚠ The wheels print zodiac, planet and aspect glyphs. The site's own faces —
Commissioner, EB Garamond, JetBrains Mono — contain none of them, so a glyph
with no font named on it falls back to whatever the reader's machine
happens to have. On 20 September that drew half a zodiac doubled and
garbled on one machine and clean on another, which is the kind of fault
nobody can reproduce and everybody can see.

So: the symbol face is served, it is declared, and every element that prints
one of those glyphs names it.
"""
from __future__ import annotations

import re
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
FACE = "AstroSymbols"


def test_the_symbol_face_is_served_to_browsers() -> None:
    shipped = list((FRONTEND / "site/public/fonts").glob("astrosymbols-*.woff2"))
    assert shipped, "no astrosymbols woff2 in public/fonts — the browser has nothing to load"
    assert shipped[0].stat().st_size < 20_000, "the cut should be a few kilobytes, not a whole face"


def test_the_face_is_declared_wherever_the_other_faces_are() -> None:
    for sheet in ("../frontend/shared/src/tokens/fonts-local.css", "../frontend/site/public/fonts/faces.css"):
        css = (Path(__file__).resolve().parents[1] / sheet).read_text()
        assert f"font-family: '{FACE}'" in css, f"{sheet}: the symbol face is not declared"
        block = css[css.index(f"font-family: '{FACE}'"):]
        assert "astrosymbols-" in block[:600], f"{sheet}: declared without a file to load"
        assert "U+2648-2653" in block[:900] or "U+2642-2653" in block[:900], \
            f"{sheet}: the unicode-range does not cover the zodiac"


def test_every_drawn_glyph_names_the_face() -> None:
    """⚠ A glyph with no font named on it is a glyph nobody can promise to draw."""
    card = (FRONTEND / "site/src/components/counters/SkyCard.astro").read_text()
    styles = card[card.index("<style"):]
    for cls in (".sg", ".bg", ".glyph"):
        assert cls in styles, f"{cls}: no rule at all"
    naming = re.findall(r"([^{}]*)\{[^}]*" + FACE + r"[^}]*\}", styles)
    named = " ".join(naming)
    for cls in (".sg", ".bg", ".glyph"):
        assert cls in named, f"{cls}: draws a glyph without naming the symbol face"


def test_the_render_note_says_this_one_is_served() -> None:
    """The render fonts are not web fonts — except this one, and the note must say so."""
    note = (FRONTEND / "site/fonts-render/README.md").read_text()
    assert "exception" in note.lower() and "astrosymbols-" in note, \
        "fonts-render/README still claims none of these reaches a browser"
