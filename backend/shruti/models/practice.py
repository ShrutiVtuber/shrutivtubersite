# SPDX-License-Identifier: AGPL-3.0-only
"""
Horoscope practice: what people write, and what others make of it.

She asked for a place where somebody learning to write horoscopes can put one
in front of other people, get told what they think, and improve — and where she
can pick the best ones to read on stream.

**A WORK is the unit.** Not a reading. Somebody writing all twelve signs for a
week is doing ONE piece of work, and her words were that a series should be
"submitted, read and voted on as one". So a work holds one reading or twelve,
and the votes and the comments attach to the work either way. A single reading
is not a special case here; it is a work that happens to hold one.

⚠ **A draft is a work with no `submitted_at`.** That is the whole of the
difference, and it is why the website's writing desk can save into this table
for a signed-in person: their drafts follow them between the site and the app
instead of living in one browser.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field

from shruti.models import TimestampMixin, UTC_TS


class PracticeWork(TimestampMixin, table=True):
    """One piece of work: a single reading, or a whole week of them."""

    __tablename__ = "practice_work"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id")

    # Which sky it was written for. Same vocabulary as her own readings, so a
    # practice piece and a published one are about the same period.
    period: str = Field(default="weekly", index=True)
    covers: str = Field(default="", index=True)

    # What the writer calls it. Optional — "Leo, week of 7 September" is a
    # perfectly good name and can be built from the work itself.
    title: str = ""

    # ⚠ Null means draft: written, kept, not shown to anybody. This is the only
    # thing separating a private draft from a public submission, so every query
    # that serves other people MUST filter on it.
    submitted_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)

    # Set when she takes it off — spam, or somebody asking for their work back.
    # Kept rather than deleted so a comment thread does not lose its subject.
    hidden: bool = False


class PracticeReading(TimestampMixin, table=True):
    """One sign's worth of writing, inside a work."""

    __tablename__ = "practice_reading"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id")
    sign: str = Field(index=True)
    body_md: str = ""


class PracticeVote(TimestampMixin, table=True):
    """
    One person, one vote, one work.

    ⚠ Uniqueness is enforced in the database, not by looking first. Two taps on
    a slow connection are two requests, and a check-then-insert would count
    both.
    """

    __tablename__ = "practice_vote"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")


class PracticeComment(TimestampMixin, table=True):
    """What somebody said about a piece of work."""

    __tablename__ = "practice_comment"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")
    body_md: str = ""
    # She removes a comment; the row stays so the thread keeps its shape.
    hidden: bool = False
