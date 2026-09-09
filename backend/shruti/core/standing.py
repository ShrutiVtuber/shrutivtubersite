# SPDX-License-Identifier: AGPL-3.0-only
"""
How long a standing compatibility test stays up.

Her table:

    | not a member | 5 days     |
    | lower tier   | 10 days    |
    | higher tier  | permanent  |

⚠ **This is the part that goes wrong quietly.** An expired test that keeps
answering is a feature given away — nobody complains, so nobody notices. One
that 404s with no explanation is a VTuber who thinks the site is broken, which
is worse than the first because they tell people. So the rule lives here on its
own, is checked on every read, and an expired test still has a page that says
when it ran and what would keep it up.

The tiers are named rather than ranked: a ranking would need maintaining every
time she adds one, and getting it wrong means giving away the permanent run.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Her own tier keys, from the billing tier rows.
LOWER = "lamplighter"
HIGHER = "almanac"

# ⚠ Days, by tier. A tier that is not in here gets the shortest run, which is
# the safe direction to be wrong in: somebody who should have had ten days asks
# why, and is told. Somebody who should have had five and got permanent never
# says a word.
RUN_DAYS: dict[str, int | None] = {
    "": 5,          # not a member
    LOWER: 10,
    HIGHER: None,   # permanent
}


def run_days(tier: str) -> int | None:
    """How many days this tier buys, or None for permanent."""
    return RUN_DAYS.get((tier or "").strip().lower(), RUN_DAYS[""])


def expires_at(tier: str, *, at: datetime | None = None) -> datetime | None:
    """
    When a test set up now, at this tier, stops answering.

    None means never — the higher tier, and hers.
    """
    days = run_days(tier)
    if days is None:
        return None
    return (at or datetime.now(timezone.utc)) + timedelta(days=days)


def has_run_out(expires: datetime | None, *, at: datetime | None = None) -> bool:
    """
    Whether a test has stopped.

    ⚠ Null is permanent, not "expired at the epoch". Getting this backwards
    would take down her own test, which is the one that has no owner to notice.
    """
    if expires is None:
        return False
    now = at or datetime.now(timezone.utc)
    # A row read back from Postgres carries its zone; one built in a test may
    # not. Treat a naive stamp as UTC rather than crashing on the comparison.
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires <= now


def what_would_keep_it(tier: str) -> str:
    """
    What to offer somebody whose test has run out.

    Never a dead end: the plan's whole warning about this feature is that an
    expired one with no explanation reads as a broken site.
    """
    if run_days(tier) is None:
        return ""          # nothing to sell; it never expires
    if (tier or "").strip().lower() == LOWER:
        return HIGHER
    return LOWER
