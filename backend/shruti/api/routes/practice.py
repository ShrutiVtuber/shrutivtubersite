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
from datetime import datetime, timezone

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
    PracticeComment, PracticeReading, PracticeVote, PracticeWork,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/practice", tags=["practice"])

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]
PERIODS = ["daily", "weekly", "monthly", "yearly"]


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
    if work is None or work.hidden:
        raise HTTPException(404, "no such work")
    # A draft is nobody's business but its author's.
    mine = viewer is not None and viewer.id == work.user_id
    if work.submitted_at is None and not mine:
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
            "id": c.id, "author": _name(u), "bodyMd": c.body_md,
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


# ── hers ────────────────────────────────────────────────────────────────────

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
