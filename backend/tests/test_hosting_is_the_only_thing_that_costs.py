# SPDX-License-Identifier: AGPL-3.0-only
"""
Her decision of 13 September 2026: reading and tracking are free and
unlimited; overlays are free for 100 hours on air a month; hosting is €5 a
month or €50 a year — sold on the account page and nowhere else, never in
the app. Going past a limit never cuts anybody off mid-stream.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import groups, overlay_guides as og

ROOT = Path(__file__).resolve().parents[2]


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def test_the_free_tier_is_a_hundred_hours() -> None:
    assert og.FREE_HOURS == 100


def test_a_limit_is_checked_only_when_minting_never_when_drawing() -> None:
    assert "refuse_if_out_of_allowance" in code_of(og.mint_token)
    assert "refuse_if_out_of_allowance" in code_of(groups.mint_goal_token)
    for fn in (og.guide, og._goal_frame, og._fill_goals):
        assert "allowance" not in code_of(fn), f"{fn.__name__} would cut somebody off mid-stream"


def test_the_operator_is_never_limited_and_hosting_lifts_the_hours() -> None:
    body = code_of(og.allowance)
    assert 'hours_limit = None if (operator or hosted) else FREE_HOURS' in body
    assert "tokens_limit = None if operator else" in body


def test_reading_and_tracking_are_never_limited() -> None:
    from shruti.api.routes import guides, runs
    for module in (guides, runs):
        source = inspect.getsource(module)
        assert "allowance" not in source and "FREE_HOURS" not in source


def test_the_app_never_names_a_price() -> None:
    app = ROOT.parent / "shrutisgametracker" / "app" / "lib"
    if not app.exists():
        return
    text = "\n".join(p.read_text(encoding="utf-8") for p in app.rglob("*.dart"))
    for word in ("€5", "€50", "5 euro", "50 euro", "checkout", "hosting-monthly", "hosting-yearly", "Host monthly", "Host yearly"):
        assert word not in text, f"{word} in the app"
