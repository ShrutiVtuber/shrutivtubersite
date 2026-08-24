"""Schedule, contact and the question box."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.db import get_session
from shruti.models import ContactMessage, Question, ScheduleEntry

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

    session.add(
        ContactMessage(
            kind=payload.kind,
            name=payload.name,
            email=str(payload.email),
            subject=payload.subject,
            body=payload.body,
            source_ip=request.headers.get("X-Real-IP", request.client.host if request.client else ""),
        )
    )
    await session.commit()
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
    session.add(Question(body=payload.body, asked_by=payload.asked_by))
    await session.commit()
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
