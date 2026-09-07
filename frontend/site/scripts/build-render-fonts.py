#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Build the fonts the OG card is rasterised with.

The site serves woff2, which is a web-transport wrapper the rasteriser cannot
open, and it serves them as variable fonts whose DEFAULT instance is not the
weight the site actually renders — Commissioner's default is Thin (100), so a
card built from the file as-shipped comes out in hairlines. The Latin subsets
also contain no astrological glyphs at all, and a missing glyph rasterises as
a hollow box rather than as an error.

So this produces three static fonts:

  Commissioner.ttf   her body face, pinned to 400
  EBGaramond.ttf     her display face, upright, pinned to 500
  AstroSymbols.ttf   a 5KB cut of DejaVu Sans holding the seventeen glyphs the
                     wheel prints and nothing else

Re-run it if the site's faces are ever regenerated; do not edit the output.

    python3 frontend/site/scripts/build-render-fonts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import decompress
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
SRC = SITE / "public" / "fonts"
OUT = SITE / "fonts-render"

# The Latin subsets, by content hash. If the faces are regenerated these names
# change — the script fails loudly rather than silently building the wrong one.
BODY = "commissioner-cf71c8ef.woff2"
DISPLAY = "ebgaramond-ef73a8c5.woff2"      # upright; -a24366b6 is the italic

# Zodiac, the seven classical planets, the three moderns, both nodes, the
# retrograde mark, and the degree/minute/second marks the card prints.
GLYPHS = list(range(0x2648, 0x2654)) + [
    0x2609, 0x263D, 0x263E, 0x263F, 0x2640, 0x2642, 0x2643, 0x2644,
    0x2645, 0x2646, 0x2647, 0x260A, 0x260B, 0x211E, 0x00B0, 0x2032, 0x2033,
]

SYMBOL_SOURCES = [
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]


def rename(font: TTFont, family: str) -> None:
    """Give a font one unambiguous family name.

    resvg matches `font-family` in the SVG against the name inside the file.
    The DejaVu cut would otherwise still call itself "DejaVu Sans", and an
    instanced Commissioner still calls itself "Commissioner Thin" — so the
    card would ask for a family that is not there and fall back silently.
    """
    for rec in font["name"].names:
        if rec.nameID in (1, 16):
            font["name"].setName(family, rec.nameID, rec.platformID,
                                 rec.platEncID, rec.langID)
        elif rec.nameID in (2, 17):
            font["name"].setName("Regular", rec.nameID, rec.platformID,
                                 rec.platEncID, rec.langID)
        elif rec.nameID == 4:
            font["name"].setName(family, rec.nameID, rec.platformID,
                                 rec.platEncID, rec.langID)
        elif rec.nameID == 6:
            font["name"].setName(family.replace(" ", ""), rec.nameID,
                                 rec.platformID, rec.platEncID, rec.langID)


def pin(woff2: str, weight: int, family: str, out_name: str) -> None:
    src = SRC / woff2
    if not src.is_file():
        sys.exit(f"missing {src} — were the site faces regenerated?")
    tmp = OUT / f".{out_name}.tmp"
    decompress(str(src), str(tmp))
    font = TTFont(str(tmp))
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": weight})
    rename(font, family)
    font.save(str(OUT / out_name))
    tmp.unlink()
    print(f"  {out_name:22} {family:16} wght={weight:<4} "
          f"{round((OUT / out_name).stat().st_size / 1024)} KB")


def symbols(out_name: str, family: str) -> None:
    src = next((p for p in SYMBOL_SOURCES if Path(p).is_file()), None)
    if src is None:
        sys.exit("DejaVu Sans not found — install fonts-dejavu-core (or "
                 "ttf-dejavu) and re-run")
    tmp = OUT / f".{out_name}.tmp"
    subset.main([
        src, f"--output-file={tmp}",
        "--unicodes=" + ",".join(f"U+{c:04X}" for c in GLYPHS),
        "--no-hinting", "--desubroutinize", "--drop-tables+=DSIG",
    ])
    font = TTFont(str(tmp))
    rename(font, family)
    font.save(str(OUT / out_name))
    tmp.unlink()

    missing = [f"U+{c:04X}" for c in GLYPHS
               if c not in TTFont(str(OUT / out_name)).getBestCmap()]
    if missing:
        sys.exit(f"glyphs absent from the cut: {missing}")
    print(f"  {out_name:22} {family:16} {len(GLYPHS)} glyphs  "
          f"{round((OUT / out_name).stat().st_size / 1024, 1)} KB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.ttf"):
        old.unlink()
    print("building render fonts:")
    pin(BODY, 400, "Commissioner", "Commissioner.ttf")
    pin(DISPLAY, 500, "EB Garamond", "EBGaramond.ttf")
    symbols("AstroSymbols.ttf", "AstroSymbols")


if __name__ == "__main__":
    main()
