# SPDX-License-Identifier: AGPL-3.0-only
"""
The practice room's shape.

The rules worth pinning are the ones that would look fine while being wrong.

**A WORK is the unit.** Twelve signs for a week is one piece of work — her
words, "submitted, read and voted on as one". If a draft ever produced one work
per sign, everything would still function: people would write, submit and vote.
It would just quietly turn one person's week into twelve entries and make her
"highest voted" list meaningless.

**One vote per person, enforced by the database.** A check-then-insert counts two
taps on a slow connection twice, and that number is what she picks readings from.

**A draft is private.** The only thing separating one from a submission is a
null `submitted_at`, so every query serving other people has to filter on it.
"""
from __future__ import annotations

import inspect

from shruti.api.routes import practice
from shruti.models.practice import (
    PracticeComment, PracticeReading, PracticeVote, PracticeWork,
)


def test_one_draft_per_person_per_period() -> None:
    """
    The unique index is what keeps a week one piece of work. Without it, a
    second draft row would appear and somebody's twelve signs would silently
    split in two.
    """
    from pathlib import Path

    migration = (
        Path(__file__).resolve().parents[1]
        / "alembic" / "versions" / "d5b82e3f1a47_horoscope_practice.py"
    ).read_text()
    assert "ux_practice_draft" in migration
    assert "submitted_at IS NULL" in migration, (
        "the draft index is not partial — it would then forbid a second "
        "SUBMITTED work for the same week, which is a thing people do"
    )


def test_a_vote_is_unique_in_the_database() -> None:
    from pathlib import Path

    migration = (
        Path(__file__).resolve().parents[1]
        / "alembic" / "versions" / "d5b82e3f1a47_horoscope_practice.py"
    ).read_text()
    assert "ux_practice_vote_once" in migration


def test_the_vote_route_survives_losing_the_race() -> None:
    """
    Two taps arrive together, the database refuses the second, and the person
    must still end up with a vote rather than an error.
    """
    source = inspect.getsource(practice.vote)
    assert "IntegrityError" in source, (
        "vote() no longer handles the unique violation — a double tap will "
        "show somebody an error for a vote that was in fact counted"
    )


def test_an_author_cannot_vote_for_their_own_work() -> None:
    source = inspect.getsource(practice.vote)
    assert "work.user_id == user.id" in source


def test_every_route_that_serves_others_hides_drafts() -> None:
    """
    A draft is written, kept, and shown to nobody. The only thing marking one is
    a null `submitted_at`, which is easy to forget in a new query.
    """
    for name in ("feed", "one", "vote", "comment"):
        source = inspect.getsource(getattr(practice, name))
        assert "submitted_at" in source, (
            f"{name}() does not mention submitted_at — it will serve drafts"
        )


def test_hiding_is_not_deleting() -> None:
    """A comment thread that loses its subject is people talking about nothing."""
    assert hasattr(PracticeWork, "hidden")
    assert hasattr(PracticeComment, "hidden")
    source = inspect.getsource(practice.hide)
    assert "session.delete" not in source


def test_posting_needs_an_account_and_reading_does_not() -> None:
    """Her decision: identity, banning and traceability at the price of friction."""
    assert "raise HTTPException(401" in inspect.getsource(practice._reader)
    for name in ("save_draft", "submit", "vote", "comment"):
        assert "_reader(" in inspect.getsource(getattr(practice, name)), name
    # The feed asks who is looking, to mark their own votes, but never demands.
    feed = inspect.getsource(practice.feed)
    assert "current_user" in feed and "_reader(" not in feed


def test_blank_readings_are_dropped_at_submission() -> None:
    source = inspect.getsource(practice.submit)
    assert "session.delete" in source and "strip()" in source


def test_the_tables_are_shaped_the_way_the_room_needs() -> None:
    assert PracticeReading.__tablename__ == "practice_reading"
    assert PracticeVote.__tablename__ == "practice_vote"
    # A reading belongs to a work, never straight to a person: that is what
    # makes a series one thing.
    assert "work_id" in PracticeReading.model_fields
    assert "user_id" not in PracticeReading.model_fields
