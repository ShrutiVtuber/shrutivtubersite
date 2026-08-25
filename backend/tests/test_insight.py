# SPDX-License-Identifier: AGPL-3.0-only
"""
Counting without following.

Every test here is about a property that makes the consent banner unnecessary.
If one of them stops holding, the honest response is not to fix the test — it
is to add the banner, because the thing being stored would have become personal
data.
"""
from __future__ import annotations

import inspect
from datetime import date

import pytest
from fastapi import Request

from shruti.api.routes import insight


def _request(ip: str = "203.0.113.9", agent: str = "Mozilla/5.0 Chrome/131") -> Request:
    return Request({
        "type": "http", "method": "POST", "path": "/api/insight/beacon",
        "headers": [(b"user-agent", agent.encode()),
                    (b"x-forwarded-for", ip.encode())],
        "client": ("203.0.113.9", 1234), "query_string": b"", "scheme": "https",
        "server": ("shrutivtuber.com", 443),
    })


def test_the_same_person_is_the_same_number_all_day():
    """Otherwise nothing could be counted at all."""
    day = date(2026, 8, 25)
    assert insight._visitor(_request(), day) == insight._visitor(_request(), day)


def test_the_same_person_is_a_different_number_tomorrow():
    """
    The whole basis of this being anonymous.

    A number that persisted would be a cookie by another name — worse, one
    somebody could not clear.
    """
    a = insight._visitor(_request(), date(2026, 8, 25))
    b = insight._visitor(_request(), date(2026, 8, 26))
    assert a != b


def test_two_people_are_two_numbers():
    day = date(2026, 8, 25)
    assert insight._visitor(_request(ip="203.0.113.9"), day) != \
        insight._visitor(_request(ip="198.51.100.4"), day)


def test_the_number_is_not_the_address():
    """It cannot be read back, and it does not contain what went in."""
    got = insight._visitor(_request(ip="203.0.113.9"), date(2026, 8, 25))
    assert "203.0.113" not in got
    assert "Chrome" not in got
    assert len(got) == 32


def test_the_address_is_never_written_down():
    """
    Used and dropped. It reaches the hash and stops — it is in no column, and
    the model has nowhere to put it even by accident.
    """
    from shruti.models import Visit

    fields = set(Visit.model_fields)
    assert not {"ip", "address", "remote_addr", "user_agent", "agent"} & fields

    stored = inspect.getsource(insight.beacon)
    assert "x-forwarded-for" not in stored      # read in _visitor, not here


def test_a_referring_search_query_is_thrown_away():
    """
    A search URL carries somebody's own words about what they were looking
    for. The host answers "where from" and is not their business.
    """
    got = insight._referrer_host("https://www.google.com/search?q=something+private")
    assert got == "www.google.com"
    assert "private" not in got


def test_arriving_from_our_own_pages_is_not_a_referrer():
    assert insight._referrer_host("https://shrutivtuber.com/tools") == ""


def test_nothing_a_visitor_typed_is_collectable():
    """
    Props are for "which tool", never "what did they ask it". The cap is on
    length and count so a well-meaning edit cannot smuggle an essay through.
    """
    source = inspect.getsource(insight.beacon)
    assert "[:40]" in source and "[:80]" in source
    assert "[:8]" in source


def test_robots_are_not_counted():
    for agent in ("Googlebot/2.1", "python-requests/2.31", "curl/8.4", "Headless Chrome"):
        assert any(r in agent.lower() for r in insight.ROBOTS), agent


def test_the_beacon_never_reports_a_problem_to_a_visitor():
    """
    A page must not look broken because a counter had an opinion, and a
    visitor cannot act on a rejected visit anyway.
    """
    source = inspect.getsource(insight.beacon)
    assert "status_code=204" in source
    assert "raise HTTPException" not in source


def test_there_is_a_way_to_throw_it_all_away():
    """A thing that collects should always have a way to stop holding."""
    assert hasattr(insight, "forget_everything")


def test_no_cookie_is_ever_set():
    """
    The claim the privacy page makes. If this ever stops being true, the page
    has to change and a banner has to appear.
    """
    source = inspect.getsource(insight)
    assert "set_cookie" not in source
    assert "Set-Cookie" not in source
