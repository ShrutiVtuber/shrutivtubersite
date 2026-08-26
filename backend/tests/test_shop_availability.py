# SPDX-License-Identifier: AGPL-3.0-only
"""
Two ways to sell, and the window has to be real.

She prints her own things, so there is no minimum order and both selling models
are worth having: batch-printed stock sitting on a shelf, and a drop open for a
fortnight around a birthday. One table serves both — a window is an optional
pair of dates, not a different kind of product.

The failure this guards against is the ordinary one: a disabled button in front
of a working endpoint. A closed drop that still takes money is worse than one
that never closed, because somebody has paid for it.
"""
from __future__ import annotations

import inspect
import re
from datetime import datetime, timedelta, timezone

from shruti.api.routes.shop import availability, checkout
from shruti.models import Product

NOW = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
DAY = timedelta(days=1)


def _p(**kw) -> Product:
    return Product(slug="x", name="x", **kw)


def test_no_window_means_simply_on_sale() -> None:
    """The default, and right for anything batch-printed and kept."""
    assert availability(_p(stock=4), NOW)["state"] == "open"
    assert availability(_p(stock=None), NOW)["state"] == "open"


def test_stock_runs_out() -> None:
    assert availability(_p(stock=0), NOW)["state"] == "sold-out"


def test_made_to_order_never_sells_out() -> None:
    """
    There is no shelf to run out of. Showing "sold out" on something she can
    print this afternoon is the specific mistake this exists to prevent.
    """
    a = availability(_p(stock=0, made_to_order=True, lead_time="2–3 weeks"), NOW)
    assert a["state"] == "open" and a["buyable"] is True
    assert a["leadTime"] == "2–3 weeks", "a buyer needs the wait instead of a count"


def test_a_drop_before_and_after() -> None:
    before = availability(_p(opens_at=NOW + 3 * DAY, closes_at=NOW + 17 * DAY), NOW)
    during = availability(_p(opens_at=NOW - DAY, closes_at=NOW + 13 * DAY), NOW)
    after = availability(_p(opens_at=NOW - 20 * DAY, closes_at=NOW - DAY), NOW)
    assert (before["state"], before["buyable"]) == ("not-yet", False)
    assert (during["state"], during["buyable"]) == ("open", True)
    assert (after["state"], after["buyable"]) == ("closed", False)


def test_the_three_shut_states_are_told_apart() -> None:
    """
    All three mean "you cannot buy this" and none of them means the same thing
    to a reader: one is bad luck, one is a date to come back on, one is over.
    """
    states = {
        availability(_p(stock=0), NOW)["state"],
        availability(_p(opens_at=NOW + DAY), NOW)["state"],
        availability(_p(closes_at=NOW - DAY), NOW)["state"],
    }
    assert states == {"sold-out", "not-yet", "closed"}


def test_the_window_is_enforced_at_checkout_and_not_only_on_the_button() -> None:
    source = re.sub(r'"""[\s\S]*?"""', "", inspect.getsource(checkout))
    assert "availability(" in source, "checkout must ask the same question the page did"
    assert 'state["buyable"]' in source
    assert "409" in source


def test_a_closed_drop_is_a_conflict_rather_than_a_not_found() -> None:
    """
    404 would say the thing never existed. It did, and somebody may be holding
    a link to it from the announcement — they are owed the real reason.
    """
    source = re.sub(r'"""[\s\S]*?"""', "", inspect.getsource(checkout))
    assert "that drop has closed" in source
