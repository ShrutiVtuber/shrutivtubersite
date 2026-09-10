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

    # ⚠ WHY it went, not just that it did. A takedown by three strangers and a
    # decision of hers are undone differently — the first is provisional and
    # waiting for her, the second is settled — and "hidden" alone cannot tell
    # them apart. Empty while it is up.
    hidden_by: str = ""          # reports | her | author


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

    # ⚠ Null for a vote arriving over the Discord bridge, where there is no
    # site account. `from_discord` carries who Discord says it was, and the
    # uniqueness that makes one vote one vote holds on both halves separately.
    #
    # ⚠ Never merged with a site account. Somebody who votes in Discord and
    # also has an account can vote twice — that is the honest answer, because
    # the bridge cannot know they are the same person and inventing a link
    # between a Discord id and an email is a claim about somebody this app
    # cannot support.
    user_id: Optional[int] = Field(
        default=None, index=True, foreign_key="site_user.id")
    from_discord: str = ""


class PracticeComment(TimestampMixin, table=True):
    """What somebody said about a piece of work."""

    __tablename__ = "practice_comment"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id")

    # ⚠ Null for a comment bridged from Discord — see `from_discord` below.
    # Exactly one of the two is set, and the database says so.
    user_id: Optional[int] = Field(
        default=None, index=True, foreign_key="site_user.id")

    # ⚠ **Which reading this is about, or the whole work.** Empty means the
    # set: "this week reads well as a series", which is a real thing to say
    # about twelve signs and is not the same as saying it about Aries.
    #
    # A sign rather than a reading id, deliberately. A writer who deletes their
    # Aries draft and writes a new one has not made the comments about Aries
    # into comments about nothing — the reading is a new row, but the subject
    # of the conversation did not change.
    sign: str = Field(default="", index=True)

    body_md: str = ""
    # She removes a comment; the row stays so the thread keeps its shape.
    hidden: bool = False
    hidden_by: str = ""          # reports | her | author

    # ⚠ A comment bridged from Discord has no site account behind it: nobody
    # signed up, agreed to anything, or can be suspended. It carries the name
    # Discord gave it and is marked as what it is — never silently attributed
    # to somebody real.
    from_discord: str = ""


class PracticeReport(TimestampMixin, table=True):
    """
    Somebody said a piece of work, or a comment, should not be there.

    ⚠ **A report is not a verdict.** Three of them take the thing off view
    automatically, because leaving something up for hours while she sleeps is
    the failure that matters — but the row is a QUEUE ENTRY, not a decision.
    She sees every one, and either agrees or puts the work straight back.

    ⚠ **One report per person per thing**, enforced in the database. Otherwise
    one determined person is a takedown, and the auto-hide becomes a weapon
    rather than a stopgap.

    A reporter from Discord has no site account, so `user_id` is null and
    `from_discord` carries who it was. They still count — the alternative is a
    room where half the readers cannot say anything is wrong.
    """

    __tablename__ = "practice_report"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Exactly one of these is set. A report is about a work OR a comment.
    work_id: Optional[int] = Field(
        default=None, index=True, foreign_key="practice_work.id")
    comment_id: Optional[int] = Field(
        default=None, index=True, foreign_key="practice_comment.id")

    user_id: Optional[int] = Field(
        default=None, index=True, foreign_key="site_user.id")
    from_discord: str = ""

    # Chosen from a short list, so the queue can be read at a glance rather
    # than as a hundred free-text paragraphs.
    reason: str = Field(default="other", index=True)
    detail: str = ""

    # ⚠ Set when SHE has looked, never by the auto-hide. A report that hid
    # something and was never reviewed is exactly the state this column exists
    # to make visible.
    reviewed_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    outcome: str = ""            # upheld | dismissed


class PracticeStrike(TimestampMixin, table=True):
    """
    A suspension: this person may read, and may not post.

    ⚠ Deliberately not a ban. A ban is `BannedEmail` and follows a deletion; a
    suspension leaves the account and its writing intact and stops it adding
    more. Most moderation is a fortnight of silence, not an erasure, and having
    only the erasure available makes every decision too big to take.

    ⚠ **`until` is nullable and null means indefinite.** Same convention as the
    standing tests, and the same warning: read it as "not suspended" and a
    permanent suspension silently lifts itself.
    """

    __tablename__ = "practice_strike"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id")
    until: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    reason: str = ""
    lifted_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)


class PracticeBridge(TimestampMixin, table=True):
    """
    Which Discord message is which piece of work.

    ⚠ Without this a reaction is a number on a message nothing can attribute,
    and a reply is a comment on nothing. The bot posts the announcement and
    tells the site the message id; every vote and comment arriving from the
    channel is matched back through here.
    """

    __tablename__ = "practice_bridge"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: int = Field(index=True, foreign_key="practice_work.id")
    message_id: str = Field(index=True, unique=True)
    channel_id: str = ""

    # ⚠ **Which sign's message this is, or the announcement itself.** Empty is
    # the announcement — a reply to it is about the whole set.
    #
    # Discord cannot nest threads: a thread hangs off a message in a CHANNEL,
    # and a message inside a thread cannot have one of its own. So a submission
    # is one announcement, one thread, and one message per sign inside it, and
    # this column is what makes a reply to the Taurus message a comment on
    # Taurus rather than on the week.
    sign: str = Field(default="", index=True)

    # The thread the per-sign messages live in. Kept so a later reading added
    # to an existing work can be posted into the thread that already exists
    # rather than starting a second one.
    thread_id: str = Field(default="", index=True)
