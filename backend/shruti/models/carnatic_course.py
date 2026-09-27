# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio v2: the course, its exercises and recordings, and what a
learner keeps while working through it.

THE COURSE TEXT is Sophia's, written in the private course repository and
imported by `scripts/sync-carnatic-course.sh` (never committed here). Once
imported it is hers to edit in the Swara Studio admin, so an import must
never overwrite her edits: each row remembers the file version it was last
in step with (`base_hash`) and whether the admin copy has diverged
(`admin_edited`). A newer file for a diverged row is kept beside it
(`file_*`) and the admin says "a newer file version exists".

PER PERSON (lesson state, attempts, bests, cards, guesses) is theirs alone
and goes with the account (ON DELETE CASCADE, migration r6q2m9n5o521,
`NOBODYS_BUT_THEIRS`). A rubric answer is feedback on somebody else's work
and is kept without a name, like a comment. A member's recording
suggestion keeps its queue entry without a name.

⚠ No streaks: nothing here records consecutive days, and nothing should.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from shruti.models import TimestampMixin, UTC_TS


# ── the course (imported, then edited in the admin) ─────────────────────────

class CarnaticUnit(TimestampMixin, table=True):
    """A unit of the syllabus, with its lesson list (written or not)."""

    __tablename__ = "carnatic_unit"

    n: int = Field(primary_key=True)
    title: str = ""
    level: str = ""                 # foundations | intermediate | advanced | any time
    intro: str = ""
    # [{id, slug, title, minutes, level, after, tools, goals}] from SYLLABUS.md
    lessons: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))


class CarnaticLesson(TimestampMixin, table=True):
    """
    One lesson in one language. `front` is the YAML front matter as JSON and
    `body` the markdown, editor notes included (the API strips them).
    """

    __tablename__ = "carnatic_lesson"
    __table_args__ = (UniqueConstraint("slug", "lang", name="uq_carnatic_lesson_slug"),)

    id: str = Field(primary_key=True)          # U01.L01
    lang: str = Field(default="en", primary_key=True)
    slug: str = Field(index=True)
    unit: int = Field(index=True)
    order: int = 0
    status: str = Field(default="draft", index=True)   # draft | review | published
    revision: int = 1
    front: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    body: str = Field(default="", sa_column=Column(Text, nullable=False))
    # In step with the course repository?
    base_hash: str = ""             # the file version this copy started from
    admin_edited: bool = False      # diverged: imports no longer overwrite it
    edited_by: str = ""
    edited_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    # The newest file seen by an import, when it differs from base_hash.
    file_hash: str = ""
    file_front: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    file_body: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    file_seen_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    published_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class CarnaticLessonRevision(SQLModel, table=True):
    """Every saved version of a lesson: who changed what, when; restorable."""

    __tablename__ = "carnatic_lesson_revision"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: str = Field(index=True)
    lang: str = "en"
    revision: int = 1
    front: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    body: str = Field(default="", sa_column=Column(Text, nullable=False))
    source: str = "admin"           # import | admin | restore
    by: str = ""
    note: str = ""
    meaning_change: bool = False
    created_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class CarnaticExercise(TimestampMixin, table=True):
    """An exercise as FORMAT.md §4 defines it, kept as JSON with the writers' extensions."""

    __tablename__ = "carnatic_exercise"

    id: str = Field(primary_key=True)          # U01.L01.Q1, CP.U14
    unit: int = Field(index=True)
    lesson: str = Field(default="", index=True)
    kind: str = Field(default="quiz", index=True)
    data: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    base_hash: str = ""
    admin_edited: bool = False
    edited_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    file_hash: str = ""
    file_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))


class CarnaticGlossary(TimestampMixin, table=True):
    """A glossary term: one line, and the lesson that teaches it."""

    __tablename__ = "carnatic_glossary"

    slug: str = Field(primary_key=True)
    term: str = ""
    definition: str = ""
    lesson: str = ""
    # glossary.yaml's `forms`: what the reader matches in lesson text (FORMAT.md §3e)
    aliases: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    iso: str = ""                   # ISO 15919 form, shown on the glossary page
    source: str = ""                # a key from the teaching lesson's sources
    base_hash: str = ""
    admin_edited: bool = False
    file_hash: str = ""
    file_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))


class CarnaticRecording(TimestampMixin, table=True):
    """
    A reference recording (LISTENING.md §2). Everything arrives as a
    candidate; nothing is public until Sophia approves it.
    """

    __tablename__ = "carnatic_recording"

    id: str = Field(primary_key=True)          # mohanam-02, form-tanpura-02, or m-<n> for suggestions
    status: str = Field(default="candidate", index=True)   # candidate | approved | rejected | held | retired
    provider: str = ""              # youtube | soundcloud | vimeo | bandcamp | archive
    url: str = ""
    title: str = ""
    channel: str = ""
    uploader_kind: str = ""         # official-artist | label | broadcaster | institution | unofficial | …
    artists: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    instrument: str = ""
    composition: str = ""
    composer: str = ""
    form: str = Field(default="", index=True)
    raga: str = Field(default="", index=True)  # our raga id, when the recording is about a raga
    tala: str = ""
    page_says: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    listen_for: str = ""
    flags: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    duration: str = ""
    raw: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # Sophia's annotations
    clips: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    sections: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    beat_map: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    # Marks the ear trainer drills on (EAR_TRAINING.md PD.09, GM.07, TL.11):
    # {"transcriptions": [{start, end, sargam}], "gamakas": [{t, gamakas}], "korvais": [{start, landing}]}
    marks: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False, server_default="{}"))
    # Decisions
    reason: str = ""                # a rejection reason the suggester sees
    decided_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    approved_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    oembed_failures: int = 0
    # A member's suggestion: who, and their one line. Kept without a name if they leave.
    suggested_by: Optional[int] = Field(default=None, index=True, foreign_key="site_user.id", ondelete="SET NULL")
    suggestion: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    base_hash: str = ""
    admin_edited: bool = False


class CarnaticRagaFlag(TimestampMixin, table=True):
    """Per raga: may the synth play its phrases? (EAR_TRAINING.md §3). Hers to change."""

    __tablename__ = "carnatic_raga_flag"

    raga: str = Field(primary_key=True)
    synth_ok: bool = True
    note: str = ""


# ── per person ──────────────────────────────────────────────────────────────

class CarnaticLessonState(SQLModel, table=True):
    """Opened, completed (by the learner's own hand), and where they were reading."""

    __tablename__ = "carnatic_lesson_state"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_carnatic_lesson_state"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    lesson_id: str = Field(index=True)
    opened_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    completed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    position: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    updated_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class CarnaticAttempt(SQLModel, table=True):
    """One attempt at a quiz, checkpoint, tap task, drill session or review."""

    __tablename__ = "carnatic_attempt"
    __table_args__ = (UniqueConstraint("user_id", "client_id", name="uq_carnatic_attempt_client"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    client_id: str
    item_id: str = Field(index=True)
    kind: str = Field(index=True)   # quiz | checkpoint | tap | drill | review | guess
    started_at: datetime = Field(sa_type=UTC_TS)
    seconds: int = 0
    result: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))


class CarnaticBest(SQLModel, table=True):
    """The best result per item and skill, so the dashboard need not scan every attempt."""

    __tablename__ = "carnatic_best"
    __table_args__ = (UniqueConstraint("user_id", "item_id", "skill", name="uq_carnatic_best"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    item_id: str
    skill: str = ""
    best: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    previous: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    achieved_at: datetime = Field(sa_type=UTC_TS)


class CarnaticCard(SQLModel, table=True):
    """A review card (EAR_TRAINING.md §6): a Leitner box and the last five results."""

    __tablename__ = "carnatic_card"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_carnatic_card"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    key: str
    box: int = 0
    last_seen: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    next_due: Optional[datetime] = Field(default=None, sa_type=UTC_TS, index=True)
    recent: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))


class CarnaticGuess(SQLModel, table=True):
    """A committed raga guess on a recording (guess the raga). Never public."""

    __tablename__ = "carnatic_guess"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    recording_id: str = Field(index=True)
    guess: str = ""
    confidence: str = ""
    phrases: str = ""
    right: bool = False
    created_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


# ── community (the generalised practice model) ──────────────────────────────

class PracticePart(SQLModel, table=True):
    """
    One part of a work in a room other than the horoscope one: the sargam, the
    text, a link, one timestamped note, a guess (LISTENING.md §4d option 2).
    A comment's `sign` names the part it is about ("note:3").
    """

    __tablename__ = "practice_part"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id", ondelete="CASCADE")
    key: str = Field(index=True)
    body_md: str = Field(default="", sa_column=Column(Text, nullable=False))
    data: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))


class PracticeRubric(TimestampMixin, table=True):
    """One reader's rubric answers on one work. Shown only as totals; kept without a name."""

    __tablename__ = "practice_rubric"
    __table_args__ = (UniqueConstraint("work_id", "user_id", name="uq_practice_rubric"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id", ondelete="CASCADE")
    user_id: Optional[int] = Field(default=None, index=True, foreign_key="site_user.id", ondelete="SET NULL")
    answers: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
