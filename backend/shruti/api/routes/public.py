"""Schedule, contact and the question box."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core import counters as counters_core
from shruti.core.db import get_session
from shruti.core.mail import send
from shruti.models import ContactMessage, Counter, Question, ScheduleEntry

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/schedule")
async def get_schedule(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Upcoming streams in UTC. Conversion to the visitor's timezone happens in the
    browser — you author in Athens time and nobody else does the arithmetic.
    """
    now = datetime.now(timezone.utc)
    rows = (
        await session.execute(
            select(ScheduleEntry)
            .where(
                ScheduleEntry.visible.is_(True),
                ScheduleEntry.starts_at >= now - timedelta(hours=6),
            )
            .order_by(ScheduleEntry.starts_at)
            .limit(20)
        )
    ).scalars().all()

    return [
        {
            "title": e.title,
            "startsAt": e.starts_at.astimezone(timezone.utc).isoformat(),
            "durationMinutes": e.duration_minutes,
            "platform": e.platform,
            "url": e.url,
            "notesMd": e.notes_md,
        }
        for e in rows
    ]


class ContactIn(BaseModel):
    kind: str = Field(default="general", pattern="^(general|business)$")
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(default="", max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    # Honeypot: a real person never fills this; bots fill everything.
    website: str = ""


@router.post("/contact", status_code=202)
async def post_contact(
    payload: ContactIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if payload.website:
        # Silently accept so the bot doesn't learn it was caught.
        return {"status": "accepted"}

    message = ContactMessage(
        kind=payload.kind,
        name=payload.name,
        email=str(payload.email),
        subject=payload.subject,
        body=payload.body,
        source_ip=request.headers.get("X-Real-IP", request.client.host if request.client else ""),
    )
    session.add(message)
    # Commit BEFORE attempting the send. The database is the source of truth:
    # if Resend is down or misconfigured the message is still on disk and can
    # be re-sent. A form that loses what someone typed because a third party
    # had an outage is worse than a form with no email at all.
    await session.commit()

    result = await send(
        subject=f"[{payload.kind}] {payload.subject or 'Message from the site'}",
        body=(
            f"From: {payload.name} <{payload.email}>\n"
            f"Kind: {payload.kind}\n\n"
            f"{payload.body}\n"
        ),
        # Their address goes in Reply-To, never in From — putting it in From
        # fails SPF for their domain and gets the mail filed as spam.
        reply_to=str(payload.email),
    )
    if not result.sent:
        log.warning("contact message %s stored but not mailed: %s",
                    message.id, result.error)

    # The visitor's experience does not depend on the send succeeding.
    return {"status": "accepted"}


class QuestionIn(BaseModel):
    body: str = Field(min_length=3, max_length=1000)
    asked_by: str = Field(default="", max_length=80)
    website: str = ""


@router.post("/questions", status_code=202)
async def post_question(
    payload: QuestionIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if payload.website:
        return {"status": "accepted"}

    question = Question(body=payload.body, asked_by=payload.asked_by)
    session.add(question)
    await session.commit()

    # A notification, not the question itself in a queue somewhere else.
    await send(
        subject="A new question was asked",
        body=(f"{payload.asked_by or 'Anonymous'} asked:\n\n{payload.body}\n\n"
              f"Nothing is public until you approve it.\n"),
    )
    return {"status": "accepted"}


@router.get("/questions")
async def list_questions(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Only approved and answered questions are ever public."""
    rows = (
        await session.execute(
            select(Question)
            .where(Question.approved.is_(True), Question.answered_at.is_not(None))
            .order_by(Question.answered_at.desc())
            .limit(50)
        )
    ).scalars().all()
    return [
        {
            "body": q.body,
            "askedBy": q.asked_by,
            "answeredMd": q.answered_md,
            "answeredAt": q.answered_at.isoformat() if q.answered_at else None,
        }
        for q in rows
    ]


@router.get("/counters")
async def public_counters(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    The counters she has chosen to show, and where they have got to.

    The same numbers the overlay draws, minus the token: what is on the stream
    is already public, and a reader who arrives from a clip should be able to
    see the goal they just watched someone fill. `visible` is the switch —
    a counter she is keeping to herself does not appear here.

    Contributor counts are included; individual supporters are not. Who gave is
    hers to show on her own stream, not a list this route hands to anyone who
    asks.
    """
    rows = (
        await session.execute(
            select(Counter)
            .where(Counter.visible == True)  # noqa: E712 — SQL, not Python
            .order_by(Counter.position, Counter.id)
        )
    ).scalars().all()

    out = []
    for c in rows:
        p = await counters_core.progress(session, c)
        out.append({
            "slug": c.slug,
            "name": c.name,
            "note": c.note,
            "unit": c.unit,
            "currency": c.currency,
            "target": c.target,
            # Uncapped, exactly as the overlay gets it. Clamping at the target
            # would throw away the overrun, which is the best thing that can
            # happen to a goal.
            "current": p["current"],
            "contributors": p["contributors"],
            "startsAt": c.starts_at.isoformat() if c.starts_at else None,
            "endsAt": c.ends_at.isoformat() if c.ends_at else None,
        })
    return out


@router.get("/sky")
async def public_sky(lat: float = 37.9838, lon: float = 23.7275) -> dict:
    """
    The same sky the overlay draws, without the token.

    It is the same function behind both, deliberately. Two code paths computing
    where the Moon is would eventually disagree, and the one that disagreed
    would be the one on the stream — discovered by somebody in chat.
    """
    from shruti.api.routes.overlay import sky_now

    return await sky_now(lat, lon)
