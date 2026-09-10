# SPDX-License-Identifier: AGPL-3.0-only
"""
Reporting, hiding, and the difference between a stopgap and a verdict.

People post writing that other people read, so the room needs a way to say
something should not be there. Every rule below is one that would look fine
while being wrong:

**Three reports hide a thing, and that is a STOPGAP.** Something staying up for
eight hours because it arrived at 3am is the failure that matters. But the row
is a queue entry, not a decision — and if a dismissal only marked the report
read, the auto-hide would stand for ever: down because three strangers said so,
and she said they were wrong.

**One OPEN report per person, not one for ever.** Permanent uniqueness closes a
real hole and opens another: a work can be edited after a dismissal, and the
person who already spoke up is the one most likely to notice it turning into
something worse.

**A suspension bites where writing ENTERS the room, and nowhere else.** It is a
fortnight of silence, not an erasure: reading, drafts and everything already
written are untouched.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from conftest import ROOT

from shruti.api.routes import practice
from shruti.models.practice import PracticeReport, PracticeStrike, PracticeWork

VERSIONS = ROOT / "backend" / "alembic" / "versions"
if not VERSIONS.is_dir():
    VERSIONS = ROOT / "alembic" / "versions"


def _migration(name: str) -> str:
    return (VERSIONS / name).read_text(encoding="utf-8")


def test_three_reports_hide_a_thing() -> None:
    """The number is a judgement and is named, not scattered."""
    assert practice.REPORTS_TO_HIDE == 3
    source = inspect.getsource(practice.report_work)
    assert "REPORTS_TO_HIDE" in source, (
        "the threshold is inlined somewhere and the constant is decoration"
    )
    assert 'hidden_by = "reports"' in source, (
        "an auto-hide must record that it was an auto-hide — `hidden` alone "
        "cannot tell a takedown by strangers from a decision of hers, and the "
        "two are undone differently"
    )


def test_dismissing_puts_it_back() -> None:
    """
    ⚠ The failure this guards is silent: a dismissal that only marks reports
    read leaves the thing hidden for ever, and the queue looks handled.
    """
    source = inspect.getsource(practice.decide)
    assert "subject.hidden = False" in source, (
        "dismissing does not put the thing back on the feed"
    )
    assert 'subject.hidden_by == "reports"' in source, (
        "dismissing must only undo what the REPORTS took down — her own "
        "earlier decision, and an author withdrawing their work, are not "
        "reversed by disagreeing with a report"
    )


def test_only_one_open_report_from_each_person() -> None:
    """
    Enforced by the database, not by looking first. Two taps on a slow
    connection are two requests, and one determined person must not be a
    takedown on their own.
    """
    later = _migration("c8f2a91b4d67_one_open_report_each.py")
    assert "ux_practice_report_work_user" in later
    assert "reviewed_at IS NULL" in later, (
        "uniqueness must be on OPEN reports: permanent uniqueness locks out "
        "the very people most likely to notice an edited work getting worse"
    )
    # And the bridge is not a way round it.
    assert "ux_practice_report_work_discord" in later, (
        "a reporter arriving over the Discord bridge has no site account; "
        "without a key on who Discord says they are, the bridge is the way "
        "round the limit"
    )


def test_a_report_is_about_exactly_one_thing() -> None:
    first = _migration("b7e41c92d8a3_practice_moderation.py")
    assert "ck_practice_report_one_subject" in first, (
        "a report row with both a work and a comment, or neither, is a queue "
        "entry nobody can act on"
    )


def test_a_suspension_bites_only_where_writing_enters() -> None:
    for name in ("submit", "comment"):
        source = inspect.getsource(getattr(practice, name))
        assert "_refuse_if_suspended" in source, (
            f"{name} does not check for a suspension, so a suspended account "
            f"can still post"
        )
    for name in ("save_draft", "read_draft", "feed", "one"):
        source = inspect.getsource(getattr(practice, name))
        assert "_refuse_if_suspended" not in source, (
            f"{name} refuses a suspended account. A suspension is a fortnight "
            f"of silence, not an erasure — reading and drafts stay"
        )


def test_a_suspension_says_so_rather_than_swallowing_the_post() -> None:
    """
    ⚠ A room that accepts a submission and drops it is worse than one that
    says no: the person thinks they posted, waits for a reply, and concludes
    nobody read it.
    """
    source = inspect.getsource(practice._refuse_if_suspended)
    assert "HTTPException" in source and "403" in source
    assert "still read" in source, "the refusal does not say what still works"


def test_null_until_means_indefinite() -> None:
    """
    ⚠ The convention that has bitten elsewhere in this codebase. Read it as
    "expired" and every permanent suspension lifts itself silently.
    """
    source = inspect.getsource(practice._suspended)
    assert "until is None" in source
    assert "return row" in source
    doc = practice._suspended.__doc__ or ""
    assert "indefinite" in doc.lower()

    model = inspect.getsource(PracticeStrike)
    assert "indefinite" in model.lower()


def test_the_author_is_told_what_happened_to_their_writing() -> None:
    source = inspect.getsource(practice.one)
    assert "work.hidden and not mine" in source, (
        "a hidden work 404s for its own author too, so their writing vanishes "
        "with no explanation and the room appears to have eaten it"
    )
    shape = inspect.getsource(practice._work_json)
    assert '"hiddenBy"' in shape, "the reason is not sent, so nothing can say it"


def test_hidden_by_can_tell_the_three_apart() -> None:
    model = inspect.getsource(PracticeWork)
    for who in ("reports", "her", "author"):
        assert who in model, f"hidden_by cannot record `{who}`"


def test_a_report_from_discord_needs_no_account() -> None:
    model = inspect.getsource(PracticeReport)
    assert "from_discord" in model, (
        "half the room reads in Discord; with no way for them to report, the "
        "bridge is a place where nothing can be said to be wrong"
    )
