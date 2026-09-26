# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio: what the Carnatic music school keeps about a person, and the
review state of its data.

The FACTS (ragas, talas, lessons, instruments) are not here. They are files
built from the private research repository by
`scripts/sync-carnatic-data.sh` and read from a volume
(`api/routes/carnatic.py`). These tables hold only what people chose and
made — settings, progress, practice time, songs, posts — and which of the
data's script names and flagged facts a reviewer has checked.

⚠ **Everything that is a person's goes with their account.** Every foreign
key to `site_user` here is ON DELETE CASCADE from the first migration
(n2l8i5j1k187, `NOBODYS_BUT_THEIRS`), and every table is in the account
export (`accounts._everything_else`). A published song sheet or a Listen post
is removed with the account rather than kept anonymised: they are a person's
own performances and compositions, nobody else's work builds on them, and the
composer says so where it publishes. (The site's publishing agreement, which
keeps guides and readings up without a name, is not asked for here.)

⚠ **No streaks.** The practice log counts seconds per day. There is no column
from which "you missed N days" could be computed cheaply, and none should be
added.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from shruti.models import TimestampMixin, UTC_TS


class CarnaticProfile(TimestampMixin, table=True):
    """A person's school settings: language, instrument, Sa, drone. One row each."""

    __tablename__ = "carnatic_profile"

    user_id: int = Field(primary_key=True, foreign_key="site_user.id", ondelete="CASCADE")
    settings: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))


class CarnaticProgress(TimestampMixin, table=True):
    """Which speeds of one path item a person has finished. Speeds only ever grow."""

    __tablename__ = "carnatic_progress"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_carnatic_progress_item"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    item_id: str
    speeds: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))


class CarnaticPracticeDay(TimestampMixin, table=True):
    """Time practised on one of the person's own days. Time only; never a streak."""

    __tablename__ = "carnatic_practice_day"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_carnatic_practice_day"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    day: str                    # YYYY-MM-DD in the person's own zone, as their device said
    seconds: int = 0
    sessions: int = 0


class CarnaticSong(TimestampMixin, table=True):
    """A composition from the composer. Private until published as a sheet."""

    __tablename__ = "carnatic_song"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    slug: str = Field(index=True, unique=True)
    title: str = ""
    raga: str = ""
    tala: str = ""
    body: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    published: bool = Field(default=False, index=True)
    published_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class CarnaticPost(TimestampMixin, table=True):
    """A performance in Listen: a link to a player, loaded only when pressed."""

    __tablename__ = "carnatic_post"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    song_id: Optional[int] = Field(default=None, foreign_key="carnatic_song.id", ondelete="SET NULL")
    title: str
    instrument: str = ""
    raga: str = ""
    tala: str = ""
    player: str                 # youtube | soundcloud | vimeo | bandcamp
    url: str
    hidden: bool = Field(default=False, index=True)
    hidden_by: str = ""         # "" | her | author


class CarnaticLike(SQLModel, table=True):
    """One person liking one post. A like is a row; there is no count to forge."""

    __tablename__ = "carnatic_like"

    post_id: int = Field(primary_key=True, foreign_key="carnatic_post.id", ondelete="CASCADE")
    user_id: int = Field(primary_key=True, foreign_key="site_user.id", ondelete="CASCADE")
    created_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class CarnaticComment(TimestampMixin, table=True):
    """A comment on a Listen post."""

    __tablename__ = "carnatic_comment"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(index=True, foreign_key="carnatic_post.id", ondelete="CASCADE")
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    body: str
    hidden: bool = False


class CarnaticReport(TimestampMixin, table=True):
    """
    A member flagging a Listen post or comment for the operator to look at.

    One report per person per thing (a second press changes nothing), and a
    report hides nothing by itself: the review queue's Moderation tab lists
    reported items first, and hiding is her decision. It is the reporter's
    row, so it goes with the reporter's account.
    """

    __tablename__ = "carnatic_report"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_carnatic_report_post"),
        UniqueConstraint("user_id", "comment_id", name="uq_carnatic_report_comment"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    post_id: Optional[int] = Field(default=None, index=True, foreign_key="carnatic_post.id", ondelete="CASCADE")
    comment_id: Optional[int] = Field(default=None, index=True, foreign_key="carnatic_comment.id", ondelete="CASCADE")
    reason: str = ""


class CarnaticReview(TimestampMixin, table=True):
    """
    A reviewer's verdict on one item of the data: a script name a native reader
    has checked, or a flagged fact a consultant has confirmed.

    Keyed by a stable string (`script:janya:mohanam:ta`, `fact:venu:tara-D1`)
    rather than a row id, because the data is rebuilt from the research on
    every sync and has no ids of its own. A key with no row is unverified.
    """

    __tablename__ = "carnatic_review"

    key: str = Field(primary_key=True)
    status: str                 # confirmed | corrected
    text: Optional[str] = None  # the corrected spelling, for "corrected"
    note: str = ""
    reviewed_by: str = ""       # the operator who recorded it


class CarnaticDeviceLink(TimestampMixin, table=True):
    """
    A one-time code to sign in on the app from the website.

    Only hashes are kept: sha256 of the QR token and an HMAC of the typed code,
    so a copy of this table cannot be redeemed.
    """

    __tablename__ = "carnatic_device_link"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    token_hash: str = Field(index=True)
    code_hash: str = Field(index=True)
    expires_at: datetime = Field(sa_type=UTC_TS)
    used_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    revoked_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    method: str = ""            # qr | code, once used
    device_name: str = ""
    user_agent: str = ""
