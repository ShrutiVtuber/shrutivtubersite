# SPDX-License-Identifier: AGPL-3.0-only
"""
A run keeps a person's place on a path — and never measures their absence.

The logic is tested where it lives (shrutisgametracker/server/tests: the
engine and the progress functions); these hold the site's half: that the
routes DELEGATE to the shared functions rather than keeping a copy, and the
rules from the brief that a route could quietly break.
"""
from __future__ import annotations

import inspect
import re

from shruti.api.routes import runs
from shrutisguides import progress

SOURCE = inspect.getsource(runs)


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def prose_free(text: str) -> str:
    text = re.sub(r'"""..*?"""', " ", text, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", text)


# ── one implementation, shared with the self-hosted tracker ─────────────────

def test_the_site_delegates_to_the_shared_functions() -> None:
    """A copy here would drift from the tracker's; there must be none."""
    assert "progress.view(" in code_of(runs._view)
    assert "progress.apply_resets(" in code_of(runs._answer)
    assert "progress.set_step(" in code_of(runs.set_step)
    assert "progress.clean_checkin(" in code_of(runs.create) and "progress.clean_checkin(" in code_of(runs.checkin)
    assert "progress.export(" in code_of(runs.export_run) and "progress.from_export(" in code_of(runs.import_run)
    for name in ("_reset_due", "_weekday_evening", "_clean_checkin", "_apply_resets", "_element"):
        assert not hasattr(runs, name), f"{name} is a local copy"
    assert runs.STATES is progress.STATES


# ── nothing is applied silently ─────────────────────────────────────────────

def test_a_checkin_marks_nothing() -> None:
    body = code_of(runs.checkin)
    assert "row.checkin = merged" in body and "row.steps" not in body


def test_accept_marks_only_what_was_ticked() -> None:
    body = code_of(runs.accept)
    assert "for sid in body.steps:" in body and "proposals" not in body


def test_a_run_starts_with_a_proposal_not_a_skip() -> None:
    assert '@router.get("/skip-proposal")' in SOURCE
    assert "engine.bulk_skip_proposal(doc, wanted)" in code_of(runs.skip_proposal)
    assert "body.skip_steps" in code_of(runs.create)


# ── nothing measures absence ────────────────────────────────────────────────

def test_no_streaks_no_day_counts_no_missed_days() -> None:
    for module in (SOURCE, inspect.getsource(progress)):
        code = prose_free(module).lower()
        for word in (r"\bstreaks?\b", r"\bdays ago\b", r"\bmissed\b", r"\bpercent\b"):
            assert not re.search(word, code), word


# ── the person's side ───────────────────────────────────────────────────────

def test_only_what_a_person_set_is_stored() -> None:
    """Locked, available and current are computed on every read, never written."""
    for state in ("locked", "available", "current"):
        assert f'"state": "{state}"' not in prose_free(SOURCE)
        assert f'"state": "{state}"' not in prose_free(inspect.getsource(progress))


def test_a_run_is_the_owners_or_404() -> None:
    body = code_of(runs._run_of)
    assert "run.user_id != user.id" in body and "404" in body and "403" not in body


def test_the_view_says_when_the_guide_moved_on() -> None:
    body = code_of(progress.view)
    assert '"stale": bool(version_id) and version_id != published_version_id' in body
    assert '"orphaned": progress.orphaned' in body
