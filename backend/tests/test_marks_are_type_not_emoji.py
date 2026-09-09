# SPDX-License-Identifier: AGPL-3.0-only
"""
A zodiac sign is type, not a picture.

Glyph.astro says it already: without U+FE0E a browser is free to render ☾ ♄ ♈
from a colour emoji font, which ignores `color` entirely — the mark comes out
as somebody else's picture instead of type in the site's rose. Its comment adds
that this "is easy to lose in a refactor", which is a test waiting to be
written, and this is it.

It was lost. Sixty marks carried the selector and eighty-eight did not, and the
horoscope desk shipped with ✍ U+270D — a Dingbat with emoji presentation by
default — beside twelve monochrome symbols. She saw that one immediately; the
eighty-eight were invisible on a machine whose font stack happens to resolve
them monochrome, and would not be on a phone.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[2] / "frontend" / "site" / "src"


SRC = _src()
FE0E = "\ufe0e"

# The zodiac, the planets and the nodes: every character the designer's guide
# calls a type mark and a browser may render from an emoji font.
MARKS = set(range(0x2648, 0x2654)) | {
    0x2609, 0x263D, 0x263E, 0x263F, 0x2640, 0x2642, 0x2643, 0x2644,
    0x2645, 0x2646, 0x2647, 0x260A, 0x260B,
}

# Characters whose default presentation is a COLOUR glyph and which therefore
# have no place among these marks at all — no selector rescues a lock.
EMOJI_ONLY = {0x270D, 0x1F512, 0x270F, 0x2712, 0x1F4DD}


def _code_lines(path: Path) -> list[tuple[int, str]]:
    """Lines that are not comments. A comment explaining the problem does not
    have to demonstrate it."""
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if line.lstrip().startswith(("*", "//", "/*")):
            continue
        out.append((n, line))
    return out


def _files() -> list[Path]:
    return sorted(list(SRC.rglob("*.astro")) + list(SRC.rglob("*.ts")))


def test_the_source_is_where_we_think() -> None:
    assert SRC.is_dir(), f"{SRC} is not readable"
    assert _files(), "no source files found"


def test_every_mark_asks_for_text_presentation() -> None:
    offenders: list[str] = []
    for f in _files():
        for n, line in _code_lines(f):
            for i, ch in enumerate(line):
                if ord(ch) not in MARKS:
                    continue
                if (line[i + 1] if i + 1 < len(line) else "") != FE0E:
                    offenders.append(f"{f.relative_to(SRC)}:{n}  {ch!r}")
    assert not offenders, (
        "these marks may render from a colour emoji font, which ignores the "
        f"site's palette entirely — append U+FE0E:\n  "
        + "\n  ".join(offenders[:12])
    )


def test_no_emoji_is_used_as_a_type_mark() -> None:
    """Some characters are pictures whatever you ask for.

    ✍ has no monochrome form to fall back to on most platforms, so a variation
    selector does not save it — the answer is a different character. Mercury,
    the scribe's planet, sits in the same Unicode block as the sun and the
    moons already in the set.
    """
    offenders: list[str] = []
    for f in _files():
        for n, line in _code_lines(f):
            for ch in line:
                if ord(ch) in EMOJI_ONLY:
                    offenders.append(f"{f.relative_to(SRC)}:{n}  {ch!r}")
    assert not offenders, (
        "these are pictures, not type marks; choose a symbol instead:\n  "
        + "\n  ".join(offenders[:12])
    )


def test_a_character_range_is_written_in_codepoints() -> None:
    """A regex range of marks must not be written with the literal characters.

    Sweeping U+FE0E onto every mark put one INSIDE a character class and made
    it invalid — "Range out of order in character class". Written as
    `\\u2648-\\u2653` the same sweep cannot reach it.
    """
    offenders: list[str] = []
    for f in _files():
        for n, line in _code_lines(f):
            for m in re.finditer(r"\[[^\]]*\]", line):
                body = m.group(0)
                if "-" in body and any(ord(c) in MARKS for c in body):
                    offenders.append(f"{f.relative_to(SRC)}:{n}  {body[:40]}")
    assert not offenders, (
        "write mark ranges as codepoints so a sweep cannot corrupt them:\n  "
        + "\n  ".join(offenders[:6])
    )
