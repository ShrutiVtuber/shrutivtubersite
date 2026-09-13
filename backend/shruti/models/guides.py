# SPDX-License-Identifier: AGPL-3.0-only
"""
Shruti's Guides: a game guide as a path, kept on the site.

A guide's CONTENT is one JSON document in the format defined by
`shrutisguides.format` (schema, validator, importer — the shared package in
the shrutisgametracker repository). This file holds what the site needs
AROUND that document: which game it belongs to, who wrote it, its versions
and their states, votes, reports, and whether she has featured it.

⚠ **Versions are the unit of state, not guides.** A guide has a published
version and, at most, one open draft — so a published guide can be edited
without the edit going live, and a rejected draft leaves the live version
alone. `Guide.published_version_id` points at the one that is served.

⚠ **Progress is keyed by step id, not by version.** A new version never
deletes anybody's progress; unknown step ids are kept and not shown. That is
the format's rule (docs/GUIDE-FORMAT.md) and it is why nothing here cascades
onto progress.

Votes, reports and blocks follow the practice room exactly, because a guide
is other people's writing put in front of readers and the same things go
wrong with it. Blocks are not duplicated at all: `PracticeBlock` is one person
blocking another, and a block is a block whatever they were reading.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from shruti.models import TimestampMixin, UTC_TS


class Game(TimestampMixin, table=True):
    """A game, so guides can be grouped and given art."""

    __tablename__ = "guide_game"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    # The variants a run can have, as the format declares them — kept here so
    # the landing page can say "Eternal · Seasonal" without opening a guide.
    variants: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    art_media_id: Optional[int] = Field(default=None, foreign_key="media.id")


class Guide(TimestampMixin, table=True):
    """One guide: its identity, its author, and which version is live."""

    __tablename__ = "guide"
    __table_args__ = (UniqueConstraint("game_id", "slug", name="uq_guide_game_slug"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(index=True, foreign_key="guide_game.id")
    slug: str = Field(index=True)
    title: str
    created_by: int = Field(index=True, foreign_key="site_user.id")

    # ⚠ The version that is served. Null means never published — a guide that
    # exists only as a draft. Not a foreign key, deliberately: the version
    # points at the guide already, and two-way keys on one pair of tables are
    # a migration ordering problem forever.
    published_version_id: Optional[int] = Field(default=None, index=True)

    # ⚠ Hers to set, from the admin. The landing page leads with these.
    featured: bool = Field(default=False, index=True)
    featured_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)

    # Same vocabulary as the practice room: reports | her | author.
    hidden: bool = False
    hidden_by: str = ""


class GuideVersion(TimestampMixin, table=True):
    """
    One body of the guide, and where it is in its life.

    states: draft → submitted → published, or submitted → sent_back → draft.
    A published version that is replaced becomes superseded and is kept, so a
    publish can be rolled back to it.
    """

    __tablename__ = "guide_version"
    __table_args__ = (UniqueConstraint("guide_id", "number", name="uq_guide_version_number"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    guide_id: int = Field(index=True, foreign_key="guide.id")
    number: int = Field(default=1)
    # The whole document, format 1. Validated on every save; a draft may be
    # saved with problems, but only a clean one can be submitted.
    body: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    state: str = Field(default="draft", index=True)
    # ⚠ Her note when sending a draft back. Shown to the author on the draft,
    # because "rejected" with no reason is the practice room's lesson again.
    note: str = ""
    # ⚠ Which tool wrote it: desk | agent | file. Her queue marks an agent's
    # draft, because "drafted by an agent" is a fact she wants in front of
    # her when she reads — and the rule that nothing an agent does publishes
    # is only checkable if the origin is kept.
    source: str = Field(default="desk")
    created_by: int = Field(index=True, foreign_key="site_user.id")
    submitted_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    published_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class GuideVote(TimestampMixin, table=True):
    """One person, one vote, one guide. Uniqueness in the database, as in the room."""

    __tablename__ = "guide_vote"
    __table_args__ = (UniqueConstraint("guide_id", "user_id", name="uq_guide_vote"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    guide_id: int = Field(index=True, foreign_key="guide.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")


class GuideReport(TimestampMixin, table=True):
    """
    Somebody said a guide should not be there. A queue entry, not a verdict —
    the practice room's rule, and its threshold, exactly.
    """

    __tablename__ = "guide_report"
    __table_args__ = (UniqueConstraint("guide_id", "user_id", name="uq_guide_report"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    guide_id: int = Field(index=True, foreign_key="guide.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")
    reason: str = Field(default="other", index=True)
    detail: str = ""
    reviewed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    outcome: str = ""            # upheld | dismissed


class GuideRun(TimestampMixin, table=True):
    """
    One person's progress through one guide — the spec's "character",
    generalised. A person may keep several runs of the same guide and
    switch between them.

    ⚠ Progress is keyed by step id and lives in JSON columns, so a new
    version of the guide never deletes any of it: ids the version no longer
    has are kept and shown greyed. `version_id` is the version the run last
    followed, for "this guide has a newer version" — never a constraint.

    ⚠ Only what a person SET is stored — done, skipped, later, ticks, the
    check-in. Locked, available and current are computed by the shared
    engine on every read, never written, so nothing here can disagree with
    the guide.
    """

    __tablename__ = "guide_run"

    id: Optional[int] = Field(default=None, primary_key=True)
    guide_id: int = Field(index=True, foreign_key="guide.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")
    version_id: Optional[int] = Field(default=None)
    name: str = ""
    variant: str = ""
    checkin: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # step id → {"state": done|skipped|later, "at": iso}
    steps: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # routine id → {"ticked": [item ids], "reset_at": iso}
    routines: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # track id → {"rank": n, "day_one": [ids], "counters": {id: n}}
    tracks: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # [{"text": …, "step": id|null, "at": iso}] — parked, never ordered by urgency, never expiring
    later: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    # One note per run, overwritten, never versioned.
    note: str = ""
    # step id → [links] the person edited on their own run
    link_overrides: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    # The last step done and when — drives the re-entry block after six hours.
    last_done: str = ""
    last_done_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    last_seen_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class Group(TimestampMixin, table=True):
    """
    A group has a goal and nothing else — no path, no steps, no schedule.
    The worked example is a stream crew pushing an empire to tier 5: a
    target, contributions, and the sigil's arcs as the tiers.

    ⚠ **Nobody is ranked and nobody is reminded.** Contributions are listed by
    size with "and N others" so a small one is never the bottom of a
    leaderboard; nothing here measures absence.
    """

    __tablename__ = "guide_group"

    id: Optional[int] = Field(default=None, primary_key=True)
    # The join code: six letters, spoken on stream. HEKATE.
    code: str = Field(index=True, unique=True)
    name: str
    goal: str = ""
    target: int = 0
    tiers: int = 5
    created_by: int = Field(index=True, foreign_key="site_user.id")
    closed: bool = False


class GroupMember(TimestampMixin, table=True):
    __tablename__ = "guide_group_member"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_member"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(index=True, foreign_key="guide_group.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")


class GroupContribution(TimestampMixin, table=True):
    """One number, given once. Never edited, never ranked."""

    __tablename__ = "guide_group_contribution"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(index=True, foreign_key="guide_group.id")
    user_id: int = Field(index=True, foreign_key="site_user.id")
    amount: int = 0
