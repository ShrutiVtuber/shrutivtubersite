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
    # The daemon numbers all twenty-four continuously, so a night hour arrives
    # as 13–24. Printing that raw gives "the 13 hour of the night", which is
    # both ungrammatical and wrong — it is the first.
    raw = now.get("index", 0)
    night = bool(now.get("isNight"))
    index = raw - 12 if night and raw > 12 else raw
    part = "night" if night else "day"

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
    unmatched = data.get("unmatched") or []
    breakdown = " + ".join(f"{l['char']} {l['value']}" for l in letters[:24])
    if len(letters) > 24:
        breakdown += " …"

    reduction = (data.get("reduction") or {}).get("final")

    # Everything ignored and a total of nought is not an answer, it is a
    # mismatch between the text and the table. Saying "0" would be confidently
    # wrong, which is the one thing this site does not do.
    if letters == [] and unmatched:
        return embed(f"“{data.get('text','')}”", "\n".join([
            f"Nothing in that has a value in the **{cipher}** table.",
            "",
            f"Ignored: {' '.join(unmatched[:12])}",
            "",
            "Try a different script — each is summed by its own table and "
            "nothing converts between them.",
            "",
            footer(bot_url, site_url),
        ]), url=f"{site_url}/tools/isopsephy")

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


# ── the chart ───────────────────────────────────────────────────────────────

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# The same twelve divisions under the names the Vedic answer uses for them. The
# daemon names the rāśi on every body but not on the angles, so without this the
# placements read "Mithuna" and the ascendant three lines below reads "Gemini" —
# one chart apparently written in two vocabularies.
RASHI = ["Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā",
         "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"]

# The nodes, which the Hellenistic payload carries without dignities and the
# Vedic one names differently. Added here rather than into GLYPH above so the
# planetary-hour table above is not quietly given two rulers it does not have.
CHART_GLYPH = dict(GLYPH, **{"Rahu": f"☊{TEXT}", "Ketu": f"☋{TEXT}"})

# What the two traditions do NOT share. Written down because the difference is
# the point of the tool and not an implementation detail: a Hellenistic chart
# carries dignities, whole-sign places, sect and the lots; a Vedic one carries
# rāśi, nakṣatra, the lagna and a daśā. Neither carries both, and rendering a
# blank row for the half that is absent would suggest the tradition has an
# opinion it does not have.


def _dms(degrees: float) -> str:
    """Degrees and minutes. Nothing is rounded to a whole degree anywhere."""
    d = int(degrees)
    m = int(round((degrees - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}′"


def _sign_of(body: dict) -> tuple[str, float]:
    """
    The sign and the degree into it.

    Taken from the longitude when the payload does not name one — the nodes
    carry no dignities in the Hellenistic answer and NOTHING carries them in
    the Vedic one, so a `dignities`-only reading prints half a chart as blanks.
    """
    lon = float(body.get("longitude", 0.0)) % 360.0
    dign = body.get("dignities") or {}
    rashi = body.get("rashi") or {}
    if dign.get("sign"):
        return dign["sign"], float(dign.get("degree", lon % 30.0))
    if rashi.get("name"):
        return rashi["name"], float(rashi.get("degree", lon % 30.0))
    return SIGNS[int(lon // 30) % 12], lon % 30.0


def _table(bodies: list[dict]) -> str:
    """
    The placements, in a code block so the degrees line up.

    Monospace for the same reason the site sets `t-tabular` on every number it
    prints: a column of positions that does not align is a column nobody reads.
    """
    rows = []
    for b in bodies:
        sign, degree = _sign_of(b)
        mark = " ℞" if b.get("retrograde") else ""
        rows.append(f"{b.get('name',''):<9}{_dms(degree):>8}  {sign}{mark}")
    return "```\n" + "\n".join(rows) + "\n```"


def chart(data: dict, *, place, moment, tradition: str, time_unknown: bool,
          moon_range: tuple[str, str] | None, alternatives: list,
          bot_url: str, site_url: str) -> dict:
    """
    One chart, as a message.

    Three things are stated rather than assumed, and each of them is a way a
    chart can be quietly wrong for somebody who would never know:

      - THE PLACE IS SHOWN BACK, with its coordinates and the alternatives it
        beat. The site's place control does this with a "Not this place?"
        escape; a chat message has no such control, so the runners-up are named
        in the answer instead.
      - THE ZONE AND OFFSET ARE SHOWN BACK. A chart cast an hour out has every
        planet very nearly right and only the ascendant moved, so it does not
        look wrong — it looks like somebody else's.
      - AN UNKNOWN TIME WITHHOLDS THE ANGLES. The ascendant moves a degree
        every four minutes, so without a time it is not imprecise, it is
        undefined, and the houses, sect and lots that hang off it go with it.
    """
    bodies = data.get("bodies") or []
    angles = data.get("angles") or {}
    vedic = tradition == "vedic"

    sun = next((b for b in bodies if b.get("name") == "Sun"), None)
    moon = next((b for b in bodies if b.get("name") == "Moon"), None)

    head = []
    for body in (sun, moon):
        if body:
            sign, degree = _sign_of(body)
            head.append(f"{CHART_GLYPH.get(body['name'], '')} {_dms(degree)} {sign}")
    if not time_unknown and angles.get("ascendant") is not None:
        asc = float(angles["ascendant"]) % 360.0
        lagna = data.get("lagna") or {}
        name = lagna.get("name") or SIGNS[int(asc // 30) % 12]
        degree = float(lagna["degree"]) if lagna.get("degree") is not None else asc % 30.0
        head.append(f"AS {_dms(degree)} {name}")

    lines = [" · ".join(head), "", _table(bodies)]

    if time_unknown:
        # Named, not silently substituted. This is the whole reason the option
        # takes the word `unknown` rather than making somebody type a time they
        # do not have.
        lines += [
            "**No birth time given**, so the chart is cast for local noon.",
            "The ascendant, the houses, "
            + ("the lagna and the daśā" if vedic else "the sect and the lots")
            + " are **not given** — without a time they are undefined, not merely "
              "approximate.",
        ]
        if moon_range:
            lines.append(f"The Moon crossed **{moon_range[0]} → {moon_range[1]}** that day.")
        lines.append("")
    else:
        names = RASHI if vedic else SIGNS
        mc = angles.get("midheaven")
        if angles.get("ascendant") is not None:
            asc = float(angles["ascendant"]) % 360.0
            # The daemon gives the lagna its own name and degree; prefer them,
            # so the ascendant is worded exactly as the tradition words it.
            lagna = data.get("lagna") or {}
            label = "Lagna" if vedic else "Ascendant"
            sign = lagna.get("name") or names[int(asc // 30) % 12]
            degree = float(lagna["degree"]) if lagna.get("degree") is not None else asc % 30
            row = f"**{label}** {_dms(degree)} {sign}"
            if mc is not None:
                mc = float(mc) % 360.0
                row += f" · **Midheaven** {_dms(mc % 30)} {names[int(mc // 30) % 12]}"
            lines += [row, ""]

        if vedic:
            nak = data.get("nakshatraOfMoon") or {}
            if nak.get("name"):
                lines.append(
                    f"**Moon's nakṣatra** {nak['name']}"
                    + (f", pāda {nak['pada']}" if nak.get("pada") else "")
                    + (f" — lord {nak['lord']}" if nak.get("lord") else ""))
            dasha = data.get("dasha") or {}
            balance = dasha.get("balanceAtBirth") or {}
            if balance.get("lord"):
                lines.append(
                    f"**Daśā at birth** {balance['lord']}, "
                    f"{float(balance.get('years', 0)):.2f} years remaining "
                    f"({dasha.get('system', 'vimshottari')}).")
        else:
            sect = data.get("sect") or {}
            if sect:
                lines.append(
                    f"**A {'day' if sect.get('isDay') else 'night'} chart** — "
                    f"luminary {sect.get('luminary','—')}, "
                    f"benefic {sect.get('benefic','—')}, "
                    f"malefic {sect.get('malefic','—')}.")
            lots = data.get("lots") or {}
            if lots.get("Fortune") is not None:
                # Hellenistic only, so the tropical names are the right ones.
                fortune = float(lots["Fortune"]) % 360.0
                lines.append(
                    f"**Lot of Fortune** {_dms(fortune % 30)} "
                    f"{SIGNS[int(fortune // 30) % 12]}.")
        lines.append("")

    # The rule the numbers were reckoned under, in the tradition's own terms.
    ayanamsa = data.get("ayanamsa") or {}
    if vedic:
        rule = "Sidereal zodiac, graha dṛṣṭi"
        if ayanamsa.get("name"):
            rule += (f" · {str(ayanamsa['name']).title()} ayanāṃśa "
                     f"{_dms(float(ayanamsa.get('degrees', 0)))}")
    else:
        rule = "Tropical zodiac, whole-sign places"
    lines.append(f"_{rule}._")

    # Where, exactly, and under whose clock. Both halves shown back.
    zone = place.timezone or "UTC"
    stamp = f"{zone} ({moment.abbreviation}, {moment.offset})" if moment.abbreviation \
        else f"{zone} ({moment.offset})"
    lines.append(f"{SUBTEXT}{place.label} — {place.lat:.4f}, {place.lon:.4f} · {stamp}")

    if moment.note:
        lines.append(f"{SUBTEXT}⚠ {moment.note}")

    if alternatives:
        others = " · ".join(p.label for p in alternatives)
        lines.append(f"{SUBTEXT}Not this one? I also found: {others}")

    lines += ["", footer(bot_url, site_url)]

    when = moment.when[:16].replace("T", " ")
    title = f"{when} · {place.name}" if not time_unknown else f"{moment.when[:10]} · {place.name}"
    return embed(title, "\n".join(lines), url=f"{site_url}/tools/natal-chart")


# ── the manual ──────────────────────────────────────────────────────────────

# Roughly what fits a Discord code block on a phone without wrapping in the
# middle of a word. Wider reads fine on a desktop and badly everywhere else.
WIDTH = 68


def _entry(command: dict) -> str:
    """
    One command, in the shape of a man page and about a tenth the length.

    NAME, then SYNOPSIS, then an example, then the one thing worth knowing
    before you run it. Everything comes off the command's own definition, so a
    command that gains an option and forgets to document it is the only way
    this can go stale — and that is visible in the synopsis, not hidden.
    """
    import textwrap

    out = [command["name"].upper()]
    out += textwrap.wrap(command.get("description", ""), WIDTH - 4,
                         initial_indent="    ", subsequent_indent="    ")
    out.append("")

    usage = command.get("usage") or f"/{command['name']}"
    for line in ([usage] if isinstance(usage, str) else usage):
        for part in line.split("\n"):
            out.append(f"    {part}")
    out.append("")

    if command.get("example"):
        out.append(f"    e.g.  {command['example']}")
    if command.get("summary"):
        out.append("")
        out += textwrap.wrap(command["summary"], WIDTH - 4,
                             initial_indent="    ", subsequent_indent="    ")
    return "\n".join(out)


def manual(commands: list[dict], bot_url: str, site_url: str,
           only: str = "") -> dict:
    """
    What the bot can be asked.

    Generated from the command list itself rather than written out beside it.
    A second copy would be wrong the first time a command changed, and wrong in
    the way documentation always goes wrong: still there, still confident.
    """
    chosen = [c for c in commands if not only or c["name"] == only]
    if not chosen:
        known = ", ".join(f"`/{c['name']}`" for c in commands)
        return embed("No such command", "\n".join([
            f"There is no `/{only}`. What there is: {known}.",
            "",
            footer(bot_url, site_url),
        ]))

    body = "\n\n".join(_entry(c) for c in chosen)
    lines = [f"```\n{body}\n```"]
    if not only:
        lines.append("`/help command:<name>` for one of them on its own.")
    lines += ["", footer(bot_url, site_url)]
    return embed("vcordbot" if not only else f"/{only}", "\n".join(lines),
                 url=f"{site_url}/tools")
