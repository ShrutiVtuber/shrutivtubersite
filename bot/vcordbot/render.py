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


ZODIAC = (
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
)


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


def horoscope_material(
    events: dict, *, sign: str, period_label: str, start: str, end: str,
    bot_url: str, site_url: str,
) -> dict:
    """
    What to write a horoscope FROM — not a horoscope.

    ⚠ This says nothing about what the sky means. It is the same material the
    writing desk on the site puts beside the box: the events inside the period,
    and which house each falls in from the given rising sign. The interpretation
    is the person's, which is the whole point of a practice room.
    """
    rising = sign.title()
    inside = [
        e for e in (events.get("events") or [])
        if e.get("kind") in ("ingress", "station", "lunation", "eclipse")
    ]

    def house_of(where: str) -> int:
        """Whole sign, counted from the rising sign — one, not zero."""
        try:
            return (ZODIAC.index(where.lower()) - ZODIAC.index(sign.lower())) % 12 + 1
        except ValueError:
            return 0

    lines = []
    for e in inside[:24]:
        when = _stamp(e.get("at", ""))
        who = " & ".join(e.get("bodies") or []) or "—"
        where = e.get("sign", "")
        detail = e.get("detail") or {}
        if e["kind"] == "ingress":
            what = f"{who} enters {where}"
        elif e["kind"] == "station":
            what = f"{who} turns {detail.get('direction', 'station')}"
        elif e["kind"] == "lunation":
            what = f"{detail.get('phase', 'lunation')} moon in {where}"
        else:
            what = f"{detail.get('type', '')} {detail.get('of', '')} eclipse in {where}".strip()
        house = house_of(where)
        lines.append(f"`{when}` {what}" + (f" — **{house}th**" if house else ""))

    if not lines:
        # A quiet period is a real answer and worth saying so, because it reads
        # differently from a loud one and that is itself something to write.
        lines = [
            "Nothing ingresses, stations or lunates inside this period.",
            "",
            "That is not nothing to write about — a quiet week reads differently "
            "from a loud one.",
        ]

    body = "\n".join([
        f"**{rising} rising** · {period_label}",
        f"{start} to {end}",
        "",
        *lines,
        "",
        "Houses are whole sign, counted from the rising sign.",
        "",
        footer(bot_url, site_url),
    ])
    return embed(
        f"To write from · {rising} · {period_label}", body,
        url=f"{site_url}/tools/horoscope-writing?sign={sign}",
    )


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

# Discord refuses an embed whose description passes 4096 characters — the whole
# message fails, it is not truncated. Ten commands come to about 2700, so this
# is not close today and would be crossed by roughly five more without anything
# warning first, which is exactly the kind of limit that is discovered by a
# user. Below the cap the manual is full; above it, it lists.
DESCRIPTION_LIMIT = 4096
ROOM = 3600


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

    if len(body) > ROOM and not only:
        # Too many to print in full. A short list plus a way to ask for one is
        # a worse manual than the full one and a far better one than an embed
        # Discord refuses to deliver at all.
        body = "\n".join(
            f"{c['name']:<11} {c.get('description', '')[:WIDTH - 12]}"
            for c in chosen)

    lines = [f"```\n{body}\n```"]
    if not only:
        lines.append("`/help command:<name>` for one of them on its own.")
    lines += ["", footer(bot_url, site_url)]
    return embed("vcordbot" if not only else f"/{only}", "\n".join(lines),
                 url=f"{site_url}/tools")


# ── the rest of the instruments ─────────────────────────────────────────────

def _in(iso: str) -> str:
    """
    "in about four hours", in the reader's own reckoning of the clock.

    Relative rather than absolute because every limb of the pañcāṅga ends at
    some point that is usually today and occasionally tomorrow, and an absolute
    time of day is ambiguous about which — while a relative one never is.
    """
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return iso
    return f"<t:{int(dt.astimezone(timezone.utc).timestamp())}:R>"


def _limb(label: str, part: dict) -> str:
    """One limb, its name, and when it gives way to the next."""
    name = part.get("name", "—")
    line = f"**{label}** {name}"
    if part.get("ruler"):
        line += f" — {part['ruler']}"
    if part.get("endsAt"):
        line += f", until {_in(part['endsAt'])}"
    return line


def panchanga(data: dict, place: str, bot_url: str, site_url: str) -> dict:
    """
    The five limbs, each with the moment it ends.

    A pañcāṅga is not a date, it is five overlapping divisions that begin and
    end at different times of day — so a limb without its end is half the fact.
    Reckoned from SUNRISE where the person asked, not from midnight and not
    from here, which is the whole reason the command takes a place.
    """
    lines = [
        _limb("Vāra", data.get("vara") or {}),
        _limb("Tithi", data.get("tithi") or {}),
        _limb("Nakṣatra", data.get("nakshatra") or {}),
        _limb("Yoga", data.get("yoga") or {}),
        _limb("Karaṇa", data.get("karana") or {}),
        "",
        f"Sunrise {_stamp(data.get('sunrise',''))} — the day is reckoned from there, not from midnight.",
    ]

    absent = data.get("undefined") or []
    if absent:
        # Named rather than omitted. A limb that cannot be reckoned somewhere
        # is a fact about the place, and hiding it reads as it having no value.
        lines.append(f"Not reckonable here: {', '.join(str(a) for a in absent)}.")

    ayanamsa = data.get("ayanamsa") or {}
    if ayanamsa.get("name"):
        lines += ["", f"_{str(ayanamsa['name']).title()} ayanāṃśa, "
                      f"{_dms(float(ayanamsa.get('degrees', 0)))}. "
                      f"A different one can move a nakṣatra boundary._"]
    lines += ["", footer(bot_url, site_url)]
    return embed(f"Pañcāṅga · {place}", "\n".join(lines),
                 url=f"{site_url}/tools/panchanga")


def attic(data: dict, bot_url: str, site_url: str) -> dict:
    """
    The Athenian calendar for one day.

    Athens is not a default here and is not offered as an option: it is that
    city's calendar, and reckoning it from somewhere else would be a different
    calendar rather than the same one seen from further away.
    """
    month = data.get("month") or {}
    day = data.get("day") or {}

    name = month.get("name", "—")
    greek = month.get("greek", "")
    header = f"**{name}**" + (f" · {greek}" if greek else "")
    if month.get("intercalary"):
        # A repeated month, inserted to keep the calendar with the moon. Worth
        # saying: it is why the same month name can occur twice in one year.
        header += " — intercalary, the month repeated"

    lines = [
        header,
        f"Day **{day.get('number','—')}** of {month.get('length','—')}"
        + (f" — {day.get('greek','')} ({day.get('transliteration','')})"
           if day.get("greek") else ""),
    ]
    if day.get("decad"):
        lines.append(f"In the {day['decad']} decad · {day.get('remaining','—')} days remain.")
    lines += [
        "",
        f"The moon is **{data.get('moonAgeDays','—')} days** old.",
        f"Next noumenia — the next new month — **{data.get('nextNoumenia','—')}**.",
    ]

    # The key is `used`. Read as `name`/`note` it silently rendered nothing,
    # which dropped the one line that says which of two disagreeing rules
    # produced the date above it.
    used = (data.get("reckoning") or {}).get("used", "")
    if used:
        lines += ["", f"_{used.title()} reckoning — a month opens at "
                      + ("the astronomical new moon"
                         if used == "conjunction" else
                         "the first crescent somebody could see")
                      + ". The other opens half the months of a year on a "
                        "different day._"]

    lines += ["", footer(bot_url, site_url)]
    return embed(f"Attic calendar · {data.get('gregorian','')}", "\n".join(lines),
                 url=f"{site_url}/tools/attic-calendar")


def hindu(data: dict, place: str, bot_url: str, site_url: str) -> dict:
    """
    The Hindu calendar date, under the reckoning that was asked for.

    The two reckonings genuinely disagree about which month it is for half of
    every month, so the one in use is named rather than left as an assumption.
    Neither is the correction of the other.
    """
    years = data.get("years") or {}
    month = data.get("month") or {}
    tithi = data.get("tithi") or {}

    name = month.get("name", "—")
    if month.get("adhika"):
        name += " (adhika — the intercalary repeat of it)"
    if month.get("kshaya"):
        name += " (kṣaya — the month skipped)"

    lines = [
        f"**{name}**, {data.get('paksha','—')} pakṣa",
        f"**{tithi.get('name','—')}**",
        "",
        f"Vikrama **{years.get('vikrama','—')}** · "
        f"Śaka **{years.get('shaka','—')}** · "
        f"Kali **{years.get('kali','—')}**",
    ]

    lunation = data.get("lunation") or {}
    if lunation.get("end"):
        lines += ["", f"This lunation ends {_in(lunation['end'])}."]

    reckoning = data.get("reckoning", "amanta")
    lines += [
        "",
        f"_{reckoning.title()} reckoning — the month ends at the "
        f"{'new' if reckoning == 'amanta' else 'full'} moon. "
        f"The other names this month differently for half of every month, and "
        f"is not a correction of it._",
    ]
    if data.get("authority"):
        lines.append(f"_Computed by {data['authority']}._")
    lines += ["", footer(bot_url, site_url)]
    return embed(f"Hindu calendar · {place}", "\n".join(lines),
                 url=f"{site_url}/tools/hindu-calendar")


def sigil(data: dict, bot_url: str, site_url: str) -> dict:
    """
    The reduction, step by step, and where the drawing lives.

    The figure is a 512-pixel SVG and a chat client will not render one, so the
    steps are the answer here and the drawing is a link. Saying that plainly
    beats posting a broken image and hoping.
    """
    steps = data.get("steps") or []
    lines = []
    for step in steps:
        line = f"**{step.get('label','')}** — `{step.get('value','')}`"
        if step.get("note"):
            line += f"  _{step['note']}_"
        lines.append(line)

    lines += [
        "",
        f"**{data.get('pointCount','—')} points**, drawn through "
        f"`{data.get('letters','')}` in order.",
    ]
    if data.get("exhausted"):
        # The method ran out of letters before it ran out of figure. Said,
        # because the result is then not what the method promises.
        lines.append(f"_{data.get('exhaustedReason') or 'The letters ran out before the figure did.'}_")
    lines += [
        "",
        f"[Draw it on the site]({site_url}/tools/sigil-generator) — the figure "
        "is an image, and this is a chat window.",
        "",
        footer(bot_url, site_url),
    ]
    return embed("Sigil", "\n".join(lines), url=f"{site_url}/tools/sigil-generator")


def stations(data: dict, place: str, bot_url: str, site_url: str) -> dict:
    """
    Today's stations, including the ones that do not happen.

    **An absent station is an answer.** A polar summer has no sunrise, and
    printing nothing there would read as a failure to compute rather than as
    the fact it is. The daemon gives a reason; it is passed on.
    """
    table = data.get("table") or []
    today = (table[0] if table else {}) or {}
    rows = today.get("stations") or []

    lines = []
    for s in rows:
        name = str(s.get("name", "")).replace("_", " ")
        if s.get("occurred"):
            line = f"**{name.title()}** {_stamp(s.get('at',''))}"
            if s.get("dedication"):
                line += f" — {s['dedication']}"
        else:
            line = (f"**{name.title()}** — does not occur"
                    + (f": {s['absentReason']}" if s.get("absentReason") else ""))
        lines.append(line)

    if not rows:
        lines.append("Nothing to report for that body today.")

    lines += [
        "",
        f"_{str(data.get('body','sun')).title()}, for {today.get('date','today')}._",
        "",
        footer(bot_url, site_url),
    ]
    return embed(f"Stations · {place}", "\n".join(lines),
                 url=f"{site_url}/tools/stations")
