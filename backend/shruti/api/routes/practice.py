# SPDX-License-Identifier: AGPL-3.0-only
"""
Horoscope practice: writing, submitting, reading, voting, saying so.

A place to put a reading in front of other people and be told what they think.
Her purpose for it, in her words: so people "can get feedback on their
interpretations, learn and grow as horoscope writers", and so she can pick the
highest-voted ones to read on stream.

**The unit is a WORK.** One reading or twelve; a series is one piece of work and
is voted on as one. See `shruti.models.practice`.

⚠ **An account is required to post.** Her decision, taken for identity, banning
and traceability. Reading the feed needs nothing.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.db import get_session
from shruti.models.accounts import User
from shruti.models.practice import (
    PracticeComment, PracticeReading, PracticeReport, PracticeStrike,
    PracticeVote, PracticeWork,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/practice", tags=["practice"])

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]
PERIODS = ["daily", "weekly", "monthly", "yearly"]

# ⚠ How many strangers it takes to put something out of sight until she looks.
#
# Three, and the number is a judgement rather than a constant: one is a
# heckler's veto, ten is nothing happening until morning. It is here, named,
# because whoever changes it should have to see this sentence.
REPORTS_TO_HIDE = 3

# The short list a report picks from. Free text is also taken, but the reason
# is what makes a queue of a hundred readable at a glance.
REPORT_REASONS = [
    "abuse",            # aimed at a person
    "hate",             # aimed at a group
    "sexual",           # explicit, or involving minors
    "spam",             # advertising, scraped text, flooding
    "self-harm",        # somebody who may need help rather than moderation
    "not-a-reading",    # off topic for the room
    "other",
]


async def _reader(request: Request, session: AsyncSession) -> User:
    """Who is posting. 401 rather than a silent anonymous write."""
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in to post — reading needs no account")
    return user


def _name(user: User | None) -> str:
    if user is None:
        return "somebody"
    return (user.display_name or "").strip() or user.email.split("@")[0]


async def _work_json(
    work: PracticeWork, session: AsyncSession, *, viewer: User | None,
    full: bool,
) -> dict:
    readings = (
        await session.execute(
            select(PracticeReading)
            .where(PracticeReading.work_id == work.id)
            .order_by(PracticeReading.id)
        )
    ).scalars().all()
    votes = (
        await session.execute(
            select(func.count()).select_from(PracticeVote)
            .where(PracticeVote.work_id == work.id)
        )
    ).scalar_one()
    mine = False
    if viewer is not None:
        mine = (
            await session.execute(
                select(PracticeVote).where(
                    PracticeVote.work_id == work.id,
                    PracticeVote.user_id == viewer.id,
                )
            )
        ).scalars().first() is not None

    author = await session.get(User, work.user_id)
    by_sign = sorted(readings, key=lambda r: SIGNS.index(r.sign)
                     if r.sign in SIGNS else 99)

    out = {
        "id": work.id,
        "author": _name(author),
        "authorId": work.user_id,
        "period": work.period,
        "covers": work.covers,
        "title": work.title or "",
        # A series is one piece of work; the shape is a fact about it, not a
        # separate kind of thing to store.
        "series": len(readings) > 1,
        "signs": [r.sign for r in by_sign],
        "votes": votes,
        "voted": mine,
        "submittedAt": work.submitted_at.isoformat() if work.submitted_at else None,
        "mine": viewer is not None and viewer.id == work.user_id,
        # ⚠ The author is told, and told WHY. Somebody whose writing vanished
        # with no explanation concludes the room ate it; "three people reported
        # this and she has not looked yet" is a different sentence, and it is
        # the true one.
        "hidden": work.hidden,
        "hiddenBy": work.hidden_by,
    }
    if full:
        out["readings"] = [
            {"sign": r.sign, "bodyMd": r.body_md} for r in by_sign
        ]
    else:
        # Enough to decide whether to open it, without shipping a week of prose
        # for every card in the feed.
        first = by_sign[0] if by_sign else None
        out["opening"] = (first.body_md or "")[:240] if first else ""
    return out


# ── writing ─────────────────────────────────────────────────────────────────

class DraftIn(BaseModel):
    period: str = "weekly"
    covers: str = Field(default="", max_length=32)
    sign: str
    body_md: str = Field(default="", max_length=8000)
    title: str = Field(default="", max_length=120)


@router.put("/draft")
async def save_draft(
    body: DraftIn, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep what somebody is writing, against their account.

    ⚠ One draft per person per period, which is why the unique index exists.
    The website's desk saves here as they type, so their drafts follow them to
    the app instead of living in one browser — and a second draft row for the
    same week would mean their words silently splitting in two.
    """
    user = await _reader(request, session)
    if body.sign not in SIGNS:
        raise HTTPException(400, "no such sign")
    if body.period not in PERIODS:
        raise HTTPException(400, "no such period")

    work = (
        await session.execute(
            select(PracticeWork).where(
                PracticeWork.user_id == user.id,
                PracticeWork.period == body.period,
                PracticeWork.covers == body.covers,
                PracticeWork.submitted_at.is_(None),
            )
        )
    ).scalars().first()
    if work is None:
        work = PracticeWork(
            user_id=user.id, period=body.period, covers=body.covers,
            title=body.title,
        )
        session.add(work)
        await session.flush()
    elif body.title:
        work.title = body.title

    reading = (
        await session.execute(
            select(PracticeReading).where(
                PracticeReading.work_id == work.id,
                PracticeReading.sign == body.sign,
            )
        )
    ).scalars().first()
    if reading is None:
        session.add(PracticeReading(
            work_id=work.id, sign=body.sign, body_md=body.body_md))
    else:
        reading.body_md = body.body_md

    await session.commit()
    return {"ok": True, "workId": work.id}


@router.get("/draft")
async def read_draft(
    request: Request, period: str = "weekly", covers: str = "", sign: str = "",
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    What this account already holds for one sign of one period.

    ⚠ Declared ABOVE `/{work_id}`, or that catch-all answers for "draft" and a
    404 arrives where a draft should. The admin router has the same note and
    the same trap has been sprung there three times.

    Answers `{"bodyMd": ""}` for somebody signed out rather than 401: the
    writing desk is public, and a tool that errors at people who have not signed
    in is a tool they close.
    """
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None or sign not in SIGNS:
        return {"bodyMd": "", "workId": None}

    work = (
        await session.execute(
            select(PracticeWork).where(
                PracticeWork.user_id == user.id,
                PracticeWork.period == period,
                PracticeWork.covers == covers,
                PracticeWork.submitted_at.is_(None),
            )
        )
    ).scalars().first()
    if work is None:
        return {"bodyMd": "", "workId": None}

    reading = (
        await session.execute(
            select(PracticeReading).where(
                PracticeReading.work_id == work.id, PracticeReading.sign == sign)
        )
    ).scalars().first()
    return {"bodyMd": reading.body_md if reading else "", "workId": work.id}


@router.post("/{work_id}/submit")
async def submit(
    work_id: int, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Put it in front of other people.

    ⚠ Empty readings are dropped at this moment rather than kept. Somebody who
    opened all twelve signs and wrote three is submitting three, and shipping
    nine blanks would waste every reader's time.
    """
    user = await _reader(request, session)
    # ⚠ A suspension bites HERE, where writing enters the room, and nowhere
    # else. Somebody suspended keeps reading, keeps their drafts and keeps
    # everything they have already written — a suspension is a fortnight of
    # silence, not an erasure, and blocking the draft endpoint too would take
    # their unfinished writing with it.
    await _refuse_if_suspended(session, user)
    work = await session.get(PracticeWork, work_id)
    if work is None or work.user_id != user.id:
        raise HTTPException(404, "no such work")
    if work.submitted_at is not None:
        raise HTTPException(409, "that has already been submitted")

    readings = (
        await session.execute(
            select(PracticeReading).where(PracticeReading.work_id == work.id)
        )
    ).scalars().all()
    written = [r for r in readings if r.body_md.strip()]
    if not written:
        raise HTTPException(422, "there is nothing written to submit yet")
    for empty in (r for r in readings if not r.body_md.strip()):
        await session.delete(empty)

    work.submitted_at = datetime.now(timezone.utc)
    await session.commit()

    # ⚠ After the commit, and it must not be able to fail the submission. They
    # wrote it and it is saved; the channel catching up late — or not at all —
    # is a smaller thing than losing somebody's work to a Discord outage.
    await _tell_discord(await _work_json(work, session, viewer=user, full=False))

    return {"ok": True, "id": work.id, "signs": len(written)}


async def _tell_discord(work: dict) -> None:
    """
    Let the practice channel know, if there is one.

    The bot owns every fact about Discord — the token, the channel, the shape of
    a message. This says only that something was submitted, to an endpoint that
    refuses anybody without the shared secret.
    """
    import os

    import httpx

    bot = os.environ.get("VCORDBOT_INTERNAL_URL", "").strip()
    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    if not (bot and secret):
        return                      # no bridge configured; a working state
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                f"{bot}/internal/practice",
                json={
                    "id": work["id"], "author": work["author"],
                    "title": work.get("title", ""), "signs": work.get("signs", []),
                    "opening": work.get("opening", ""),
                },
                headers={"X-Shruti-Internal": secret},
            )
    except Exception as exc:                       # noqa: BLE001
        log.warning("practice channel not told: %s", type(exc).__name__)


@router.get("/mine")
async def mine(
    request: Request, session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Everything this person has written, drafts first."""
    user = await _reader(request, session)
    works = (
        await session.execute(
            select(PracticeWork)
            .where(PracticeWork.user_id == user.id)
            .order_by(PracticeWork.submitted_at.is_(None).desc(),
                      PracticeWork.updated_at.desc())
        )
    ).scalars().all()
    return [await _work_json(w, session, viewer=user, full=False) for w in works]


# ── reading what others wrote ───────────────────────────────────────────────

@router.get("")
async def feed(
    request: Request,
    sort: str = "recent",
    period: str = "",
    covers: str = "",
    limit: int = 30,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    What has been submitted. No account needed to read.

    `sort=top` is what she reads from — the highest voted for a period, which is
    the whole point of the votes.
    """
    from shruti.api.routes.accounts import current_user

    viewer = await current_user(request, session)
    q = (
        select(PracticeWork)
        .where(PracticeWork.submitted_at.is_not(None))
        .where(PracticeWork.hidden.is_(False))
    )
    if period:
        q = q.where(PracticeWork.period == period)
    if covers:
        q = q.where(PracticeWork.covers == covers)

    if sort == "top":
        votes = (
            select(PracticeVote.work_id, func.count().label("n"))
            .group_by(PracticeVote.work_id).subquery()
        )
        q = (q.join(votes, votes.c.work_id == PracticeWork.id, isouter=True)
              .order_by(func.coalesce(votes.c.n, 0).desc(),
                        PracticeWork.submitted_at.desc()))
    else:
        q = q.order_by(PracticeWork.submitted_at.desc())

    works = (await session.execute(q.limit(min(limit, 100)))).scalars().all()
    return [await _work_json(w, session, viewer=viewer, full=False) for w in works]


@router.get("/{work_id}")
async def one(
    work_id: int, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.api.routes.accounts import current_user

    viewer = await current_user(request, session)
    work = await session.get(PracticeWork, work_id)
    if work is None:
        raise HTTPException(404, "no such work")
    # A draft is nobody's business but its author's.
    mine = viewer is not None and viewer.id == work.user_id
    if work.submitted_at is None and not mine:
        raise HTTPException(404, "no such work")
    # ⚠ Hidden is 404 for everybody EXCEPT its author, who gets it with the
    # reason attached. Hiding somebody's writing from themselves adds nothing:
    # they wrote it, they still have it, and they are the one person who needs
    # to know what happened to it.
    if work.hidden and not mine:
        raise HTTPException(404, "no such work")

    out = await _work_json(work, session, viewer=viewer, full=True)
    comments = (
        await session.execute(
            select(PracticeComment, User)
            .join(User, User.id == PracticeComment.user_id, isouter=True)
            .where(PracticeComment.work_id == work.id)
            .where(PracticeComment.hidden.is_(False))
            .order_by(PracticeComment.created_at)
        )
    ).all()
    out["comments"] = [
        {
            "id": c.id,
            # ⚠ A bridged comment carries the name Discord gave it and says so.
            # It is never attributed to a site account, because there is not
            # one behind it — nobody signed up, agreed to anything, or can be
            # suspended.
            "author": c.from_discord or _name(u),
            "fromDiscord": bool(c.from_discord),
            "bodyMd": c.body_md,
            "at": c.created_at.isoformat() if c.created_at else None,
            "mine": viewer is not None and viewer.id == c.user_id,
        }
        for c, u in comments
    ]
    return out


# ── saying what you think ───────────────────────────────────────────────────

@router.post("/{work_id}/vote")
async def vote(
    work_id: int, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    One person, one vote — and pressing it again takes it back.

    ⚠ The uniqueness is the database's. A check-then-insert would count two
    taps on a slow connection twice, and this is the number she picks readings
    from.
    """
    user = await _reader(request, session)
    work = await session.get(PracticeWork, work_id)
    if work is None or work.submitted_at is None or work.hidden:
        raise HTTPException(404, "no such work")
    if work.user_id == user.id:
        raise HTTPException(403, "voting for your own work is not a vote")

    existing = (
        await session.execute(
            select(PracticeVote).where(
                PracticeVote.work_id == work_id, PracticeVote.user_id == user.id)
        )
    ).scalars().first()
    if existing is not None:
        await session.delete(existing)
        await session.commit()
        voted = False
    else:
        session.add(PracticeVote(work_id=work_id, user_id=user.id))
        try:
            await session.commit()
            voted = True
        except IntegrityError:
            # The other tap won. Their vote counts; this one is not a second.
            await session.rollback()
            voted = True

    total = (
        await session.execute(
            select(func.count()).select_from(PracticeVote)
            .where(PracticeVote.work_id == work_id)
        )
    ).scalar_one()
    return {"ok": True, "voted": voted, "votes": total}


class CommentIn(BaseModel):
    body_md: str = Field(min_length=1, max_length=4000)


@router.post("/{work_id}/comments", status_code=201)
async def comment(
    work_id: int, body: CommentIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    work = await session.get(PracticeWork, work_id)
    if work is None or work.submitted_at is None or work.hidden:
        raise HTTPException(404, "no such work")

    row = PracticeComment(
        work_id=work_id, user_id=user.id, body_md=body.body_md.strip())
    session.add(row)
    await session.commit()

    # ⚠ Their own comment must not wake their own phone. Somebody saying
    # something on their own work is not news to them, and being notified about
    # yourself is the fastest way to turn notifications off.
    if work.user_id != user.id:
        try:
            from shruti.core.notify import tell

            await tell(
                session, "replies",
                title="Somebody read your reading",
                body=f"{_name(user)} said something about it.",
                url=f"/practice/{work_id}",
                to_user=work.user_id,
            )
        except Exception as exc:                   # noqa: BLE001
            log.warning("could not tell the author: %s", type(exc).__name__)

    return {"ok": True, "id": row.id, "author": _name(user)}


@router.delete("/comments/{comment_id}", status_code=204)
async def remove_comment(
    comment_id: int, request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Somebody taking back what they said. She removes things elsewhere."""
    user = await _reader(request, session)
    row = await session.get(PracticeComment, comment_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "no such comment")
    row.hidden = True
    await session.commit()


# ── saying something is wrong ───────────────────────────────────────────────

class ReportIn(BaseModel):
    reason: str = Field(default="other", max_length=32)
    detail: str = Field(default="", max_length=1000)


async def _suspended(session: AsyncSession, user_id: int) -> PracticeStrike | None:
    """
    The suspension in force, or None.

    ⚠ `until` NULL means indefinite, not "expired". Reading it the other way
    round lifts every permanent suspension silently, which is the failure that
    matters here — the one nobody notices until the person is posting again.
    """
    now = datetime.now(timezone.utc)
    rows = (
        await session.execute(
            select(PracticeStrike)
            .where(PracticeStrike.user_id == user_id,
                   PracticeStrike.lifted_at.is_(None))
        )
    ).scalars().all()
    for row in rows:
        if row.until is None:
            return row
        until = row.until
        if until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
        if until > now:
            return row
    return None


async def _refuse_if_suspended(session: AsyncSession, user: User) -> None:
    """
    Say so, and say until when.

    ⚠ 403 with the reason, never a silent no-op. A room that accepts a
    submission and quietly drops it is worse than one that says no: the person
    thinks they posted, waits for a reply, and concludes nobody read it.
    """
    strike = await _suspended(session, user.id)
    if strike is None:
        return
    until = "for now" if strike.until is None else (
        f"until {strike.until.date().isoformat()}")
    raise HTTPException(
        403,
        f"Posting is paused on this account {until}."
        + (f" {strike.reason}" if strike.reason else "")
        + " You can still read, and everything you have written is still here.",
    )


async def _count_reports(session: AsyncSession, **where) -> int:
    return (
        await session.execute(
            select(func.count()).select_from(PracticeReport).filter_by(**where)
        )
    ).scalar_one()


@router.post("/{work_id}/report", status_code=201)
async def report_work(
    work_id: int, body: ReportIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Say a piece of work should not be there.

    ⚠ Three reports take it off view. That is a STOPGAP and not a verdict:
    leaving something up for eight hours because it arrived at three in the
    morning is the failure that actually matters, and a wrongly hidden reading
    is visible again in one tap of hers. Every report reaches her queue whether
    it hid anything or not.
    """
    user = await _reader(request, session)
    work = await session.get(PracticeWork, work_id)
    if work is None or work.submitted_at is None:
        raise HTTPException(404, "no such work")
    if work.user_id == user.id:
        raise HTTPException(
            403, "to take your own work down, withdraw it rather than report it")

    # ⚠ Read BEFORE the commit that may fail. A rollback expires every loaded
    # attribute, so `work.hidden` afterwards is a lazy refresh — IO from a
    # place SQLAlchemy's async layer cannot do it, which surfaces as
    # MissingGreenlet and a 500. The value is a bool; keep the bool.
    was_hidden = work.hidden

    reason = body.reason if body.reason in REPORT_REASONS else "other"
    session.add(PracticeReport(
        work_id=work_id, user_id=user.id,
        reason=reason, detail=body.detail.strip()))
    try:
        await session.commit()
    except IntegrityError:
        # ⚠ Already reported by this person. Answered as success on purpose:
        # telling somebody "you already reported this" invites them to find a
        # second account, and the honest answer to "is this reported?" is yes.
        await session.rollback()
        return {"ok": True, "hidden": was_hidden}

    total = await _count_reports(session, work_id=work_id)
    if total >= REPORTS_TO_HIDE and not was_hidden:
        work.hidden = True
        work.hidden_by = "reports"
        await session.commit()
        await _tell_her(session, work_id, total)

    return {"ok": True, "hidden": work.hidden}


@router.post("/comments/{comment_id}/report", status_code=201)
async def report_comment(
    comment_id: int, body: ReportIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """The same, for something somebody said."""
    user = await _reader(request, session)
    row = await session.get(PracticeComment, comment_id)
    if row is None:
        raise HTTPException(404, "no such comment")
    if row.user_id == user.id:
        raise HTTPException(403, "delete your own comment rather than report it")

    was_hidden = row.hidden       # see the note in report_work

    reason = body.reason if body.reason in REPORT_REASONS else "other"
    session.add(PracticeReport(
        comment_id=comment_id, user_id=user.id,
        reason=reason, detail=body.detail.strip()))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return {"ok": True, "hidden": was_hidden}

    total = await _count_reports(session, comment_id=comment_id)
    if total >= REPORTS_TO_HIDE and not was_hidden:
        row.hidden = True
        row.hidden_by = "reports"
        await session.commit()

    return {"ok": True, "hidden": row.hidden}


async def _tell_her(session: AsyncSession, work_id: int, total: int) -> None:
    """
    A takedown is the one moderation event worth a notification.

    ⚠ Fails soft. Something being hidden must not depend on a push service
    being up — it is already hidden by the time this runs.
    """
    try:
        from shruti.core.notify import tell

        await tell(
            session, "moderation",
            title="A reading was taken down by reports",
            body=f"{total} people reported it. It is off the feed until you look.",
            url="/admin/community?tab=reports",
            to_admin=True,
        )
    except Exception as exc:                       # noqa: BLE001
        log.warning("could not tell her about a takedown: %s",
                    type(exc).__name__)


@router.post("/{work_id}/withdraw", status_code=200)
async def withdraw(
    work_id: int, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    An author taking their own work back.

    ⚠ Marked as theirs, not as hers and not as a takedown. Somebody changing
    their mind about their own writing is not a moderation event and must not
    appear in a queue as though it were.
    """
    user = await _reader(request, session)
    work = await session.get(PracticeWork, work_id)
    if work is None or work.user_id != user.id:
        raise HTTPException(404, "no such work")
    work.hidden = True
    work.hidden_by = "author"
    await session.commit()
    return {"ok": True}


# ── hers ────────────────────────────────────────────────────────────────────

@router.get("/admin/to-read", dependencies=[Depends(require_admin)])
async def to_read(
    period: str = "weekly", covers: str = "", limit: int = 10,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    What to read on stream: the best of a period, votes and comments together.

    Her purpose for the votes, in her words — take "the highest voted/most
    commented each week and read them alongside my weekly horoscope writing
    streams so the community can hear what others are saying".

    ⚠ **Both counts, not votes alone.** A piece nobody voted for but six people
    argued about is exactly the one worth reading out; ranking on votes alone
    would bury it under whatever got shared the widest. A comment counts for
    two, because writing a sentence about somebody's work is more effort than
    tapping a heart.
    """
    votes = (
        select(PracticeVote.work_id, func.count().label("n"))
        .group_by(PracticeVote.work_id).subquery()
    )
    remarks = (
        select(PracticeComment.work_id, func.count().label("n"))
        .where(PracticeComment.hidden.is_(False))
        .group_by(PracticeComment.work_id).subquery()
    )
    q = (
        select(
            PracticeWork,
            func.coalesce(votes.c.n, 0).label("votes"),
            func.coalesce(remarks.c.n, 0).label("remarks"),
        )
        .join(votes, votes.c.work_id == PracticeWork.id, isouter=True)
        .join(remarks, remarks.c.work_id == PracticeWork.id, isouter=True)
        .where(PracticeWork.submitted_at.is_not(None))
        .where(PracticeWork.hidden.is_(False))
        .where(PracticeWork.period == period)
    )
    if covers:
        q = q.where(PracticeWork.covers == covers)
    q = q.order_by(
        (func.coalesce(votes.c.n, 0) + func.coalesce(remarks.c.n, 0) * 2).desc(),
        PracticeWork.submitted_at.desc(),
    ).limit(min(limit, 50))

    out = []
    for work, vote_count, remark_count in (await session.execute(q)).all():
        body = await _work_json(work, session, viewer=None, full=True)
        body["votes"] = vote_count
        body["comments"] = remark_count
        # What she would say out loud before reading it.
        author = await session.get(User, work.user_id)
        body["byline"] = _name(author)
        out.append(body)
    return out


@router.get("/admin/reports", dependencies=[Depends(require_admin)])
async def reports(
    session: AsyncSession = Depends(get_session), include_reviewed: bool = False,
) -> list[dict]:
    """
    What people have said should not be there.

    ⚠ Grouped by the thing reported, not listed one row per report. Three
    people reporting one reading is ONE decision to make; a list that shows it
    as three invites her to make it three times, and to disagree with herself.

    ⚠ Unreviewed first, and within that the ones that actually hid something.
    A report that took a reading off the feed and has been sitting for two days
    is the most expensive row in the table.
    """
    query = select(PracticeReport)
    if not include_reviewed:
        query = query.where(PracticeReport.reviewed_at.is_(None))
    rows = (await session.execute(
        query.order_by(PracticeReport.created_at.desc()))).scalars().all()

    # Group: one entry per subject.
    subjects: dict[tuple[str, int], dict] = {}
    for row in rows:
        key = ("work", row.work_id) if row.work_id else ("comment", row.comment_id)
        entry = subjects.setdefault(key, {
            "kind": key[0], "id": key[1], "reports": [], "reasons": {},
        })
        entry["reports"].append({
            "id": row.id,
            "reason": row.reason,
            "detail": row.detail,
            "at": row.created_at.isoformat() if row.created_at else "",
            "from_discord": row.from_discord,
            "reviewed": row.reviewed_at is not None,
            "outcome": row.outcome,
        })
        entry["reasons"][row.reason] = entry["reasons"].get(row.reason, 0) + 1

    out: list[dict] = []
    for (kind, subject_id), entry in subjects.items():
        if kind == "work":
            work = await session.get(PracticeWork, subject_id)
            if work is None:
                continue
            author = await session.get(User, work.user_id)
            entry["hidden"] = work.hidden
            entry["hidden_by"] = work.hidden_by
            entry["author"] = _name(author)
            entry["author_id"] = work.user_id
            entry["title"] = work.title
            entry["period"] = work.period
            entry["covers"] = work.covers
            readings = (await session.execute(
                select(PracticeReading).where(
                    PracticeReading.work_id == subject_id))).scalars().all()
            entry["signs"] = [r.sign for r in readings]
            entry["excerpt"] = (readings[0].body_md[:400] if readings else "")
        else:
            row = await session.get(PracticeComment, subject_id)
            if row is None:
                continue
            author = (await session.get(User, row.user_id)
                      if row.user_id else None)
            entry["hidden"] = row.hidden
            entry["hidden_by"] = row.hidden_by
            entry["author"] = row.from_discord or _name(author)
            entry["author_id"] = row.user_id
            entry["from_discord"] = bool(row.from_discord)
            entry["work_id"] = row.work_id
            entry["excerpt"] = row.body_md[:400]
        entry["count"] = len(entry["reports"])
        out.append(entry)

    # Hidden-and-unreviewed first: those are the ones costing somebody their
    # writing while they wait.
    out.sort(key=lambda e: (
        not (e["hidden"] and e["hidden_by"] == "reports"), -e["count"]))
    return out


class VerdictIn(BaseModel):
    # uphold  — she agrees; it stays down
    # dismiss — she does not; it goes straight back up
    outcome: str = Field(pattern="^(uphold|dismiss)$")
    suspend_days: int | None = None
    reason: str = Field(default="", max_length=500)


@router.post("/admin/reports/{kind}/{subject_id}",
             dependencies=[Depends(require_admin)])
async def decide(
    kind: str, subject_id: int, body: VerdictIn,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Her decision on one reported thing, and every report about it at once.

    ⚠ Dismissing PUTS IT BACK. A dismissal that only marks the report read
    would leave the auto-hide standing for ever — the thing would stay down
    because three strangers said so and she said they were wrong.
    """
    if kind not in {"work", "comment"}:
        raise HTTPException(404, "no such thing")

    if kind == "work":
        subject = await session.get(PracticeWork, subject_id)
        column = PracticeReport.work_id
    else:
        subject = await session.get(PracticeComment, subject_id)
        column = PracticeReport.comment_id
    if subject is None:
        raise HTTPException(404, "no such thing")

    upheld = body.outcome == "uphold"
    if upheld:
        subject.hidden = True
        subject.hidden_by = "her"
    else:
        # ⚠ Only if the REPORTS put it down. Her own earlier decision, or an
        # author withdrawing their work, is not undone by dismissing a report.
        if subject.hidden and subject.hidden_by == "reports":
            subject.hidden = False
            subject.hidden_by = ""

    now = datetime.now(timezone.utc)
    open_reports = (await session.execute(
        select(PracticeReport).where(
            column == subject_id, PracticeReport.reviewed_at.is_(None)))
    ).scalars().all()
    for row in open_reports:
        row.reviewed_at = now
        row.outcome = body.outcome

    suspended_until = None
    if upheld and body.suspend_days is not None:
        author_id = getattr(subject, "user_id", None)
        if author_id:
            # 0 days means indefinite — see the note on `until`.
            until = (None if body.suspend_days <= 0
                     else now + timedelta(days=body.suspend_days))
            session.add(PracticeStrike(
                user_id=author_id, until=until,
                reason=body.reason or "Reported writing in the practice room."))
            suspended_until = "indefinite" if until is None else until.isoformat()

    await session.commit()
    return {
        "ok": True, "hidden": subject.hidden, "reviewed": len(open_reports),
        "suspended_until": suspended_until,
    }


@router.get("/admin/strikes", dependencies=[Depends(require_admin)])
async def strikes(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Who is suspended, and until when."""
    rows = (await session.execute(
        select(PracticeStrike).where(PracticeStrike.lifted_at.is_(None))
        .order_by(PracticeStrike.created_at.desc()))).scalars().all()
    out = []
    for row in rows:
        who = await session.get(User, row.user_id)
        out.append({
            "id": row.id,
            "user_id": row.user_id,
            "who": _name(who),
            "email": who.email if who else "",
            # ⚠ Said in words, because "null" on a screen reads as "none" and
            # this null means the opposite of none.
            "until": row.until.isoformat() if row.until else "",
            "indefinite": row.until is None,
            "reason": row.reason,
            "since": row.created_at.isoformat() if row.created_at else "",
        })
    return out


@router.delete("/admin/strikes/{strike_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def lift(
    strike_id: int, session: AsyncSession = Depends(get_session),
) -> None:
    """Let them post again."""
    row = await session.get(PracticeStrike, strike_id)
    if row is None:
        raise HTTPException(404, "no such suspension")
    row.lifted_at = datetime.now(timezone.utc)
    await session.commit()


@router.post("/{work_id}/hide", dependencies=[Depends(require_admin)])
async def hide(
    work_id: int, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Take something off the feed.

    Hidden rather than deleted: a comment thread that loses its subject is a
    page of people talking about nothing.
    """
    work = await session.get(PracticeWork, work_id)
    if work is None:
        raise HTTPException(404, "no such work")
    work.hidden = not work.hidden
    await session.commit()
    return {"ok": True, "hidden": work.hidden}
