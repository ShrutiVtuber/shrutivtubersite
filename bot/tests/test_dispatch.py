# SPDX-License-Identifier: AGPL-3.0-only
"""
Every command, answered, without Discord being involved at all.

The ephemeris is a stand-in here. What is under test is the bot's own
behaviour: what it does with an empty argument, an enormous one, an ephemeris
that will not answer, and a command it has never heard of.
"""
from __future__ import annotations

import asyncio

from vcordbot import dispatch as D
from vcordbot.astro import AstroError

BOT, SITE = "https://bot.example.test", "https://site.example.test"
NOW = "2026-08-26T12:00:00+03:00"


class FakeAstro:
    """Answers like the daemon does, or refuses on command."""

    def __init__(self, *, fail: str | None = None) -> None:
        self.fail = fail
        self.calls: list[tuple] = []

    async def planetary_hours(self, when, lat, lon):
        self.calls.append(("hours", when, lat, lon))
        if self.fail:
            raise AstroError(self.fail)
        return {"current": {"index": 5, "ruler": "Mars", "isNight": False,
                            "endsAt": "2026-08-26T09:20:25+00:00"},
                "sunrise": "2026-08-26T03:49:25+00:00",
                "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Mercury"}

    async def isopsephy(self, text, cipher="greek-iso"):
        self.calls.append(("iso", text, cipher))
        if self.fail:
            raise AstroError(self.fail)
        return {"text": text, "total": 373, "cipher": {"name": "Isopsephy"},
                "letters": [{"char": "λ", "value": 30}],
                "reduction": {"final": 4}, "unmatched": []}

    # The rest of the instruments, shaped as the daemon actually answers them.
    # Copied from real responses rather than invented: the Vedic chart taught
    # this suite that a made-up payload agrees with whatever the code already
    # does, including where the code is wrong.

    async def panchanga(self, when, lat, lon):
        self.calls.append(("panchanga", when, lat, lon))
        if self.fail:
            raise AstroError(self.fail)
        return {"sunrise": "2026-08-28T03:55:41+00:00",
                "ayanamsa": {"name": "lahiri", "degrees": 24.232106},
                "vara": {"name": "Śukravāra", "ruler": "Venus"},
                "tithi": {"name": "Kṛṣṇa Pratipadā", "endsAt": "2026-08-29T04:27:25+00:00"},
                "nakshatra": {"name": "Śatabhiṣā", "endsAt": "2026-08-28T21:43:27+00:00"},
                "yoga": {"name": "Sukarman", "endsAt": "2026-08-29T01:06:23+00:00"},
                "karana": {"name": "Bālava", "endsAt": "2026-08-28T16:26:42+00:00"},
                "undefined": []}

    async def attic(self, when, reckoning="conjunction"):
        self.calls.append(("attic", when, reckoning))
        if self.fail:
            raise AstroError(self.fail)
        return {"gregorian": "2026-08-28",
                "month": {"name": "Metageitnion", "greek": "Μεταγειτνιών",
                          "length": 30, "intercalary": False},
                "day": {"number": 16, "greek": "16 ἐπὶ δέκα",
                        "transliteration": "16 epi deka",
                        "decad": "μεσοῦντος", "remaining": 15},
                "moonAgeDays": 15.077, "nextNoumenia": "2026-09-12",
                # The daemon's key is `used`, not `name` or `note`.
                "reckoning": {"used": reckoning, "note": None}}

    async def hindu(self, when, lat, lon, reckoning="amanta"):
        self.calls.append(("hindu", when, lat, lon, reckoning))
        if self.fail:
            raise AstroError(self.fail)
        # The two reckonings genuinely name a different month for the same day.
        return {"reckoning": reckoning, "authority": "drik",
                "years": {"vikrama": 2083, "shaka": 1948, "kali": 5127},
                "month": {"name": "Śrāvaṇa" if reckoning == "amanta" else "Bhādrapada",
                          "adhika": False, "kshaya": False},
                "paksha": "Kṛṣṇa",
                "tithi": {"name": "Kṛṣṇa Pratipadā"},
                "lunation": {"end": "2026-09-11T03:27:01+00:00"}}

    async def sigil(self, statement):
        self.calls.append(("sigil", statement))
        if self.fail:
            raise AstroError(self.fail)
        return {"steps": [{"label": "Statement of intent", "value": statement, "note": ""},
                          {"label": "Vowels struck", "value": "CLRTY", "note": "removed: AIU"}],
                "letters": "CDLNRSTY", "pointCount": 8,
                "exhausted": False, "exhaustedReason": ""}

    async def stations(self, body, when, lat, lon):
        self.calls.append(("stations", body, when, lat, lon))
        if self.fail:
            raise AstroError(self.fail)
        return {"body": body,
                "table": [{"date": "2026-08-28", "stations": [
                    {"name": "sunrise", "at": "2026-08-28T03:51:08+00:00",
                     "occurred": True, "absentReason": "", "dedication": ""},
                    {"name": "sunset", "at": "2026-08-28T17:03:48+00:00",
                     "occurred": True, "absentReason": "", "dedication": ""},
                    # A station that does not happen is an answer, not a gap.
                    {"name": "civil_dawn", "at": "", "occurred": False,
                     "absentReason": "the Sun does not reach that depth here today",
                     "dedication": ""},
                ]}]}


def cmd(name, **options):
    return {"type": D.APPLICATION_COMMAND,
            "data": {"name": name,
                     "options": [{"name": k, "value": v} for k, v in options.items()]}}


def run(interaction, astro=None):
    """
    Drive one interaction to completion.

    Synchronous on purpose: `pytest-asyncio` would be a plugin dependency for
    the sake of a decorator, and a test suite that needs a plugin to run is one
    more thing standing between somebody and finding out whether the bot works.
    """
    return asyncio.run(D.dispatch(interaction, astro or FakeAstro(),
                                  bot_url=BOT, site_url=SITE, now_iso=NOW))


def test_ping_is_answered_with_pong() -> None:
    """
    The whole handshake. Discord sends this when the endpoint URL is saved and
    periodically after; get it wrong and the URL cannot even be set.
    """
    assert run({"type": D.PING}) == {"type": D.PONG}


def test_the_hour_answers_publicly() -> None:
    r = run(cmd("hour"))
    assert r["type"] == D.CHANNEL_MESSAGE
    assert "Mars" in r["data"]["embeds"][0]["description"]
    # Not ephemeral: the whole point is that a channel sees it.
    assert "flags" not in r["data"]


def test_isopsephy_passes_the_cipher_slug_through() -> None:
    """
    The daemon takes a cipher SLUG. It was sent a language name once, ignored
    it, fell back to Greek, and returned a confident total with every Hebrew
    letter unmatched — a wrong answer that looked entirely right.
    """
    a = FakeAstro()
    run(cmd("isopsephy", text="אמת", script="heb-hechrachi"), a)
    assert a.calls == [("iso", "אמת", "heb-hechrachi")]


def test_isopsephy_defaults_to_greek() -> None:
    a = FakeAstro()
    run(cmd("isopsephy", text="ΛΟΓΟΣ"), a)
    assert a.calls[0][2] == "greek-iso"


def test_every_offered_cipher_is_a_slug_the_daemon_knows() -> None:
    """
    The choices in the picker are sent verbatim as the cipher. A friendly
    language name among them would be silently ignored by the daemon and
    answered in Greek, which is how this broke the first time.
    """
    from vcordbot.commands import COMMANDS
    iso = next(c for c in COMMANDS if c["name"] == "isopsephy")
    script = next(o for o in iso["options"] if o["name"] == "script")
    for choice in script["choices"]:
        assert "-" in choice["value"], (
            f"{choice['value']!r} is not a cipher slug — the daemon takes "
            f"slugs like 'heb-hechrachi', not language names")


def test_an_empty_word_is_refused_before_the_ephemeris() -> None:
    a = FakeAstro()
    r = run(cmd("isopsephy", text="   "), a)
    assert a.calls == [], "nothing should have been asked"
    assert r["data"]["flags"] == D.EPHEMERAL, "a scolding should be private"


def test_a_paste_is_refused_by_us_not_by_the_ephemeris() -> None:
    """Our limit, so the message is ours and predictable."""
    a = FakeAstro()
    r = run(cmd("isopsephy", text="α" * 500), a)
    assert a.calls == []
    assert "two hundred" in r["data"]["embeds"][0]["description"]


def test_an_ephemeris_failure_is_shown_privately_and_kindly() -> None:
    r = run(cmd("hour"), FakeAstro(fail="The ephemeris took too long to answer."))
    body = r["data"]["embeds"][0]["description"]
    assert r["data"]["flags"] == D.EPHEMERAL
    assert "took too long" in body

    # Only the message itself. The footer below it carries links by design, and
    # an earlier version of this test split on the wrong side of them and
    # failed the code for the footer doing its job.
    from vcordbot import render
    said = body.split(render.SUBTEXT)[0]
    assert "Traceback" not in said
    assert "http" not in said, "an internal hostname must not reach a stranger's channel"


def test_an_unknown_command_does_not_raise() -> None:
    r = run(cmd("summon"))
    assert r["type"] == D.CHANNEL_MESSAGE
    assert r["data"]["flags"] == D.EPHEMERAL


def test_every_registered_command_is_actually_implemented() -> None:
    """
    The failure this catches: a command registered with Discord, visible in the
    picker, and answering "I do not have that command" — which looks like a
    broken bot to everyone but us.
    """
    from vcordbot.commands import COMMANDS
    for c in COMMANDS:
        required = {o["name"]: "ΛΟΓΟΣ" for o in c.get("options", []) if o.get("required")}
        r = run(cmd(c["name"], **required))
        body = r["data"]["embeds"][0]["description"]
        assert "I do not have that command" not in body, f"/{c['name']} is not implemented"


def test_every_answer_carries_the_footer() -> None:
    from vcordbot import render
    for interaction in (cmd("hour"), cmd("isopsephy", text="ΛΟΓΟΣ"), cmd("nope")):
        r = run(interaction)
        assert render.footer(BOT, SITE) in r["data"]["embeds"][0]["description"]


# ── the chart ───────────────────────────────────────────────────────────────

import pytest                                                       # noqa: E402

from vcordbot import commands as C, places as P                     # noqa: E402

ATHENS_PLACE = P.Place("Athens", "Attica", "Greece", "GR", 37.9838, 23.7275,
                       90.0, "Europe/Athens", 664046)

HELLENIC = {
    "tradition": "hellenistic", "zodiac": "tropical",
    "angles": {"ascendant": 138.513877, "midheaven": 41.058453},
    "sect": {"isDay": True, "luminary": "Sun", "benefic": "Jupiter",
             "malefic": "Saturn"},
    "lots": {"Fortune": 101.598692},
    "bodies": [
        {"name": "Sun", "longitude": 53.861797, "retrograde": False,
         "dignities": {"sign": "Taurus", "degree": 23.8618}},
        {"name": "Moon", "longitude": 355.2, "retrograde": False,
         "dignities": {"sign": "Pisces", "degree": 25.2}},
        # No dignities, exactly as the daemon sends the nodes.
        {"name": "Rahu", "longitude": 200.5, "retrograde": True},
    ],
}

VEDIC = {
    "tradition": "vedic", "zodiac": "sidereal",
    "ayanamsa": {"name": "lahiri", "degrees": 23.807291},
    "angles": {"ascendant": 77.952913, "midheaven": 329.123765},
    "lagna": {"index": 3, "name": "Mithuna", "degree": 17.9529},
    "nakshatraOfMoon": {"name": "Revatī", "pada": 2, "lord": "Mercury"},
    "dasha": {"system": "vimshottari",
              "balanceAtBirth": {"lord": "Mercury", "years": 10.8539}},
    # NOTHING carries dignities in this tradition.
    "bodies": [
        {"name": "Sun", "longitude": 29.933906, "retrograde": False,
         "rashi": {"index": 1, "name": "Meṣa", "degree": 29.9339}},
        {"name": "Moon", "longitude": 340.1, "retrograde": False,
         "rashi": {"index": 12, "name": "Mīna", "degree": 10.1}},
    ],
}


class ChartAstro(FakeAstro):
    """The ephemeris, answering /chart in whichever tradition was asked for."""

    async def chart(self, when, lat, lon, *, tradition="hellenistic",
                    house_system="whole_sign"):
        self.calls.append(("chart", when, lat, lon, tradition))
        if self.fail:
            raise AstroError(self.fail)
        return dict(VEDIC if tradition == "vedic" else HELLENIC)


BIRTH = {"date": "1996-05-14", "time": "09:30",
         "city": "Athens", "country": "Greece"}


def chart_cmd(monkeypatch, astro=None, **options):
    """One /chart, with the gazetteer stood in for."""
    async def fake_find(city, country="", region="", client=None):
        return ATHENS_PLACE, []
    monkeypatch.setattr(D.places, "find", fake_find)
    return run(cmd("chart", **options), astro or ChartAstro())


def test_a_chart_is_ephemeral_unless_it_is_shared(monkeypatch) -> None:
    """
    A chart IS birth data — the ascendant gives the time of day to within a few
    minutes. It must not land in a shared channel because somebody forgot a
    flag.
    """
    private = chart_cmd(monkeypatch, None, **BIRTH)
    assert private["data"]["flags"] == D.EPHEMERAL

    public = chart_cmd(monkeypatch, None, **BIRTH, share=True)
    assert "flags" not in public["data"]


def test_the_ephemeris_is_sent_the_local_offset_not_a_bare_clock(monkeypatch) -> None:
    """
    THE bug this command exists to avoid. The daemon reads a naive datetime as
    UTC, so `09:30` for a birth in Athens means half past twelve there — every
    planet very nearly right and the ascendant forty-five degrees out.
    """
    astro = ChartAstro()
    chart_cmd(monkeypatch, astro, **BIRTH)
    assert astro.calls == [("chart", "1996-05-14T09:30:00+03:00",
                            37.9838, 23.7275, "hellenistic")]


def test_the_ephemeris_refuses_a_moment_with_no_offset() -> None:
    """Belt and braces: the guard lives in the client, not only in the caller."""
    from vcordbot.astro import Astro
    with pytest.raises(AstroError):
        asyncio.run(Astro("http://nowhere.invalid").chart(
            "1996-05-14T09:30:00", 0, 0))


def test_vedic_renders_what_only_vedic_has(monkeypatch) -> None:
    """
    Neither tradition carries the other's half. A Vedic chart has no dignities
    at all, so a `dignities`-only reading prints every position as a blank.
    """
    r = chart_cmd(monkeypatch, None, **BIRTH, tradition="vedic")
    said = r["data"]["embeds"][0]["description"]
    assert "Meṣa" in said                       # the rāśi, not "Taurus"
    assert "Revatī" in said                     # the Moon's nakṣatra
    assert "Mithuna" in said                    # the lagna
    assert "Sidereal" in said
    assert "day chart" not in said              # which this tradition has not


def test_hellenic_renders_what_only_hellenic_has(monkeypatch) -> None:
    said = chart_cmd(monkeypatch, None, **BIRTH)["data"]["embeds"][0]["description"]
    assert "day chart" in said
    assert "Lot of Fortune" in said
    assert "Tropical" in said
    assert "nakṣatra" not in said


def test_a_node_without_dignities_still_gets_a_sign(monkeypatch) -> None:
    """Rahu comes with no dignities. It must not print as an empty row."""
    said = chart_cmd(monkeypatch, None, **BIRTH)["data"]["embeds"][0]["description"]
    assert "Rahu" in said and "Libra" in said


def test_the_place_and_the_clock_are_shown_back(monkeypatch) -> None:
    """
    Both are ways the answer can be quietly wrong for somebody who would never
    know, so both are printed rather than assumed.
    """
    said = chart_cmd(monkeypatch, None, **BIRTH)["data"]["embeds"][0]["description"]
    assert "Athens, Attica, Greece" in said
    assert "37.9838" in said
    assert "Europe/Athens" in said and "+03:00" in said


def test_an_unknown_time_withholds_the_angles(monkeypatch) -> None:
    """
    Without a time the ascendant is not imprecise, it is undefined — and the
    houses, sect and lots that hang off it go with it.
    """
    r = chart_cmd(monkeypatch, None, **dict(BIRTH, time="unknown"))
    said = r["data"]["embeds"][0]["description"]
    assert "No birth time given" in said
    assert "not given" in said
    assert "Ascendant" not in said


def test_a_twelve_hour_time_is_caught_by_name(monkeypatch) -> None:
    """
    `9:30 pm` read as 24-hour is half past nine in the morning — twelve hours
    and a different chart away.
    """
    r = chart_cmd(monkeypatch, None, **dict(BIRTH, time="9:30 pm"))
    assert "24-hour" in r["data"]["embeds"][0]["description"]
    assert r["data"]["flags"] == D.EPHEMERAL


def test_an_ambiguous_date_is_refused_rather_than_guessed(monkeypatch) -> None:
    r = chart_cmd(monkeypatch, None, **dict(BIRTH, date="05/14/1996"))
    assert "YYYY-MM-DD" in r["data"]["embeds"][0]["description"]


def test_a_city_that_cannot_be_found_says_so_privately(monkeypatch) -> None:
    async def missing(city, country="", region="", client=None):
        raise P.PlaceError("I could not find **Nowhereton**.")
    monkeypatch.setattr(D.places, "find", missing)
    r = run(cmd("chart", **dict(BIRTH, city="Nowhereton")), ChartAstro())
    assert "Nowhereton" in r["data"]["embeds"][0]["description"]
    assert r["data"]["flags"] == D.EPHEMERAL


def test_a_chart_is_deferred_because_it_cannot_answer_in_three_seconds() -> None:
    """
    Too few names here and the interaction times out and the person loses what
    they typed; too many and a fast answer arrives as an edit.
    """
    assert "chart" in C.DEFERRED
    assert "help" not in C.DEFERRED


# ── the manual ──────────────────────────────────────────────────────────────


def test_help_lists_every_command_that_exists() -> None:
    said = run(cmd("help"))["data"]["embeds"][0]["description"]
    for name in C.NAMES:
        assert name.upper() in said, name


def test_help_gives_syntax_and_an_example_for_each() -> None:
    said = run(cmd("help"))["data"]["embeds"][0]["description"]
    assert "/chart date:<YYYY-MM-DD>" in said
    assert "e.g.  /chart date:1996-05-14 time:09:30 city:Athens country:Greece" in said


def test_help_can_be_asked_about_one_command() -> None:
    r = run(cmd("help", command="chart"))
    said = r["data"]["embeds"][0]["description"]
    assert "CHART" in said and "ISOPSEPHY" not in said
    assert r["data"]["flags"] == D.EPHEMERAL


def test_help_about_a_command_that_does_not_exist_says_what_does() -> None:
    said = run(cmd("help", command="nonesuch"))["data"]["embeds"][0]["description"]
    assert "no `/nonesuch`" in said and "/chart" in said


def test_the_help_keys_never_reach_discord() -> None:
    """
    Discord validates this payload strictly: an unknown key is a rejected PUT,
    not a warning, and the whole command list fails to register with it.
    """
    def keys(node, found):
        if isinstance(node, dict):
            found.update(node)
            for v in node.values():
                keys(v, found)
        elif isinstance(node, list):
            for v in node:
                keys(v, found)
        return found

    sent = keys(C.for_discord(), set())
    assert not sent & set(C.OURS)
    # And the help still has them to work from.
    assert all(c.get("usage") for c in C.COMMANDS)


# ── the rest of the instruments ─────────────────────────────────────────────

TOKYO = P.Place("Tokyo", "Tokyo", "Japan", "JP", 35.6895, 139.6917, 40.0,
                "Asia/Tokyo", 8336599)


def with_place(monkeypatch, name, astro=None, **options):
    """One command, with the gazetteer stood in for."""
    async def fake_lookup(text, client=None):
        return TOKYO, []
    monkeypatch.setattr(D.places, "lookup", fake_lookup)
    return run(cmd(name, **options), astro or ChartAstro())


def test_hour_actually_uses_the_place_it_was_given(monkeypatch) -> None:
    """
    THE bug. `place` was declared, registered, shown in the picker — and read
    by nothing. The handler took Athens whatever was typed and titled the
    answer "Athens" to match, so asking for Tokyo did not fail, it lied.
    """
    astro = ChartAstro()
    r = with_place(monkeypatch, "hour", astro, place="Tokyo, Japan")
    assert astro.calls[0][2:4] == (35.6895, 139.6917), astro.calls
    assert "Tokyo" in r["data"]["embeds"][0]["title"]


def test_hour_without_a_place_is_still_athens(monkeypatch) -> None:
    astro = ChartAstro()
    with_place(monkeypatch, "hour", astro)
    assert astro.calls[0][2:4] == (D.ATHENS.lat, D.ATHENS.lon)


def test_a_free_text_place_is_read_city_first_country_last() -> None:
    """`Springfield, IL, USA` — the order every postal address agrees on."""
    seen = {}

    async def fake_find(city, country="", region="", client=None):
        seen.update(city=city, country=country, region=region)
        return TOKYO, []

    import vcordbot.places as real
    original, real.find = real.find, fake_find
    try:
        asyncio.run(real.lookup("Springfield, IL, USA"))
    finally:
        real.find = original
    assert seen == {"city": "Springfield", "region": "IL", "country": "USA"}


def test_panchanga_gives_every_limb_with_its_ending(monkeypatch) -> None:
    """
    A limb without its end is half the fact: these are five overlapping
    divisions that begin and end at different times of day, not a date.
    """
    said = with_place(monkeypatch, "panchanga")["data"]["embeds"][0]["description"]
    for limb in ("Vāra", "Tithi", "Nakṣatra", "Yoga", "Karaṇa"):
        assert limb in said, limb
    assert said.count("until <t:") == 4          # vāra alone has no end
    assert "reckoned from there, not from midnight" in said


def test_attic_refuses_an_ambiguous_date(monkeypatch) -> None:
    r = with_place(monkeypatch, "attic", date="08/28/2026")
    assert "YYYY-MM-DD" in r["data"]["embeds"][0]["description"]


def test_attic_is_athens_and_does_not_offer_otherwise() -> None:
    """
    Not a default: it is that city's calendar. Reckoned from elsewhere it
    would be a different calendar, not the same one seen from further away.
    """
    attic = next(c for c in C.COMMANDS if c["name"] == "attic")
    assert not any(o["name"] == "place" for o in attic["options"])


def test_hindu_passes_the_reckoning_through(monkeypatch) -> None:
    """
    Amānta and pūrṇimānta name a different month for the same day, for half of
    every month. Sending the wrong one answers a question nobody asked.
    """
    astro = ChartAstro()
    with_place(monkeypatch, "hindu", astro, reckoning="purnimanta")
    assert astro.calls[0][4] == "purnimanta"

    said = with_place(monkeypatch, "hindu", ChartAstro(),
                      reckoning="purnimanta")["data"]["embeds"][0]["description"]
    assert "Bhādrapada" in said
    assert "not a correction of it" in said


def test_hindu_defaults_to_amanta(monkeypatch) -> None:
    astro = ChartAstro()
    with_place(monkeypatch, "hindu", astro)
    assert astro.calls[0][4] == "amanta"


def test_sigil_shows_the_reduction_and_links_the_drawing(monkeypatch) -> None:
    """A 512px SVG will not render in a chat client. Say so, do not try."""
    said = with_place(monkeypatch, "sigil",
                      statement="clarity in study")["data"]["embeds"][0]["description"]
    assert "Statement of intent" in said and "Vowels struck" in said
    assert "8 points" in said
    assert "/tools/sigil-generator" in said


def test_stations_reports_the_ones_that_do_not_happen(monkeypatch) -> None:
    """
    A polar summer has no sunrise. Printing nothing would read as a failure to
    compute rather than the fact it is.
    """
    said = with_place(monkeypatch, "stations")["data"]["embeds"][0]["description"]
    assert "**Sunrise** <t:" in said
    assert "Civil Dawn** — does not occur: the Sun does not reach that depth" in said


def test_every_instrument_the_client_can_ask_for_has_a_command() -> None:
    """
    Five methods sat on the ephemeris client with no command in front of them.
    Both halves worked, so nothing was missing to grep for — the feature was
    simply unreachable. This is the check that would have said so.
    """
    import inspect as _inspect

    from vcordbot.astro import Astro

    asked = {n for n, _ in _inspect.getmembers(Astro, _inspect.iscoroutinefunction)
             if not n.startswith("_")}
    wired = {n for n in asked if f"astro.{n}(" in _inspect.getsource(D)}
    assert asked == wired, f"reachable from no command: {sorted(asked - wired)}"


def test_the_manual_always_fits_in_an_embed() -> None:
    """
    Discord REFUSES an over-long embed rather than truncating it, so the
    failure is the whole message going missing. Ten commands sit at about
    2700 characters; this is the check that the eleventh does not break /help
    for everybody, discovered by whoever runs it.
    """
    from vcordbot import render

    many = C.COMMANDS + [dict(c, name=f"{c['name']}{i}")
                         for i in range(4) for c in C.COMMANDS]
    for commands in (C.COMMANDS, many):
        said = render.manual(commands, BOT, SITE)["description"]
        assert len(said) < render.DESCRIPTION_LIMIT, len(said)

    # And below the cap it is still the full manual, not the short list.
    full = render.manual(C.COMMANDS, BOT, SITE)["description"]
    assert "e.g.  /chart" in full


def test_attic_names_the_reckoning_it_used(monkeypatch) -> None:
    """
    Two rules that open half the months of a year on different days. Which one
    produced the date has to travel with the date. The daemon's key is `used`;
    read as `note` it rendered nothing at all and the line vanished silently.
    """
    astro = ChartAstro()
    said = with_place(monkeypatch, "attic", astro,
                      reckoning="visibility")["data"]["embeds"][0]["description"]
    assert astro.calls[0][2] == "visibility"
    assert "Visibility reckoning" in said
    assert "first crescent somebody could see" in said


def test_attic_defaults_to_conjunction(monkeypatch) -> None:
    astro = ChartAstro()
    with_place(monkeypatch, "attic", astro)
    assert astro.calls[0][2] == "conjunction"
