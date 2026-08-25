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

import asyncio
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.config import get_settings
from shruti.core.consents import NEWSLETTER, CONSENT_VERSION
from shruti.core.db import get_session
from shruti.core.emails import newsletter_issue
from shruti.core.mail import send
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


# ── writing and sending an issue ────────────────────────────────────────────
#
# All of this was missing. The subscribe form, the double opt-in, the
# unsubscribe, the preference centre and the public archive were built; nothing
# could write a letter or send one. So the site was collecting confirmed
# addresses, promising one letter a month, against a table no code ever wrote a
# row to.
#
# Declared BEFORE /archive/{slug}: FastAPI matches in declaration order, and a
# literal path arriving after a catch-all is the mistake this codebase has made
# four times, silently every time.

log = logging.getLogger(__name__)

# Sent in small batches with a pause between them. Not politeness — a provider
# that decides this looks like a blast starts dropping mail, and the failure
# lands on the subscriber rather than here.
BATCH = 20
BREATH_SECONDS = 1.0


def _slugify(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return out[:80] or "issue"


class IssueIn(BaseModel):
    subject: str = Field(default="", max_length=200)
    letter_md: str = Field(default="", max_length=40000)
    slug: str = Field(default="", max_length=80)
    visible: bool = False


def _issue_view(i: Issue) -> dict:
    return {
        "id": i.id,
        "slug": i.slug,
        "subject": i.subject,
        "letterMd": i.letter_md,
        "visible": i.visible,
        "sentAt": i.sent_at.isoformat() if i.sent_at else None,
    }


async def _recipients(session: AsyncSession) -> list[Subscriber]:
    """
    Everybody who may lawfully be written to, today.

    Four conditions, and every one of them can lose an address for a reason
    that is theirs rather than ours: confirmed (an unconfirmed address is not
    consent), not unsubscribed, not paused past today, and still wanting the
    letter rather than only some sections.
    """
    today = datetime.now(timezone.utc).date().isoformat()
    rows = (
        await session.execute(
            select(Subscriber).where(
                Subscriber.confirmed_at.is_not(None),
                Subscriber.unsubscribed_at.is_(None),
            )
        )
    ).scalars().all()
    return [
        r for r in rows
        if r.cadence != "paused"
        and not (r.paused_until and r.paused_until > today)
    ]


@router.get("/admin/issues", dependencies=[Depends(require_admin)])
async def list_issues(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(Issue).order_by(Issue.id.desc()))
    ).scalars().all()
    return [_issue_view(i) for i in rows]


@router.get("/admin/audience", dependencies=[Depends(require_admin)])
async def audience(session: AsyncSession = Depends(get_session)) -> dict:
    """How many it would actually reach, and why the others fall out."""
    all_rows = (await session.execute(select(Subscriber))).scalars().all()
    today = datetime.now(timezone.utc).date().isoformat()
    return {
        "total": len(all_rows),
        "confirmed": len([r for r in all_rows if r.confirmed_at]),
        "unconfirmed": len([r for r in all_rows if not r.confirmed_at]),
        "unsubscribed": len([r for r in all_rows if r.unsubscribed_at]),
        "paused": len([
            r for r in all_rows
            if r.confirmed_at and not r.unsubscribed_at
            and (r.cadence == "paused" or (r.paused_until and r.paused_until > today))
        ]),
        "wouldReceive": len(await _recipients(session)),
    }


@router.post("/admin/issues", status_code=201, dependencies=[Depends(require_admin)])
async def create_issue(
    body: IssueIn, session: AsyncSession = Depends(get_session)
) -> dict:
    slug = _slugify(body.slug or body.subject)
    clash = (
        await session.execute(select(Issue).where(Issue.slug == slug))
    ).scalar_one_or_none()
    if clash is not None:
        slug = f"{slug}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    issue = Issue(
        slug=slug, subject=body.subject, letter_md=body.letter_md,
        visible=body.visible,
    )
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return _issue_view(issue)


@router.put("/admin/issues/{issue_id}", dependencies=[Depends(require_admin)])
async def update_issue(
    issue_id: int, body: IssueIn, session: AsyncSession = Depends(get_session)
) -> dict:
    issue = await session.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(404, "no such issue")
    if issue.sent_at is not None and (
        body.subject != issue.subject or body.letter_md != issue.letter_md
    ):
        # The archive has to match what landed in people's inboxes. Editing a
        # sent issue would make the public copy a different letter from the one
        # anybody read.
        raise HTTPException(
            409,
            "this issue has been sent — its words cannot change. "
            "Only whether it shows in the archive.",
        )
    issue.subject = body.subject
    issue.letter_md = body.letter_md
    issue.visible = body.visible
    if body.slug and issue.sent_at is None:
        issue.slug = _slugify(body.slug)
    await session.commit()
    await session.refresh(issue)
    return _issue_view(issue)


@router.delete("/admin/issues/{issue_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_issue(
    issue_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    issue = await session.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(404, "no such issue")
    if issue.sent_at is not None:
        raise HTTPException(
            409,
            "this issue has been sent. Hide it from the archive instead — "
            "deleting it would not un-send it, and the archive is the record.",
        )
    await session.delete(issue)
    await session.commit()
    return Response(status_code=204)


def _rendered(issue: Issue, subscriber: Subscriber | None, imprint: dict | None) -> str:
    site = get_settings().site_url.rstrip("/")
    token = subscriber.unsubscribe_token if subscriber else ""
    return newsletter_issue(
        subject=issue.subject,
        letter_md=issue.letter_md,
        issue_line=(issue.sent_at or datetime.now(timezone.utc)).strftime("%B %Y"),
        unsubscribe_url=f"{site}/newsletter/unsubscribed?token={token}" if token else site,
        preferences_url=f"{site}/newsletter/preferences?token={token}" if token else site,
        browser_url=f"{site}/newsletter/archive/{issue.slug}",
        confirmed_on=(
            subscriber.confirmed_at.strftime("%-d %B %Y")
            if subscriber and subscriber.confirmed_at else ""
        ),
        imprint=imprint,
    )


@router.post("/admin/issues/{issue_id}/test", dependencies=[Depends(require_admin)])
async def test_issue(
    issue_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send it to her, and nobody else.

    Here because the alternative is finding a typo in five hundred inboxes.
    The rendering is the same one the real send uses, so what she reads is what
    they would read.
    """
    issue = await session.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(404, "no such issue")
    html = _rendered(issue, None, None)
    result = await send(
        subject=f"[test] {issue.subject}",
        body=issue.letter_md,
        html=html,
    )
    return {"sent": result.sent, "error": result.error}


@router.post("/admin/issues/{issue_id}/send", dependencies=[Depends(require_admin)])
async def send_issue(
    issue_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send it, once.

    **Refuses a second time.** An issue that has been sent has `sent_at`, and
    sending again would put the same letter in the same inboxes — the mistake
    that costs a subscriber list. Fixing a typo means a new issue, which is
    also what an errata is.
    """
    issue = await session.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(404, "no such issue")
    if issue.sent_at is not None:
        raise HTTPException(409, "this issue has already been sent")
    if not issue.subject.strip() or not issue.letter_md.strip():
        raise HTTPException(400, "an issue needs a subject and a letter")

    people = await _recipients(session)
    if not people:
        raise HTTPException(400, "there is nobody confirmed to send to yet")

    imprint = None
    try:
        from shruti.core.settings_store import imprint_settings

        imprint = await imprint_settings(session)
    except Exception:                                  # noqa: BLE001
        pass

    sent = failed = 0
    for start in range(0, len(people), BATCH):
        for person in people[start:start + BATCH]:
            result = await send(
                subject=issue.subject,
                body=issue.letter_md,
                to=person.email,
                html=_rendered(issue, person, imprint),
            )
            if result.sent:
                sent += 1
            else:
                failed += 1
                log.warning("issue %s did not reach a subscriber: %s",
                            issue.slug, result.error)
        if start + BATCH < len(people):
            await asyncio.sleep(BREATH_SECONDS)

    # Stamped even when some sends failed. It HAS gone out; pretending
    # otherwise invites a second send to the people who did get it.
    issue.sent_at = datetime.now(timezone.utc)
    issue.visible = True
    await session.commit()
    return {"sent": sent, "failed": failed, "of": len(people)}


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
