# SPDX-License-Identifier: AGPL-3.0-only
"""
What the bot says, checked without a gateway.

The whole point of keeping `render` free of Discord imports is that this file
needs no token, no server and no network. If these ever need one, the layering
has broken.
"""
from __future__ import annotations

import re

from vcordbot import render

BOT = "https://bot.example.test"
SITE = "https://site.example.test"


def test_the_footer_is_on_every_message() -> None:
    """
    It is permanent now — there is no paid tier that removes it — so its
    presence is the thing most worth a test. A message without it is a message
    that neither says where it came from nor that a machine sent it.
    """
    hours = render.planetary_hours(
        {"current": {"index": 5, "ruler": "Mars", "isNight": False,
                     "endsAt": "2026-08-26T09:20:25+00:00"},
         "sunrise": "2026-08-26T03:49:25+00:00",
         "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Mercury"},
        "Athens", BOT, SITE)
    iso = render.isopsephy(
        {"text": "ΛΟΓΟΣ", "total": 373, "letters": [{"char": "λ", "value": 30}],
         "reduction": {"final": 4}, "cipher": {"name": "Isopsephy"}}, BOT, SITE)
    bad = render.failure("nope", BOT, SITE)

    for e in (hours, iso, bad):
        assert render.footer(BOT, SITE) in e["description"]


def test_the_footer_says_both_things_and_is_clickable() -> None:
    f = render.footer(BOT, SITE)
    assert f.startswith("-# "), "must be subtext — quiet, or people resent it"
    assert "posted automatically" in f, "the disclosure rides on this line"
    assert f"]({BOT})" in f, "an embed footer cannot hold a link; this can"


def test_the_footer_appears_once() -> None:
    """Twice in one message is the way a tolerated footer becomes an advert."""
    e = render.isopsephy(
        {"text": "x", "total": 1, "letters": [], "cipher": {}}, BOT, SITE)
    assert e["description"].count("posted automatically") == 1


def test_times_are_rendered_for_the_reader_not_for_athens() -> None:
    """
    A Discord timestamp is correct for a viewer in Athens and one in Toronto at
    the same time. Printing a formatted time would be right for one of them.
    """
    e = render.planetary_hours(
        {"current": {"index": 1, "ruler": "Sun", "isNight": False,
                     "endsAt": "2026-08-26T09:20:25+00:00"},
         "sunrise": "2026-08-26T03:49:25+00:00",
         "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Sun"},
        "Athens", BOT, SITE)
    assert re.search(r"<t:\d+:t>", e["description"])
    assert "09:20" not in e["description"], "a wall-clock time is right for one timezone only"


def test_glyphs_carry_text_presentation() -> None:
    """Without U+FE0E a client swaps in a colour-emoji font and ignores style."""
    for mark in render.GLYPH.values():
        assert mark.endswith("\ufe0e")


def test_letters_with_no_value_are_named_rather_than_dropped() -> None:
    """A character silently ignored changes the sum by its absence."""
    e = render.isopsephy(
        {"text": "ΛΟΓΟΣ!", "total": 373, "letters": [{"char": "λ", "value": 30}],
         "unmatched": ["!"], "cipher": {}}, BOT, SITE)
    assert "Ignored" in e["description"] and "!" in e["description"]


def test_a_failure_does_not_blame_the_person() -> None:
    e = render.failure("The ephemeris took too long to answer.", BOT, SITE)
    assert "you" not in e["description"].lower().split("posted")[0]


def test_a_night_hour_is_numbered_within_the_night() -> None:
    """
    The daemon numbers all twenty-four continuously, so the first hour of the
    night arrives as 13. Rendering that raw produced "the 13 hour of the
    night" — ungrammatical, and wrong by twelve.
    """
    e = render.planetary_hours(
        {"current": {"index": 13, "ruler": "Sun", "isNight": True,
                     "endsAt": "2026-08-26T20:00:00+00:00"},
         "sunrise": "2026-08-26T03:49:25+00:00",
         "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Mercury"},
        "Athens", BOT, SITE)
    assert "i hour of the night" in e["description"]
    assert "13" not in e["description"].split("Sunrise")[0]


def test_a_day_hour_keeps_its_number() -> None:
    e = render.planetary_hours(
        {"current": {"index": 5, "ruler": "Mars", "isNight": False,
                     "endsAt": "2026-08-26T09:20:25+00:00"},
         "sunrise": "2026-08-26T03:49:25+00:00",
         "sunset": "2026-08-26T17:03:48+00:00", "dayRuler": "Mercury"},
        "Athens", BOT, SITE)
    assert "v hour of the day" in e["description"]


def test_a_text_with_no_values_says_so_rather_than_answering_nought() -> None:
    """
    Everything ignored and a total of nought is a mismatch between the text and
    the table, not a sum. Printing "0" is confidently wrong.
    """
    e = render.isopsephy(
        {"text": "אמת", "total": 0, "letters": [], "unmatched": ["א", "מ", "ת"],
         "cipher": {"name": "Isopsephy"}, "reduction": {"final": 0}}, BOT, SITE)
    assert "## 0" not in e["description"]
    assert "Nothing in that has a value" in e["description"]
    assert "Try a different script" in e["description"]
