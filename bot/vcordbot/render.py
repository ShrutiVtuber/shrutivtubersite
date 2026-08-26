# SPDX-License-Identifier: AGPL-3.0-only
"""
Answers, as Discord embeds.

Plain dictionaries rather than library objects, so every one of these can be
asserted against in a test with no gateway, no token and no server. The Discord
layer converts at the last moment.

**The footer is not decoration.** It is on every message, permanently, and it
does two jobs at once: it says where the answer came from, and it says the
message was posted by a machine. There is no paid tier that removes it — which
makes it more important to get right, not less. One line of subtext, never its
own embed, never twice in a message.
"""
from __future__ import annotations

from datetime import datetime, timezone

# Discord's subtext marker. Renders small and quiet, and unlike an embed footer
# it can carry a link — which an embed footer cannot, and this line has to.
SUBTEXT = "-# "

ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]

# Text presentation, so a client does not substitute a colour-emoji font and
# ignore the surrounding style. Same rule the website follows.
TEXT = "︎"
GLYPH = {
    "Sun": f"☉{TEXT}", "Moon": f"☾{TEXT}", "Mars": f"♂{TEXT}",
    "Mercury": f"☿{TEXT}", "Jupiter": f"♃{TEXT}", "Venus": f"♀{TEXT}",
    "Saturn": f"♄{TEXT}",
}


def footer(bot_url: str, site_url: str) -> str:
    """The one line every message ends with."""
    return f"{SUBTEXT}[vcordbot]({bot_url}) · posted automatically · [instruments]({site_url}/tools)"


def _stamp(iso: str) -> str:
    """
    A Discord timestamp, which every reader sees in their OWN timezone.

    This is the single best thing Discord gives a tool like this: one string
    that is correct for a viewer in Athens and a viewer in Toronto at once, so
    the bot never has to ask where anybody is or apologise for guessing.
    """
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return iso
    return f"<t:{int(dt.astimezone(timezone.utc).timestamp())}:t>"


def embed(title: str, description: str, *, fields=None, url=None) -> dict:
    out: dict = {"title": title, "description": description, "color": 0x26304A}
    if url:
        out["url"] = url
    if fields:
        out["fields"] = fields
    return out


def planetary_hours(data: dict, place: str, bot_url: str, site_url: str) -> dict:
    """The hour now, the ruler, and when it turns over."""
    now = data.get("current") or {}
    ruler = now.get("ruler", "—")
    glyph = GLYPH.get(ruler, "")
    index = now.get("index", 0)
    part = "night" if now.get("isNight") else "day"

    lines = [
        f"**{glyph} {ruler}** — the {ROMAN[index] if 0 < index < len(ROMAN) else index} hour of the {part}.",
        f"Runs until {_stamp(now.get('endsAt', ''))}.",
        "",
        f"Sunrise {_stamp(data.get('sunrise',''))} · sunset {_stamp(data.get('sunset',''))}",
        f"The day belongs to **{data.get('dayRuler','—')}**.",
        "",
        # The fact that makes the answer make sense, and the reason this is not
        # simply a clock.
        "An hour here is a twelfth of the daylight, so it is only sixty minutes twice a year.",
        "",
        footer(bot_url, site_url),
    ]
    return embed(f"Planetary hour · {place}", "\n".join(lines),
                 url=f"{site_url}/tools/planetary-hours")


def isopsephy(data: dict, bot_url: str, site_url: str) -> dict:
    """The sum, the letters that made it, and what was ignored."""
    total = data.get("total", 0)
    cipher = (data.get("cipher") or {}).get("name", "isopsephy")
    letters = data.get("letters") or []
    breakdown = " + ".join(f"{l['char']} {l['value']}" for l in letters[:24])
    if len(letters) > 24:
        breakdown += " …"

    reduction = (data.get("reduction") or {}).get("final")
    unmatched = data.get("unmatched") or []

    lines = [f"## {total}", ""]
    if breakdown:
        lines += [breakdown, ""]
    if reduction is not None:
        lines.append(f"Reduces to **{reduction}**.")
    if unmatched:
        # Named rather than silently dropped: a character with no value in this
        # table changes the sum by its absence, and hiding that is how a wrong
        # total looks right.
        lines.append(f"Ignored, having no value in this table: {' '.join(unmatched[:12])}")
    lines += [
        "",
        f"_{cipher}. Matches are only ever found inside one system._",
        "",
        footer(bot_url, site_url),
    ]
    return embed(f"“{data.get('text','')}”", "\n".join(lines),
                 url=f"{site_url}/tools/isopsephy")


def failure(message: str, bot_url: str, site_url: str) -> dict:
    """Something went wrong, said without blaming the person who asked."""
    return embed("Not this time", f"{message}\n\n{footer(bot_url, site_url)}")
