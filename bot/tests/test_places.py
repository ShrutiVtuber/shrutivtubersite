# SPDX-License-Identifier: AGPL-3.0-only
"""
Resolving a city, and the clock that was running there at the time.

The gazetteer is a stand-in. What is under test is the bot's own filtering —
which Springfield, which Athens — and the offset arithmetic, which is the part
that decides whether a chart belongs to the person who asked for it or to
somebody three hours away.
"""
from __future__ import annotations

import asyncio

import httpx
import pytest

from vcordbot import places
from vcordbot.places import Place, PlaceError

ROWS = [
    {"name": "Athens", "admin1": "Attica", "country": "Greece", "country_code": "GR",
     "latitude": 37.98376, "longitude": 23.72784, "elevation": 90.0,
     "timezone": "Europe/Athens", "population": 664046},
    {"name": "Athens", "admin1": "Georgia", "country": "United States", "country_code": "US",
     "latitude": 33.96095, "longitude": -83.37794, "elevation": 205.0,
     "timezone": "America/New_York", "population": 116714},
    {"name": "Athens", "admin1": "Ohio", "country": "United States", "country_code": "US",
     "latitude": 39.32924, "longitude": -82.10126, "elevation": 218.0,
     "timezone": "America/New_York", "population": 24688},
]


def gazetteer(rows=ROWS, status=200):
    """A client that answers like Open-Meteo and records nothing else."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"results": rows})
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def find(city, country="", region=""):
    async def go():
        async with gazetteer() as client:
            return await places.find(city, country, region, client=client)
    return asyncio.run(go())


def test_country_narrows_a_repeated_city_name() -> None:
    """
    Athens, Greece and Athens, Georgia are eleven degrees and seven hours
    apart. Getting this wrong produces a chart that is entirely plausible.
    """
    best, _ = find("Athens", "Greece")
    assert best.country_code == "GR"
    assert best.timezone == "Europe/Athens"


def test_usa_is_understood_however_it_is_typed() -> None:
    for typed in ("USA", "usa", "United States", "US", "america"):
        best, _ = find("Athens", typed)
        assert best.country_code == "US", typed


def test_a_state_picks_between_two_cities_in_one_country() -> None:
    best, _ = find("Athens", "USA", "Ohio")
    assert best.region == "Ohio"


def test_a_postal_code_works_as_well_as_the_state_name() -> None:
    """An American types OH. The gazetteer says Ohio. Both must land."""
    best, _ = find("Athens", "USA", "OH")
    assert best.region == "Ohio"


def test_the_runners_up_come_back_too() -> None:
    """
    A chat message has no "Not this place?" control, so the alternatives have
    to travel with the answer or a wrong Athens is invisible.
    """
    best, others = find("Athens")
    assert best.region == "Attica"                      # most populous wins
    assert [p.region for p in others] == ["Georgia", "Ohio"]


def test_nothing_found_says_so_rather_than_guessing() -> None:
    async def go():
        async with httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda r: httpx.Response(200, json={"results": []}))) as c:
            return await places.find("Nowhereton", "Greece", client=c)
    with pytest.raises(PlaceError, match="could not find"):
        asyncio.run(go())


def test_an_unreachable_gazetteer_is_not_a_missing_city() -> None:
    """The caller must be able to tell those apart, and so must the person."""
    async def go():
        async with httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda r: httpx.Response(503, json={}))) as c:
            return await places.find("Athens", client=c)
    with pytest.raises(PlaceError, match="could not be reached"):
        asyncio.run(go())


# ── the clock that was running ──────────────────────────────────────────────

ATHENS = Place("Athens", "Attica", "Greece", "GR", 37.9838, 23.7275, 90.0,
               "Europe/Athens", 664046)
LA = Place("Los Angeles", "California", "United States", "US", 34.05, -118.24,
           89.0, "America/Los_Angeles", 3898747)


def test_the_offset_is_the_one_that_applied_on_the_day() -> None:
    """
    Summer in Athens is +03:00 and winter is +02:00. Today's rules are not the
    answer to a question about 1996.
    """
    assert places.at(ATHENS, "1996-05-14", "09:30").offset == "+03:00"
    assert places.at(ATHENS, "1996-01-14", "09:30").offset == "+02:00"


def test_the_moment_carries_its_offset() -> None:
    """
    The whole point. A bare local time reaches the ephemeris as UTC, which for
    Athens is three hours and about forty-five degrees of ascendant away.
    """
    assert places.at(ATHENS, "1996-05-14", "09:30").when == "1996-05-14T09:30:00+03:00"
    assert places.at(LA, "1996-05-14", "09:30").when == "1996-05-14T09:30:00-07:00"


def test_a_clock_that_skipped_that_hour_is_reported() -> None:
    """
    02:30 on the night the clock goes forward never happened. Somebody whose
    certificate says it deserves to be told, not silently moved an hour.
    """
    note = places.at(LA, "1996-04-07", "02:30").note
    assert "never occurred" in note


def test_an_hour_lived_twice_is_reported() -> None:
    note = places.at(LA, "1996-10-27", "01:30").note
    assert "happened twice" in note


def test_an_ordinary_hour_says_nothing() -> None:
    assert places.at(ATHENS, "1996-05-14", "09:30").note == ""
