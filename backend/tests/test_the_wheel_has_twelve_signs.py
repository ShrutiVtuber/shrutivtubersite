# SPDX-License-Identifier: AGPL-3.0-only
"""
A wheel has twelve signs, drawn once each, in zodiacal order.

The sky card on the phone had six blank sectors and six sectors with two
signs drawn on top of each other. Nothing was missing from the data: the
glyph list was built with `"♈︎♉︎…".split("")` on a string that already
carried U+FE0E after every sign, and a split by "" splits by code unit, so
the list had twenty-four entries — sign, selector, sign, selector — and the
rim loop placed all twenty-four at thirty-degree steps, twice round.

`lib/wheel.ts` is the one definition of the zodiac in drawing order, and the
comment there says anything that draws a wheel imports it. This test holds
that: nobody splits a glyph string, and every list of the twelve signs in the
frontend is the twelve signs, once each, in order, each with its selector.
"""
from __future__ import annotations

import re
from pathlib import Path

from test_marks_are_type_not_emoji import SRC

FE0E = "︎"
ZODIAC = "♈♉♊♋♌♍♎♏♐♑♒♓"
GLYPH_STRING = re.compile(r'["\'`]([^"\'`\n]*[♈-♓][^"\'`\n]*)["\'`]\s*\.split\(')


def _sources():
    for p in sorted(SRC.rglob("*")):
        if p.suffix in {".astro", ".ts", ".tsx", ".js", ".mjs"} and "node_modules" not in p.parts:
            yield p


def test_no_glyph_string_is_split_by_code_unit():
    guilty = []
    for p in _sources():
        for m in GLYPH_STRING.finditer(p.read_text(encoding="utf-8")):
            guilty.append(f"{p.relative_to(SRC)}: {m.group(0)[:60]}")
    assert not guilty, "a split by code unit halves the zodiac:\n" + "\n".join(guilty)


def test_the_wheel_defines_the_zodiac_once_in_order():
    wheel = (SRC / "lib" / "wheel.ts").read_text(encoding="utf-8")
    block = re.search(r"SIGN_GLYPH = \[(.*?)\]", wheel, re.S)
    assert block, "lib/wheel.ts no longer exports SIGN_GLYPH"
    entries = re.findall(r'"([^"]+)"', block.group(1))
    assert [e[0] for e in entries] == list(ZODIAC), "the twelve signs, in zodiacal order"
    assert all(e == e[0] + FE0E for e in entries), "each entry is one sign and its text selector"


ORDERED = re.compile(r'["\'`][^"\'`\n]*♈[^"\'`\n]*♉[^"\'`\n]*♊[^"\'`\n]*["\'`]')


def test_every_wheel_draws_the_one_definition():
    """Nobody keeps a second list of the zodiac in drawing order. A record keyed
    by sign name (a lookup, not an order) is fine; a list or a string of the
    signs in sequence is the thing that was twenty-four long."""
    for p in _sources():
        if p.name == "wheel.ts":
            continue
        code = p.read_text(encoding="utf-8")
        rel = p.relative_to(SRC)
        assert not re.search(r"const SIGN_GLYPHS? *(: *[^=]+)?= *[\[\"'`]", code), f"{rel} keeps its own list of the zodiac"
        assert not ORDERED.search(code), f"{rel} holds the zodiac in sequence in one string — import SIGN_GLYPH from lib/wheel"
        if "SIGN_GLYPH.map(" in code:
            assert re.search(r'import \{[^}]*\bSIGN_GLYPH\b[^}]*\} from "[./]+/lib/wheel"', code), (
                f"{rel} walks the rim without importing SIGN_GLYPH from lib/wheel"
            )
