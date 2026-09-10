# SPDX-License-Identifier: AGPL-3.0-only
"""
Offers, and the three ways one becomes a promise she cannot keep.

This is the monetisation path for a free app, so the failures are not cosmetic:
each one ends with somebody typing a code at a till and being refused, in
public, after she announced it on stream.

1. **An offer that has ended keeps showing.** She either honours a discount she
   withdrew or refuses somebody who read it in her own app.
2. **A members-only offer reaches a non-member.** Same refusal, and it makes
   the membership look like a trick.
3. **A sponsor's code gets a Stripe coupon of ours behind it.** A discount
   invented for a code she does not own, which nobody will accept anywhere.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone

from shruti.api.routes import offers
from shruti.models import Offer

NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def _offer(**kw) -> Offer:
    return Offer(title="x", **kw)


def test_no_end_date_means_no_end() -> None:
    """
    ⚠ Inverted, this hides every open-ended offer she has — and the symptom is
    an empty list, which looks like nothing was ever created.
    """
    assert offers.running(_offer(), at=NOW) is True
    assert offers.running(_offer(), at=datetime(2099, 1, 1, tzinfo=timezone.utc)) is True


def test_an_offer_stops_the_moment_it_ends() -> None:
    ends = NOW + timedelta(days=1)
    assert offers.running(_offer(ends_at=ends), at=ends - timedelta(seconds=1)) is True
    assert offers.running(_offer(ends_at=ends), at=ends) is False
    assert offers.running(_offer(ends_at=ends), at=ends + timedelta(days=30)) is False


def test_an_offer_does_not_start_early() -> None:
    """Something set up for next week must not be readable this week."""
    starts = NOW + timedelta(days=7)
    assert offers.running(_offer(starts_at=starts), at=NOW) is False
    assert offers.running(_offer(starts_at=starts), at=starts) is True


def test_hidden_beats_every_date() -> None:
    assert offers.running(_offer(visible=False), at=NOW) is False
    assert offers.running(
        _offer(visible=False, ends_at=NOW + timedelta(days=100)), at=NOW) is False


def test_a_naive_stamp_is_read_as_utc() -> None:
    """
    A row built by a migration or a fixture may carry no zone. Comparing it
    raises TypeError, which on the app's home screen is a blank section.
    """
    assert offers.running(_offer(ends_at=datetime(2020, 1, 1)), at=NOW) is False
    assert offers.running(_offer(ends_at=datetime(2099, 1, 1)), at=NOW) is True


def test_a_members_only_offer_is_left_out_rather_than_locked() -> None:
    """
    Not shown-and-greyed. A list of things you cannot have is a worse advert
    for a membership than a shorter list — and it cannot leak the code.
    """
    source = inspect.getsource(offers.what_is_on)
    assert "member or not o.members_only" in source
    # The code itself is assembled per offer, so a filtered-out offer never has
    # its code built at all.
    assert "if running(o) and" in source


def test_a_sponsors_offer_cannot_carry_one_of_our_coupons() -> None:
    source = inspect.getsource(offers.make)
    assert 'body.kind == "sponsor"' in source
    assert "discount_id is not None" in source


def test_the_code_comes_from_the_discount_not_a_copy() -> None:
    """
    Stripe holds the real code. A copy on the offer row is a second place for
    it to be wrong, and the wrong one is the one people would type.
    """
    source = inspect.getsource(offers._json)
    assert "discount.code" in source
    assert "discount.active" in source, (
        "a deactivated discount still hands out its code"
    )
