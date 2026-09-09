# SPDX-License-Identifier: AGPL-3.0-only
"""
Which period a horoscope is for.

⚠ **This must agree with the site's `lib/periods.ts` and the app's
`services/periods.dart`.** The id is what the database is keyed on, and a
reading filed under the wrong week is filed under somebody else's week — both
look perfectly plausible and nobody can tell by reading them.

ISO weeks are the subtle part: Monday starts the week, week one holds the first
Thursday, and **Thursday decides the year**, which is why a week in early
January can belong to the year before. `test_periods_agree.py` holds this
against the same fixture the app uses, generated from the site's own code.
"""
from __future__ import annotations

from datetime import date, timedelta

PERIODS = ("daily", "weekly", "monthly", "yearly")


def iso_week(day: date) -> str:
    """The ISO week id for a day: "2026-W37"."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def week_days(week_id: str) -> tuple[str, str]:
    """The Monday and Sunday of an ISO week id."""
    year, week = week_id.split("-W")
    monday = date.fromisocalendar(int(year), int(week), 1)
    return monday.isoformat(), (monday + timedelta(days=6)).isoformat()


def current_covers(period: str, at: date | None = None) -> str:
    today = at or date.today()
    if period == "daily":
        return today.isoformat()
    if period == "weekly":
        return iso_week(today)
    if period == "yearly":
        return str(today.year)
    return f"{today.year}-{today.month:02d}"


def span(period: str, covers: str) -> tuple[str, str]:
    """The first and last day of a period, inclusive."""
    if period == "daily":
        return covers, covers
    if period == "weekly":
        return week_days(covers)
    if period == "yearly":
        return f"{covers}-01-01", f"{covers}-12-31"
    year, month = (int(p) for p in covers.split("-"))
    first = date(year, month, 1)
    last = date(year + (month == 12), (month % 12) + 1, 1) - timedelta(days=1)
    return first.isoformat(), last.isoformat()


def label(period: str, covers: str) -> str:
    if period == "weekly":
        start, _ = week_days(covers)
        return f"Week of {date.fromisoformat(start):%-d %B %Y}"
    if period == "daily":
        return f"{date.fromisoformat(covers):%A %-d %B %Y}"
    if period == "monthly":
        return f"{date.fromisoformat(covers + '-01'):%B %Y}"
    return covers
