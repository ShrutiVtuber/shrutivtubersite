# SPDX-License-Identifier: AGPL-3.0-only
"""
How long a standing compatibility test stays up.

Her table: five days for somebody who is not a member, ten for the lower tier,
permanent for the higher. Which makes it a membership feature with an expiry
rather than a page.

⚠ **This is the part the plan says will go wrong quietly**, and it is worth
saying why the two failures are not symmetric:

- An expired test that keeps answering is a feature given away. Nobody
  complains about getting something for free, so nobody notices.
- One that stops with no explanation is a VTuber who thinks the site is broken
  — and they tell people.

So: the rule is checked, null is permanent rather than "expired long ago", an
unknown tier gets the SHORT run, and there is always something to offer.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from shruti.core.standing import (
    HIGHER, LOWER, expires_at, has_run_out, run_days, what_would_keep_it,
)

NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize("tier,days", [("", 5), (LOWER, 10)])
def test_the_table_she_gave(tier: str, days: int) -> None:
    assert run_days(tier) == days
    assert expires_at(tier, at=NOW) == NOW + timedelta(days=days)


def test_the_higher_tier_is_permanent() -> None:
    assert run_days(HIGHER) is None
    assert expires_at(HIGHER, at=NOW) is None


def test_an_unknown_tier_gets_the_SHORT_run() -> None:
    """
    The safe direction to be wrong in. Somebody who should have had ten days and
    got five asks why, and is told. Somebody who should have had five and got
    permanent never says a word, and the feature is gone.
    """
    # ⚠ Not "ALMANAC " — that is the higher tier written oddly, and the test
    # below says it is normalised. An unknown tier is one she has never sold.
    for odd in ("patron", "gold", "supporter", None, "  "):
        assert run_days(odd or "") == 5, odd


def test_the_tier_is_matched_whatever_its_case() -> None:
    assert run_days("Almanac") is None
    assert run_days("  LAMPLIGHTER  ") == 10


def test_null_means_permanent_and_not_expired_at_the_epoch() -> None:
    """
    Backwards, this takes down HER test — the one with no owner to notice it
    has gone.
    """
    assert has_run_out(None) is False
    assert has_run_out(None, at=datetime(2099, 1, 1, tzinfo=timezone.utc)) is False


def test_a_run_ends_the_moment_it_ends() -> None:
    ends = datetime(2026, 9, 15, tzinfo=timezone.utc)
    assert has_run_out(ends, at=ends - timedelta(seconds=1)) is False
    assert has_run_out(ends, at=ends) is True
    assert has_run_out(ends, at=ends + timedelta(days=1)) is True


def test_a_naive_stamp_is_read_as_utc_rather_than_crashing() -> None:
    """
    A row built in a test, or by a migration, may carry no zone. Comparing it
    raises TypeError, which on a public page is a 500 where an answer belongs.
    """
    assert has_run_out(datetime(2020, 1, 1), at=NOW) is True
    assert has_run_out(datetime(2099, 1, 1), at=NOW) is False


def test_there_is_always_something_to_offer_somebody_who_expired() -> None:
    """Never a dead end — that is the whole warning about this feature."""
    assert what_would_keep_it("") == LOWER
    assert what_would_keep_it(LOWER) == HIGHER
    # Nothing to sell somebody who already has the permanent one.
    assert what_would_keep_it(HIGHER) == ""
