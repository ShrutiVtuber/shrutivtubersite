# SPDX-License-Identifier: AGPL-3.0-only
"""
A run keeps a person's place on a path — and never measures their absence.

The engine is tested where it lives (shrutisgametracker/server/tests); these
hold the site's half: the routes, the resets, the re-entry words, and the
rules from the brief that a route could quietly break.
"""
from __future__ import annotations

import inspect
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from shruti.api.routes import runs

SOURCE = inspect.getsource(runs)


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def prose_free(text: str) -> str:
    """Comments and docstrings out, so a guard never matches its own explanation."""
    text = re.sub(r'"""..*?"""', " ", text, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", text)


# ── nothing is applied silently ─────────────────────────────────────────────

def test_a_checkin_marks_nothing() -> None:
    body = code_of(runs.checkin)
    assert "row.checkin = merged" in body
    assert "row.steps" not in body                     # proposals come back; nothing is marked


def test_accept_marks_only_what_was_ticked() -> None:
    body = code_of(runs.accept)
    assert "for sid in body.steps:" in body
    assert "proposals" not in body                     # it does not re-derive the list and apply it


def test_a_run_starts_with_a_proposal_not_a_skip() -> None:
    assert '@router.get("/skip-proposal")' in SOURCE
    assert "engine.bulk_skip_proposal(doc, wanted)" in code_of(runs.skip_proposal)
    body = code_of(runs.create)
    assert "body.skip_steps" in body                   # what the person confirmed, and only that


# ── nothing measures absence ────────────────────────────────────────────────

def test_no_streaks_no_day_counts_no_missed_days() -> None:
    code = prose_free(SOURCE).lower()
    for word in ("streak", "days ago", "missed", "days_missed", "percent"):
        assert word not in code, word


def test_re_entry_names_a_weekday_never_a_count() -> None:
    zone = ZoneInfo("Europe/Athens")
    when = datetime(2026, 9, 8, 19, 30, tzinfo=timezone.utc)           # a Tuesday, 22:30 in Athens
    assert runs._weekday_evening(when, zone) == "Tuesday evening"
    assert runs._weekday_evening(datetime(2026, 9, 9, 6, 0, tzinfo=timezone.utc), zone) == "Wednesday morning"
    body = code_of(runs._view)
    assert "REENTRY_AFTER" in body and "_weekday_evening" in body


# ── the person's side is never overridden ────────────────────────────────────

def test_only_what_a_person_set_is_stored() -> None:
    """Locked, available and current are computed on every read, never written."""
    body = code_of(runs.set_step)
    assert 'if body.state == "open":' in body and "steps.pop(step_id, None)" in body
    assert '"available"' not in prose_free(SOURCE) or "engine.compute" in SOURCE
    for state in ("locked", "available", "current"):
        assert f'"state": "{state}"' not in prose_free(SOURCE)


def test_undo_takes_the_step_off_the_later_list_too() -> None:
    body = code_of(runs.set_step)
    assert 'later = [x for x in later if x.get("step") != step_id]' in body


def test_a_run_is_the_owners_or_404() -> None:
    body = code_of(runs._run_of)
    assert "run.user_id != user.id" in body and "404" in body and "403" not in body


def test_a_checkin_keeps_only_declared_fields_within_range() -> None:
    doc = {"checkin": [
        {"id": "level", "label": "Level", "type": "number", "min": 1, "max": 70},
        {"id": "story", "label": "Story", "type": "ordered", "options": ["act1", "act2"]},
    ]}
    out = runs._clean_checkin({"level": 99, "story": "act2", "bogus": 1, "paragon": 5}, doc)
    assert out == {"level": 70, "story": "act2"}
    assert runs._clean_checkin({"story": "nope", "level": "x"}, doc) == {}


# ── resets ───────────────────────────────────────────────────────────────────

def test_routine_resets_follow_the_format() -> None:
    zone = ZoneInfo("UTC")
    now = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)                 # Wednesday noon
    assert not runs._reset_due("manual", None, None, now, zone)
    assert runs._reset_due("session", None, now - timedelta(hours=7), now, zone)
    assert not runs._reset_due("session", None, now - timedelta(hours=1), now, zone)
    # daily: 04:00 local — ticked yesterday evening resets, ticked this morning after 04:00 does not
    assert runs._reset_due("daily", now - timedelta(hours=20), None, now, zone)
    assert not runs._reset_due("daily", now - timedelta(hours=2), None, now, zone)
    # weekly: Tuesday 04:00 — ticked last Sunday resets, ticked Tuesday 05:00 does not
    assert runs._reset_due("weekly", now - timedelta(days=3), None, now, zone)
    assert not runs._reset_due("weekly", now - timedelta(days=1, hours=7), None, now, zone)


def test_a_reset_clears_ticks_and_nothing_else() -> None:
    body = code_of(runs._apply_resets)
    assert '{"ticked": [], "reset_at": now.isoformat()}' in body
    assert "row.steps" not in body and "row.checkin" not in body


# ── nobody's progress is trapped ─────────────────────────────────────────────

def test_export_carries_everything_and_import_checks_the_kind() -> None:
    body = code_of(runs.export_run)
    for key in ('"steps"', '"checkin"', '"routines"', '"tracks"', '"later"', '"note"', '"linkOverrides"'):
        assert key in body
    assert 'if r.get("kind") != "run":' in code_of(runs.import_run)


def test_the_view_says_when_the_guide_moved_on() -> None:
    """"This guide has a newer version. Your progress is kept" — the page needs to know."""
    body = code_of(runs._view)
    assert '"stale": bool(row.version_id) and row.version_id != version.id' in body
    assert '"orphaned": progress.orphaned' in body
