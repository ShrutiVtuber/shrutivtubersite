# SPDX-License-Identifier: AGPL-3.0-only
"""
The newsletter: double opt-in, one-click unsubscribe, and a preference centre.

**An unconfirmed address is not consent**, so nothing is ever sent to one.
**Unsubscribe takes one click and no login**, and the landing page does not
argue — no survey, no "are you sure", no win-back offer. It mentions pause
once, because a pause keeps more people than an unsubscribe loses and nothing
is deleted by it.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.consents import NEWSLETTER, CONSENT_VERSION
from shruti.core.db import get_session
from shruti.core.sessions import new_token
from shruti.models.accounts import ConsentRecord, Issue, Subscriber

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


class SubscribeIn(BaseModel):
    email: EmailStr
    consent: bool = False


@router.post("/subscribe", status_code=202)
async def subscribe(
    body: SubscribeIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if not body.consent:
        raise HTTPException(422, "the letter needs your agreement before it can be sent")

    email = body.email.lower().strip()
    row = (
        await session.execute(select(Subscriber).where(Subscriber.email == email))
    ).scalar_one_or_none()

    if row is None:
        row = Subscriber(
            email=email, confirm_token=new_token(), unsubscribe_token=new_token(),
        )
        session.add(row)
    elif row.unsubscribed_at is not None:
        # Coming back is a new decision, and a new confirmation.
        row.unsubscribed_at = None
        row.confirmed_at = None
        row.confirm_token = new_token()

    session.add(ConsentRecord(
        email=email, kind=NEWSLETTER.kind, granted=True, version=CONSENT_VERSION,
        wording=NEWSLETTER.wording, lawful_basis=NEWSLETTER.lawful_basis,
        source="newsletter-form",
    ))
    await session.commit()

    from shruti.api.routes.accounts import _send_optin
    await _send_optin(email, row.confirm_token, session)

    # The reply is the same whether or not the address was already known.
    return {"ok": True, "checkEmail": True}


@router.get("/confirm")
async def confirm(token: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = (
        await session.execute(select(Subscriber).where(Subscriber.confirm_token == token))
    ).scalar_one_or_none()
    if row is None or not token:
        raise HTTPException(400, "that confirmation link is not valid or has been used")

    row.confirmed_at = row.confirmed_at or datetime.now(timezone.utc)
    row.unsubscribed_at = None
    # Single use.
    row.confirm_token = ""
    await session.commit()
    return {"ok": True, "email": row.email, "unsubscribeToken": row.unsubscribe_token}


@router.get("/unsubscribe")
async def unsubscribe(token: str, session: AsyncSession = Depends(get_session)) -> dict:
    """
    One click, no login. The token is in every issue's footer.

    The unsubscribe token is NOT cleared: a second click on the same link must
    still work rather than erroring, because people click twice.
    """
    row = (
        await session.execute(select(Subscriber).where(Subscriber.unsubscribe_token == token))
    ).scalar_one_or_none()
    if row is None or not token:
        raise HTTPException(400, "that unsubscribe link is not valid")

    if row.unsubscribed_at is None:
        row.unsubscribed_at = datetime.now(timezone.utc)
        session.add(ConsentRecord(
            email=row.email, kind=NEWSLETTER.kind, granted=False,
            version=CONSENT_VERSION, wording=NEWSLETTER.wording,
            lawful_basis=NEWSLETTER.lawful_basis, source="unsubscribe-link",
        ))
        await session.commit()

    return {"ok": True, "email": row.email}


class PreferencesIn(BaseModel):
    token: str
    wants_horoscope: bool = True
    wants_videos: bool = True
    wants_streams: bool = True
    wants_articles: bool = True
    cadence: str = Field(default="monthly", pattern="^(monthly|paused)$")
    paused_until: str | None = None


@router.get("/preferences")
async def read_preferences(token: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = (
        await session.execute(select(Subscriber).where(Subscriber.unsubscribe_token == token))
    ).scalar_one_or_none()
    if row is None or not token:
        raise HTTPException(400, "that link is not valid")
    return _prefs(row)


@router.put("/preferences")
async def save_preferences(
    body: PreferencesIn, session: AsyncSession = Depends(get_session)
) -> dict:
    row = (
        await session.execute(
            select(Subscriber).where(Subscriber.unsubscribe_token == body.token)
        )
    ).scalar_one_or_none()
    if row is None or not body.token:
        raise HTTPException(400, "that link is not valid")

    row.wants_horoscope = body.wants_horoscope
    row.wants_videos = body.wants_videos
    row.wants_streams = body.wants_streams
    row.wants_articles = body.wants_articles
    row.cadence = body.cadence
    # A pause deletes nothing and consent stays intact — that is the whole
    # point of offering it instead of an unsubscribe.
    row.paused_until = body.paused_until if body.cadence == "paused" else None
    await session.commit()
    return _prefs(row)


def _prefs(row: Subscriber) -> dict:
    return {
        "email": row.email,
        "confirmed": row.confirmed_at is not None,
        "unsubscribed": row.unsubscribed_at is not None,
        "cadence": row.cadence,
        "pausedUntil": row.paused_until,
        "sections": {
            "horoscope": row.wants_horoscope, "videos": row.wants_videos,
            "streams": row.wants_streams, "articles": row.wants_articles,
        },
    }


@router.get("/archive")
async def archive(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Past issues, public.

    Good for search, and it shows a prospective subscriber exactly what they
    are getting before handing over an address.
    """
    rows = (
        await session.execute(
            select(Issue)
            .where(Issue.visible.is_(True), Issue.sent_at.is_not(None))
            .order_by(Issue.sent_at.desc())
        )
    ).scalars().all()
    return [
        {
            "slug": i.slug, "subject": i.subject,
            "sentAt": i.sent_at.isoformat() if i.sent_at else None,
        }
        for i in rows
    ]


@router.get("/archive/{slug}")
async def archived_issue(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = (
        await session.execute(
            select(Issue).where(Issue.slug == slug, Issue.visible.is_(True))
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such issue")
    return {
        "slug": row.slug, "subject": row.subject, "letterMd": row.letter_md,
        "sentAt": row.sent_at.isoformat() if row.sent_at else None,
    }
