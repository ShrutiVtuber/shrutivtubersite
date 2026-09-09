# SPDX-License-Identifier: AGPL-3.0-only
"""
The bot, the site and the app must agree about which week it is.

Three implementations of ISO weeks now exist — TypeScript on the site, Dart in
the app, Python here — because each runs somewhere the others cannot. Three
chances to disagree about a rule subtle enough (Thursday decides the year) that
every one of them would render a perfectly plausible week.

So all three are checked against ONE fixture, generated from the site's own code
over fifteen years. ⚠ Regenerate with
`node --experimental-strip-types frontend/site/scripts/gen-weeks.mjs`, and copy
the rebuilt fixture to all three repos — the app has the matching test.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from vcordbot.periods import current_covers, iso_week, span, week_days

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "iso_weeks.json").read_text()
)
WEEKS = FIXTURE["weeks"]


def test_the_fixture_covers_the_hard_years() -> None:
    assert len(WEEKS) > 700
    assert any(w["week"].endswith("-W53") for w in WEEKS), (
        "no 53-week year in the fixture — the case that breaks naive "
        "implementations is missing"
    )
    assert any(w["days"][0].startswith("2019") and w["week"].startswith("2020")
               for w in WEEKS), "no week that belongs to the previous year"


def test_every_day_lands_in_the_week_the_site_gives_it() -> None:
    wrong = []
    for w in WEEKS:
        for day in (w["first"], w["last"]):
            got = iso_week(date.fromisoformat(day))
            if got != w["week"]:
                wrong.append(f"{day}: site {w['week']}, bot {got}")
    assert not wrong, f"{len(wrong)} days differ:\n" + "\n".join(wrong[:8])


def test_every_week_spans_the_days_the_site_says() -> None:
    wrong = []
    for w in WEEKS:
        got = week_days(w["week"])
        want = tuple(w["days"])
        if got != want:
            wrong.append(f"{w['week']}: site {want}, bot {got}")
    assert not wrong, f"{len(wrong)} weeks differ:\n" + "\n".join(wrong[:8])


def test_a_week_contains_its_own_monday() -> None:
    for w in WEEKS:
        start, _ = week_days(w["week"])
        assert iso_week(date.fromisoformat(start)) == w["week"]


def test_the_other_periods_are_keyed_the_way_the_site_keys_them() -> None:
    when = date(2026, 9, 10)
    assert current_covers("daily", when) == "2026-09-10"
    assert current_covers("monthly", when) == "2026-09"
    assert current_covers("yearly", when) == "2026"


def test_a_month_ends_on_its_own_last_day() -> None:
    """February, and a leap February — the two the arithmetic gets wrong."""
    assert span("monthly", "2026-02") == ("2026-02-01", "2026-02-28")
    assert span("monthly", "2028-02") == ("2028-02-01", "2028-02-29")
    assert span("monthly", "2026-12") == ("2026-12-01", "2026-12-31")
