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
from io import BytesIO
from pathlib import Path

log = logging.getLogger(__name__)

# Twitter and most other cards want 1.91:1. 1200x630 is the size everything
# accepts and nothing crops badly.
WIDTH, HEIGHT = 1200, 630

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# The site's palette, as the card must match the page it came from.
INK = (38, 48, 74)
SOFT = (74, 84, 112)
FAINT = (110, 120, 144)
PAPER = (246, 242, 239)
LINE = (220, 214, 220)
ROSE = (168, 90, 118)


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
) -> bytes:
    """One PNG. Never raises — a missing card must not take down the page."""
    from PIL import Image, ImageDraw

    card = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(card)

    display = _font("EBGaramond-SemiBold.ttf", 58)
    small = _font("Commissioner.ttf", 26)
    tiny = _font("Commissioner.ttf", 22)
    huge = _font("EBGaramond-SemiBold.ttf", 92)

    # A horizon line, the site's one recurring motif.
    draw.line((0, HEIGHT - 96, WIDTH, HEIGHT - 96), fill=LINE, width=2)

    # The two avatars, or two quiet placeholders where there are none. A
    # missing avatar must not leave a hole — plenty of people will have one
    # side and not the other.
    size = 168
    for avatar, cx in ((left_avatar, 250), (right_avatar, WIDTH - 250)):
        box = (cx - size // 2, 118)
        if avatar:
            try:
                card.paste(_circle(Image.open(BytesIO(avatar)), size), box,
                           _circle(Image.open(BytesIO(avatar)), size))
                continue
            except Exception:                          # noqa: BLE001
                log.info("an avatar could not be read; drawing the placeholder")
        draw.ellipse((box[0], box[1], box[0] + size, box[1] + size),
                     outline=LINE, width=3)

    # Their names under each.
    for name, cx in ((left_name, 250), (right_name, WIDTH - 250)):
        text = _fit(draw, name or "—", small, 300)
        w = draw.textlength(text, font=small)
        draw.text((cx - w / 2, 118 + size + 22), text, font=small, fill=INK)

    # The band, in the middle, where the eye lands — one phrase to screenshot.
    # Sized to fit rather than truncated: "Written in the same sky" is the
    # longest and it is also the one people most want to post.
    verdict = _font("EBGaramond-SemiBold.ttf", 62)
    if draw.textlength(band, font=verdict) > 420:
        verdict = _font("EBGaramond-SemiBold.ttf", 46)
    w = draw.textlength(band, font=verdict)
    draw.text((WIDTH / 2 - w / 2, 168), band, font=verdict, fill=INK)

    # The count underneath, always, so the band can be argued with. A verdict
    # with its own evidence beside it is a different thing from a verdict.
    tally = f"{harmonious} harmonious · {hard} hard"
    w = draw.textlength(tally, font=tiny)
    draw.text((WIDTH / 2 - w / 2, 258), tally, font=tiny, fill=FAINT)

    # The top marker, across the card.
    text = _fit(draw, headline, display, WIDTH - 160)
    w = draw.textlength(text, font=display)
    draw.text((WIDTH / 2 - w / 2, 372), text, font=display, fill=INK)

    # And the line that stops it being a claim. On the card itself, not only
    # on the page — a card travels without its page.
    note = "What the tradition says about the configurations present. Not a prediction."
    text = _fit(draw, note, tiny, WIDTH - 120)
    w = draw.textlength(text, font=tiny)
    draw.text((WIDTH / 2 - w / 2, 452), text, font=tiny, fill=SOFT)

    mark = "shrutivtuber.com"
    w = draw.textlength(mark, font=tiny)
    draw.text((WIDTH / 2 - w / 2, HEIGHT - 62), mark, font=tiny, fill=ROSE)

    out = BytesIO()
    card.save(out, format="PNG", optimize=True)
    return out.getvalue()
