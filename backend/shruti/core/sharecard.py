# SPDX-License-Identifier: AGPL-3.0-only
"""
The image a comparison looks like when somebody posts it.

**This exists because the share is the feature.** Two people comparing charts
will screenshot it or paste the link, and a link with no image is a grey box on
every timeline it lands on. Generated rather than screenshotted so it is right
every time and does not depend on anybody's browser.

Drawn with Pillow, which is already here for image dimensions, against the
site's own typefaces — EB Garamond and Commissioner, both OFL, shipped in
`assets/fonts` because a container has no fonts at all and a card in the
default bitmap face would look like a 1997 error dialogue.

**A tally, never a score.** The headline is a count of configurations, which is
arithmetic and true. A percentage would look like a measurement of a
relationship, and this site does not claim predictive validity for anything.
"""
from __future__ import annotations

import logging
import re
from io import BytesIO
from pathlib import Path

log = logging.getLogger(__name__)

# Twitter and most other cards want 1.91:1. 1200x630 is the size everything
# accepts and nothing crops badly.
WIDTH, HEIGHT = 1200, 630

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# The palette a design did not give us. Every design is a row now — see
# `CardDesign` — and these are only what a missing or malformed one falls back
# to, so a card always renders even if somebody saves a design with an empty
# colour.
FALLBACK = {
    "background": "#F6F2EF",
    "ink": "#26304A",
    "soft": "#4A5470",
    "faint": "#6E7890",
    "line": "#DCD6DC",
    "accent": "#A85A76",
}

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _rgb(value: str, fallback: str) -> tuple[int, int, int]:
    """Hex to a tuple, falling back rather than raising on a bad one."""
    raw = value if _HEX.match(value or "") else fallback
    return tuple(int(raw[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def _font(name: str, size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except Exception:                                  # noqa: BLE001
        # A card in the fallback face is ugly but still a card; a 500 here
        # would take out the page that embeds it.
        log.warning("card font %s is missing; falling back", name)
        return ImageFont.load_default()


def _circle(img, size: int):
    """Crop to a circle, because an avatar is round everywhere else it appears."""
    from PIL import Image, ImageDraw

    img = img.convert("RGBA")
    # Cover, not fit: a portrait squeezed into a square is somebody's art
    # distorted, and for a VTuber that art is their face.
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2,
                    (w - side) // 2 + side, (h - side) // 2 + side))
    img = img.resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _fit(draw, text: str, font, limit: int) -> str:
    """Trim to the width available, with an ellipsis rather than a hard cut."""
    if draw.textlength(text, font=font) <= limit:
        return text
    while text and draw.textlength(text + "…", font=font) > limit:
        text = text[:-1]
    return (text + "…") if text else ""


def _wrap(text: str, at: int) -> list[str]:
    """Word-wrap at roughly `at` characters, never mid-word."""
    words, lines, line = text.split(), [], ""
    for w in words:
        candidate = f"{line} {w}".strip()
        if len(candidate) > at and line:
            lines.append(line)
            line = w
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def comparison_card(
    *,
    left_name: str,
    right_name: str,
    headline: str,
    band: str,
    harmonious: int,
    hard: int,
    left_avatar: bytes | None = None,
    right_avatar: bytes | None = None,
    design: dict | None = None,
    backdrop: bytes | None = None,
) -> bytes:
    """
    One PNG. Never raises — a missing card must not take down the page.

    Laid out to `docs/design/HANDOFF_COMPATIBLE.md`. Four things changed from
    the first version and each is the reason for the one under it:

    1. **The verdict is the card.** 88px, left-aligned, on the optical centre.
       Centred between two avatars it read as a caption. It is the only line
       that has to survive being a thumbnail on a phone.
    2. **Avatars smaller, overlapped, top-left.** Overlapped they read as a
       pair; on opposite edges they read as a versus graphic. Smaller also
       stops the art-absent state looking like a failure — avatars are
       uploaded by each chart's own owner, so half-empty pairs are common.
    3. **Count and top marker on one line under the verdict.** They are the
       evidence FOR the verdict, and having them right there is what stops the
       card reading as a horoscope.
    4. **The disclaimer sits on the bottom rule opposite the site name.**
       Structural furniture rather than small print, which is the only way a
       disclaimer survives a future redesign. Never at reduced opacity.

    ONE SUBSTITUTION from the handoff, deliberate and visible: it specifies
    JetBrains Mono for the count, the marker and the site name. Only the two
    brand faces ship as TrueType — the mono exists in the site's fonts as
    .woff2, which Pillow cannot read — so those lines are set in Commissioner.
    Naming a font that is not there does not fail loudly; it silently falls
    back to a bitmap face and the card looks broken.
    """
    from PIL import Image, ImageDraw

    design = design or {}
    # Handoff colour roles, mapped onto the columns that store them.
    VERDICT = _rgb(design.get("ink", ""), FALLBACK["ink"])          # verdict
    NAMES = _rgb(design.get("soft", ""), FALLBACK["soft"])          # names
    MARKER = _rgb(design.get("faint", ""), FALLBACK["faint"])       # marker
    NOTE = _rgb(design.get("line", ""), FALLBACK["faint"])          # note / rules
    PAPER = _rgb(design.get("background", ""), FALLBACK["background"])
    COUNT = _rgb(design.get("accent", ""), FALLBACK["accent"])      # count

    M = 72                      # margin, all four sides
    INNER = WIDTH - M * 2

    card = Image.new("RGB", (WIDTH, HEIGHT), PAPER)

    if backdrop:
        try:
            art = Image.open(BytesIO(backdrop)).convert("RGB")
            # Cover, never squash: a design's artwork stretched to 1200x630 is
            # somebody's picture distorted.
            scale = max(WIDTH / art.width, HEIGHT / art.height)
            art = art.resize((round(art.width * scale), round(art.height * scale)),
                             Image.LANCZOS)
            card.paste(art, ((WIDTH - art.width) // 2, (HEIGHT - art.height) // 2))
            if design.get("scrim"):
                # Two bands, not one. The strip left between them keeps a slice
                # of the artwork visible under the verdict and echoes the
                # site's horizon rule — it is the design, not a gap.
                veil = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
                vd = ImageDraw.Draw(veil)
                vd.rectangle((0, 196, WIDTH, 482), fill=(*PAPER, 173))
                vd.rectangle((0, 502, WIDTH, HEIGHT), fill=(*PAPER, 173))
                card = Image.alpha_composite(card.convert("RGBA"), veil).convert("RGB")
        except Exception:                              # noqa: BLE001
            log.info("a card backdrop could not be read; using the flat colour")

    draw = ImageDraw.Draw(card)

    f_name = _font("Commissioner.ttf", 27)
    f_count = _font("Commissioner.ttf", 27)
    f_marker = _font("Commissioner.ttf", 22)
    f_note = _font("Commissioner.ttf", 19)
    f_mark = _font("Commissioner.ttf", 20)
    f_initial = _font("EBGaramond-SemiBold.ttf", 40)

    # ── top band: the pair ────────────────────────────────────────────────
    AV, TOP = 92, 72
    centres = [(M, TOP), (M + 72, TOP)]          # 20px of overlap
    faces = (left_avatar, right_avatar)
    names = (left_name or "—", right_name or "—")

    # Drawn back to front so the second disc overlaps the first.
    for (avatar, name), (x, y) in zip(zip(faces, names), centres):
        placed = False
        if avatar:
            try:
                disc = _circle(Image.open(BytesIO(avatar)), AV)
                card.paste(disc, (x, y), disc)
                placed = True
            except Exception:                      # noqa: BLE001
                log.info("an avatar could not be read; drawing the art-absent disc")
        if not placed:
            # Art-absent, not broken: a flat disc in the names colour at 12%,
            # a ring at 50%, and the initial. Half-empty pairs are the norm.
            plate = Image.new("RGBA", (AV, AV), (0, 0, 0, 0))
            pd = ImageDraw.Draw(plate)
            pd.ellipse((0, 0, AV - 1, AV - 1), fill=(*NAMES, 31),
                       outline=(*NAMES, 128), width=1)
            letter = (name.strip() or "?")[0].upper()
            lw = pd.textlength(letter, font=f_initial)
            pd.text(((AV - lw) / 2, AV / 2 - 26), letter, font=f_initial, fill=(*NAMES, 210))
            card = Image.alpha_composite(card.convert("RGBA"),
                                         Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)))
            card.paste(plate, (x, y), plate)
            card = card.convert("RGB")
            draw = ImageDraw.Draw(card)

    # Names, baseline-aligned with the disc centres.
    name_y = TOP + AV // 2 - 17
    x = 262
    first = _fit(draw, names[0], f_name, 300)
    draw.text((x, name_y), first, font=f_name, fill=NAMES)
    x += draw.textlength(first, font=f_name) + 10
    draw.text((x, name_y), "and", font=f_name, fill=MARKER)
    x += draw.textlength("and", font=f_name) + 10
    draw.text((x, name_y), _fit(draw, names[1], f_name, WIDTH - M - x),
              font=f_name, fill=NAMES)

    # ── the two hairlines, at 38% ─────────────────────────────────────────
    rules = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rules)
    rd.rectangle((M, 190, WIDTH - M, 190), fill=(*NOTE, 97))
    rd.rectangle((M, 502, WIDTH - M, 502), fill=(*NOTE, 97))
    card = Image.alpha_composite(card.convert("RGBA"), rules).convert("RGB")
    draw = ImageDraw.Draw(card)

    # ── middle band: the verdict, then its evidence ───────────────────────
    # Wrap at twenty characters and step down only if it still will not fit.
    # "Written in the same sky" is the longest of the five and sits at 88, so
    # the ladder only ever fires on a band added later.
    lines: list[str] = []
    for size in (88, 76, 68):
        f_verdict = _font("EBGaramond-SemiBold.ttf", size)
        lines = _wrap(band, 20)
        if len(lines) <= 2 and all(draw.textlength(l, font=f_verdict) <= INNER for l in lines):
            break
    y = 236
    for line in lines[:2]:
        draw.text((M, y), line, font=f_verdict, fill=VERDICT)
        y += int(size * 0.98)

    # 20px in the handoff measured from a single-line verdict. Two lines put a
    # descender where that gap was, so it is measured from the descender here.
    tally_y = y + 30
    tally = f"{harmonious} harmonious · {hard} hard"
    draw.text((M, tally_y), tally, font=f_count, fill=COUNT)
    x = M + draw.textlength(tally, font=f_count) + 16
    draw.text((x, tally_y + 5), _fit(draw, headline, f_marker, WIDTH - M - x),
              font=f_marker, fill=MARKER)

    # ── bottom band: the disclaimer is furniture, not small print ─────────
    note = "What the tradition says about the configurations present. Not a prediction."
    draw.text((M, 520), _fit(draw, note, f_note, INNER - 220), font=f_note, fill=NOTE)
    mark = "shrutivtuber.com"
    draw.text((WIDTH - M - draw.textlength(mark, font=f_mark), 521),
              mark, font=f_mark, fill=NOTE)

    out = BytesIO()
    card.save(out, format="PNG", optimize=True)
    return out.getvalue()


def invite_card(
    *,
    name: str,
    avatar: bytes | None = None,
    design: dict | None = None,
    backdrop: bytes | None = None,
) -> bytes:
    """
    The image an INVITATION turns into on a timeline.

    A comparison already had one; the invite did not, and the invite is the more
    public of the two. It is the link somebody posts to tag another creator, so
    it is seen by that creator's whole timeline before anybody has compared
    anything — and it was unfurling with the generic site card, which made the
    most public moment in the loop look like a link to a homepage.

    Deliberately simpler than the comparison card. There is no tally yet and
    nothing to be honest or dishonest about: one name, one face, and what is
    being asked.
    """
    from PIL import Image, ImageDraw

    design = design or {}
    INK = _rgb(design.get("ink", ""), FALLBACK["ink"])
    SOFT = _rgb(design.get("soft", ""), FALLBACK["soft"])
    FAINT = _rgb(design.get("faint", ""), FALLBACK["faint"])
    PAPER = _rgb(design.get("background", ""), FALLBACK["background"])
    LINE = _rgb(design.get("line", ""), FALLBACK["line"])
    ROSE = _rgb(design.get("accent", ""), FALLBACK["accent"])

    card = Image.new("RGB", (WIDTH, HEIGHT), PAPER)

    if backdrop:
        try:
            art = Image.open(BytesIO(backdrop)).convert("RGB")
            scale = max(WIDTH / art.width, HEIGHT / art.height)
            art = art.resize((round(art.width * scale), round(art.height * scale)),
                             Image.LANCZOS)
            card.paste(art, ((WIDTH - art.width) // 2, (HEIGHT - art.height) // 2))
        except Exception:                              # noqa: BLE001
            log.warning("invite card backdrop would not open; using the flat colour")

    draw = ImageDraw.Draw(card)

    # The two faces actually shipped in assets/fonts. Naming a weight that is
    # not there does not fail loudly — `_font` falls back to Pillow's bitmap
    # default, and the card renders looking like a 1997 error dialogue.
    eyebrow = _font("Commissioner.ttf", 24)
    display = _font("EBGaramond-SemiBold.ttf", 62)
    body = _font("Commissioner.ttf", 28)
    mark = _font("EBGaramond-SemiBold.ttf", 26)

    # A face if there is one, on the left, so the eye lands on a person.
    text_left = 96
    if avatar:
        try:
            face = _circle(Image.open(BytesIO(avatar)), 260)
            card.paste(face, (96, (HEIGHT - 260) // 2), face)
            text_left = 96 + 260 + 56
        except Exception:                              # noqa: BLE001
            log.warning("invite card avatar would not open; drawing without it")

    limit = WIDTH - text_left - 96

    draw.text((text_left, 168), "AN INVITATION", font=eyebrow, fill=ROSE)

    who = _fit(draw, name or "Someone", display, limit)
    draw.text((text_left, 214), who, font=display, fill=INK)

    draw.text((text_left, 300), _fit(draw, "wants to compare charts with you.", body, limit),
              font=body, fill=SOFT)

    draw.line((text_left, 372, text_left + min(limit, 420), 372), fill=LINE, width=2)

    draw.text((text_left, 396),
              _fit(draw, "No account needed. It takes one form.", body, limit),
              font=body, fill=FAINT)

    draw.text((text_left, HEIGHT - 96), "shrutivtuber.com", font=mark, fill=FAINT)

    out = BytesIO()
    card.save(out, format="PNG", optimize=True)
    return out.getvalue()
