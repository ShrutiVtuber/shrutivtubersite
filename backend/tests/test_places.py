"""Place resolution: the gazetteer proxy, and the historical timezone."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from shruti.api.app import app

client = TestClient(app)


@pytest.mark.parametrize(
    "tz,when,offset,abbr",
    [
        # Greece in 1996 is not Greece today, which is the whole reason this
        # endpoint exists: a chart cast an hour out looks right and is not.
        ("Europe/Athens", "1996-05-14T09:30", "+03:00", "EEST"),
        ("Europe/Athens", "2026-01-14T09:30", "+02:00", "EET"),
    ],
)
def test_the_offset_is_the_one_that_applied_then(tz, when, offset, abbr):
    r = client.get("/api/places/offset", params={"tz": tz, "when": when})
    assert r.status_code == 200
    body = r.json()
    assert body["offset"] == offset
    assert body["abbreviation"] == abbr


def test_a_clock_gap_is_not_an_ambiguity():
    """
    Both a spring-forward gap and an autumn fold make the two folds disagree,
    so comparing them alone cannot tell the two apart - it called 01:30 on 29
    March 1981 in London "occurred twice" when the UK clock went forward at
    01:00 GMT and that minute never existed. The round trip separates them.
    """
    r = client.get("/api/places/offset",
                   params={"tz": "Europe/London", "when": "1981-03-29T01:30"}).json()
    assert r["imaginary"] is True
    assert r["ambiguous"] is False
    assert "never occurred" in r["note"]


def test_a_repeated_hour_is_reported_as_repeated():
    r = client.get("/api/places/offset",
                   params={"tz": "America/New_York", "when": "2025-11-02T01:30"}).json()
    assert r["ambiguous"] is True
    assert r["imaginary"] is False
    assert "twice" in r["note"]


def test_an_ordinary_time_is_flagged_as_neither():
    r = client.get("/api/places/offset",
                   params={"tz": "Europe/Athens", "when": "1996-05-14T09:30"}).json()
    assert r["ambiguous"] is False and r["imaginary"] is False and r["note"] == ""


def test_an_unknown_zone_is_refused():
    r = client.get("/api/places/offset", params={"tz": "Mars/Olympus", "when": "2026-01-01T00:00"})
    assert r.status_code == 400


def test_a_short_query_is_refused():
    """Two characters minimum - a one-letter search is every city on Earth."""
    assert client.get("/api/places", params={"q": "a"}).status_code == 422
