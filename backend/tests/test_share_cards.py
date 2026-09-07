# SPDX-License-Identifier: AGPL-3.0-only
"""
The picture a shared reading shows, and the fonts it is drawn with.

Everything here guards a failure that produces a VALID-LOOKING RESULT. That is
the whole character of this surface: a share card that is wrong is still a
200, still a well-formed PNG, and still 1200x630. Nothing throws.

  * `fontBuffers` instead of `fontFiles` — resvg accepts it, ignores it, and
    returns a card with every piece of text missing. The first one built that
    way was a wheel with no glyphs, no sign name and no byline.
  * a font without the astrological block — every glyph becomes a hollow box.
  * `180 - lon` instead of `180 + lon` — the zodiac runs clockwise. Both draw a
    plausible chart; the only tell is that Taurus sits above Aries instead of
    below. Two files in this repo carried a comment saying "anticlockwise"
    while doing the opposite.
  * a native module missing from the runtime image — a 500 on every share,
    discovered by whoever pastes the first link.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path


def _root() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base
    return here.parents[2]


ROOT = _root()
SRC = ROOT / "frontend" / "site" / "src"
FONTS = ROOT / "frontend" / "site" / "fonts-render"
CARD = SRC / "pages" / "horoscopes" / "[sign]" / "[period]" / "[covers]" / "og.png.ts"


def code_of(path: Path) -> str:
    """Source with comments stripped — this file's own prose names both the
    right and the wrong spelling of everything it checks."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)//.*$", " ", text)


# ── a minimal cmap reader ────────────────────────────────────────────────────
# fontTools is not in the test image and is not worth adding for this. Formats
# 4 and 12 are the only ones these files use.

def codepoints(ttf: Path) -> set[int]:
    data = ttf.read_bytes()
    (num_tables,) = struct.unpack(">H", data[4:6])
    cmap_off = None
    for i in range(num_tables):
        rec = 12 + i * 16
        if data[rec:rec + 4] == b"cmap":
            (cmap_off,) = struct.unpack(">I", data[rec + 8:rec + 12])
            break
    assert cmap_off is not None, f"{ttf.name} has no cmap table"

    (n_sub,) = struct.unpack(">H", data[cmap_off + 2:cmap_off + 4])
    best = None
    for i in range(n_sub):
        rec = cmap_off + 4 + i * 8
        plat, enc = struct.unpack(">HH", data[rec:rec + 4])
        (off,) = struct.unpack(">I", data[rec + 4:rec + 8])
        # Unicode BMP or full-repertoire subtables only.
        if (plat, enc) in ((3, 1), (3, 10), (0, 3), (0, 4), (0, 6)):
            best = cmap_off + off if best is None else best
            if (plat, enc) in ((3, 10), (0, 4), (0, 6)):
                best = cmap_off + off
    assert best is not None, f"{ttf.name} has no unicode cmap subtable"

    out: set[int] = set()
    (fmt,) = struct.unpack(">H", data[best:best + 2])
    if fmt == 4:
        (seg2,) = struct.unpack(">H", data[best + 6:best + 8])
        seg = seg2 // 2
        ends = struct.unpack(">%dH" % seg, data[best + 14:best + 14 + seg2])
        s0 = best + 16 + seg2
        starts = struct.unpack(">%dH" % seg, data[s0:s0 + seg2])
        for a, b in zip(starts, ends):
            if a == 0xFFFF:
                continue
            out.update(range(a, b + 1))
    elif fmt == 12:
        (n_groups,) = struct.unpack(">I", data[best + 12:best + 16])
        for i in range(n_groups):
            g = best + 16 + i * 12
            a, b, _ = struct.unpack(">III", data[g:g + 12])
            out.update(range(a, b + 1))
    else:
        raise AssertionError(f"{ttf.name}: unhandled cmap format {fmt}")
    return out


# ── the fonts ────────────────────────────────────────────────────────────────

ZODIAC = list(range(0x2648, 0x2654))
BODIES = [0x2609, 0x263D, 0x263F, 0x2640, 0x2642, 0x2643, 0x2644,
          0x2645, 0x2646, 0x2647, 0x260A, 0x260B]


def test_the_render_fonts_are_shipped():
    """
    The site serves woff2 only, which the rasteriser cannot open.

    These three are decompressed, weight-pinned copies built by
    scripts/build-render-fonts.py. Without them the card renders with no text
    at all and still returns 200.
    """
    assert FONTS.is_dir(), f"{FONTS} is missing"
    have = {p.name for p in FONTS.glob("*.ttf")}
    assert have == {"Commissioner.ttf", "EBGaramond.ttf", "AstroSymbols.ttf"}, have


def test_the_symbol_font_has_every_glyph_the_wheel_prints():
    """A codepoint the font lacks renders as a hollow box, not as an error."""
    cps = codepoints(FONTS / "AstroSymbols.ttf")
    missing = [f"U+{c:04X}" for c in ZODIAC + BODIES + [0x211E] if c not in cps]
    assert not missing, f"AstroSymbols.ttf is missing {missing}"


def test_the_text_fonts_carry_latin():
    for name in ("Commissioner.ttf", "EBGaramond.ttf"):
        cps = codepoints(FONTS / name)
        for ch in "ABCXYZabcxyz0189":
            assert ord(ch) in cps, f"{name} cannot render {ch!r}"


def test_the_fonts_are_reproducible():
    """Built by a script that is in the repo, not decompressed by hand once."""
    script = ROOT / "frontend" / "site" / "scripts" / "build-render-fonts.py"
    assert script.is_file()
    body = script.read_text(encoding="utf-8")
    assert "instantiateVariableFont" in body, (
        "Commissioner is variable and defaults to Thin — a card built from the "
        "file as shipped comes out in hairlines"
    )


# ── the card ─────────────────────────────────────────────────────────────────

def test_the_card_endpoint_exists():
    assert CARD.is_file()


def test_the_card_passes_font_paths_not_buffers():
    code = code_of(CARD)
    assert "fontFiles" in code
    assert "fontBuffers" not in code, (
        "resvg accepts fontBuffers, ignores it, and returns a card with no text"
    )


def test_the_card_does_not_load_system_fonts():
    """
    Otherwise it renders differently depending on what the base image happens
    to ship, and the failure only appears once the image is rebuilt.
    """
    assert re.search(r"loadSystemFonts\s*:\s*false", code_of(CARD))


def test_the_card_validates_what_it_is_asked_to_draw():
    """An endpoint that renders any string is an unbounded image generator."""
    code = code_of(CARD)
    assert "SHAPE" in code and "404" in code
    assert "ZODIAC.includes" in code


def test_the_card_shares_the_wheel_geometry():
    code = code_of(CARD)
    assert "lib/wheel" in code, (
        "the card must import the geometry, not carry a fifth copy of it"
    )


def test_the_reading_points_at_its_own_card():
    code = code_of(SRC / "components" / "horoscope" / "Reading.astro")
    assert "og.png" in code and "ogImage=" in code


# ── the direction trap ───────────────────────────────────────────────────────

WHEELS = [
    SRC / "lib" / "wheel.ts",
    SRC / "components" / "chart" / "TransitWheel.astro",
    SRC / "components" / "chart" / "WheelStepper.astro",
    SRC / "components" / "counters" / "SkyCard.astro",
    SRC / "pages" / "overlay" / "sky.astro",
    CARD,
]


def test_the_shared_geometry_runs_the_zodiac_anticlockwise():
    code = code_of(SRC / "lib" / "wheel.ts")
    assert "180 + degrees" in code, "nine o'clock is 0deg and the zodiac runs anticlockwise"
    assert "cy - radius" in code, "SVG y grows downward, so the sine is subtracted"


def test_no_wheel_draws_the_zodiac_backwards():
    """
    `180 - lon` is the clockwise spelling. It has been written twice in this
    repo, both times under a comment claiming anticlockwise.
    """
    for path in WHEELS:
        assert path.is_file(), f"{path} is missing — this check would prove nothing"
        code = code_of(path)
        assert not re.search(r"180\s*-\s*(lon|longitude|angle|deg)", code), \
            f"{path.name} runs the zodiac clockwise"


# ── the runtime image ────────────────────────────────────────────────────────

DOCKERFILE = ROOT / "frontend" / "site" / "Dockerfile"


def test_the_image_ships_the_fonts_and_a_real_node_modules():
    """
    A native module cannot be bundled, so it has to genuinely be present.

    pnpm fills the package's own node_modules with symlinks into the workspace
    store; copying that directory alone lands them dangling, and the failure is
    a 500 on the first share rather than anything at build time.
    """
    body = DOCKERFILE.read_text(encoding="utf-8")
    assert "fonts-render" in body, "the render fonts never reach the image"
    assert "pnpm deploy" in body, (
        "the runtime tree must be resolved, or @resvg/resvg-js is missing"
    )


def test_the_rasteriser_is_declared():
    import json
    pkg = json.loads((ROOT / "frontend" / "site" / "package.json").read_text())
    assert "@resvg/resvg-js" in pkg.get("dependencies", {})
