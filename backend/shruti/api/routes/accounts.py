# SPDX-License-Identifier: AGPL-3.0-only
"""
Accounts, consents, the nativity, and the rights that are not a support email.

Export and delete are IN-PAGE CONTROLS that work now, not a promise to get back
to someone within thirty days. Deletion is immediate, irreversible, has no
hostage grace period, and reaches the newsletter list as well as the account.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from shruti.core.consents import BY_KIND, CONSENT_VERSION
from shruti.core.db import get_session
from shruti.core.mail import send as send_mail
from shruti.core.sessions import (
    SESSION_COOKIE, SESSION_DAYS, hash_password, issue_link, issue_session,
    new_token, read_link, read_session, verify_password,
)
from shruti.models.accounts import ConsentRecord, Nativity, Subscriber, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/account", tags=["accounts"])


# ── who is asking ───────────────────────────────────────────────────────────

async def current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User | None:
    claims = read_session(request.cookies.get(SESSION_COOKIE))
    if not claims:
        return None
    return (
        await session.execute(select(User).where(User.id == int(claims["sub"])))
    ).scalar_one_or_none()


async def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(401, "not signed in")
    return user


def _set_session(response: Response, user: User, secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE, issue_session(user.id, user.email),
        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=secure, path="/",
    )


# ── signing up ──────────────────────────────────────────────────────────────

class ConsentIn(BaseModel):
    kind: str
    granted: bool = False


class SignUpIn(BaseModel):
    email: EmailStr
    password: str | None = Field(default=None, min_length=10, max_length=200)
    display_name: str = Field(default="", max_length=120)
    consents: list[ConsentIn] = Field(default_factory=list)


async def _record_consents(
    session: AsyncSession, email: str, user_id: int | None,
    consents: list[ConsentIn], source: str,
) -> None:
    """
    Append a record per decision, storing the wording verbatim.

    Append-only: withdrawing writes a new row rather than editing the old one,
    because "what did they agree to, and when" cannot be answered by a row that
    has been overwritten.
    """
    for c in consents:
        spec = BY_KIND.get(c.kind)
        if spec is None:
            continue
        session.add(ConsentRecord(
            user_id=user_id, email=email, kind=spec.kind, granted=c.granted,
            version=CONSENT_VERSION, wording=spec.wording,
            lawful_basis=spec.lawful_basis, source=source,
        ))


@router.post("/signup", status_code=201)
async def sign_up(
    body: SignUpIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    email = body.email.lower().strip()
    given = {c.kind: c.granted for c in body.consents}

    # Only the contract consent can ever be required. A special-category
    # consent that blocked a submit would not be freely given.
    if not given.get("account"):
        raise HTTPException(422, "the account agreement is required to create an account")

    existing = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing is not None:
        # Not "that address is taken": whether an address has an account is
        # not something a stranger gets to learn from a form.
        return {"ok": True, "checkEmail": True}

    user = User(
        email=email, display_name=body.display_name.strip(),
        password_hash=hash_password(body.password) if body.password else None,
    )
    session.add(user)
    await session.flush()

    await _record_consents(session, email, user.id, body.consents, "signup-form")

    if given.get("newsletter"):
        token = new_token()
        session.add(Subscriber(
            email=email, user_id=user.id, confirm_token=token,
            unsubscribe_token=new_token(),
        ))
        await _send_optin(email, token)

    await session.commit()

    secure = request.url.scheme == "https" or \
        request.headers.get("x-forwarded-proto") == "https"
    _set_session(response, user, secure)
    return {"ok": True, "id": user.id, "email": user.email}


# ── signing in ──────────────────────────────────────────────────────────────

class SignInIn(BaseModel):
    email: EmailStr
    password: str | None = None


@router.post("/signin")
async def sign_in(
    body: SignInIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    email = body.email.lower().strip()
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()

    if body.password:
        # verify_password is called even with no user, so an unknown address
        # costs the same as a wrong password.
        if not verify_password(user.password_hash if user else None, body.password):
            raise HTTPException(401, "that email and password do not match")
        secure = request.url.scheme == "https" or \
            request.headers.get("x-forwarded-proto") == "https"
        _set_session(response, user, secure)
        return {"ok": True, "signedIn": True}

    # Magic link. The reply is identical whether or not the address is known.
    if user is not None:
        await _send_magic_link(email)
    return {"ok": True, "checkEmail": True}


@router.get("/link")
async def use_link(
    token: str, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    email = read_link(token, purpose="signin")
    if not email:
        raise HTTPException(400, "that link has expired or has already been used")
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(400, "that link has expired or has already been used")
    user.email_verified_at = user.email_verified_at or datetime.now(timezone.utc)
    await session.commit()
    secure = request.url.scheme == "https" or \
        request.headers.get("x-forwarded-proto") == "https"
    _set_session(response, user, secure)
    return {"ok": True, "signedIn": True}


@router.post("/signout")
async def sign_out(response: Response) -> dict:
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


# ── the account ─────────────────────────────────────────────────────────────

@router.get("/me")
async def me(
    user: User = Depends(require_user), session: AsyncSession = Depends(get_session)
) -> dict:
    nativity = (
        await session.execute(select(Nativity).where(Nativity.user_id == user.id))
    ).scalars().first()
    consents = (
        await session.execute(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user.id)
            .order_by(ConsentRecord.created_at.desc())
        )
    ).scalars().all()

    # The current state of each decision is its most recent record.
    latest: dict[str, ConsentRecord] = {}
    for c in consents:
        latest.setdefault(c.kind, c)

    subscriber = (
        await session.execute(select(Subscriber).where(Subscriber.email == user.email))
    ).scalar_one_or_none()

    return {
        "email": user.email,
        "displayName": user.display_name,
        "timezone": user.timezone,
        "readingLanguage": user.reading_language,
        "preferredTradition": user.preferred_tradition,
        "houseSystem": user.house_system,
        "ayanamsa": user.ayanamsa,
        "nativity": _nativity_payload(nativity),
        "consents": [
            {
                "kind": k, "granted": c.granted, "version": c.version,
                "givenAt": c.created_at.isoformat() if c.created_at else None,
                "lawfulBasis": c.lawful_basis, "source": c.source,
            }
            for k, c in latest.items()
        ],
        "newsletter": {
            "subscribed": bool(subscriber and subscriber.confirmed_at and not subscriber.unsubscribed_at),
            "pending": bool(subscriber and not subscriber.confirmed_at and not subscriber.unsubscribed_at),
            "cadence": subscriber.cadence if subscriber else None,
        },
    }


def _nativity_payload(n: Nativity | None) -> dict | None:
    if n is None:
        return None
    return {
        "label": n.label, "birthDate": n.birth_date, "birthTime": n.birth_time,
        "timeUnknown": n.time_unknown, "placeName": n.place_name,
        "lat": n.lat, "lon": n.lon, "elevation": n.elevation,
        "timezone": n.timezone, "utcOffsetMinutes": n.utc_offset_minutes,
    }


class ProfileIn(BaseModel):
    display_name: str = Field(default="", max_length=120)
    timezone: str = Field(default="", max_length=64)
    reading_language: str = Field(default="en", max_length=8)
    preferred_tradition: str = Field(default="", max_length=20)
    house_system: str = Field(default="", max_length=32)
    ayanamsa: str = Field(default="", max_length=32)


@router.put("/profile")
async def save_profile(
    body: ProfileIn, user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    user.display_name = body.display_name.strip()
    user.timezone = body.timezone.strip()
    user.reading_language = body.reading_language
    user.preferred_tradition = body.preferred_tradition
    user.house_system = body.house_system
    user.ayanamsa = body.ayanamsa
    await session.commit()
    return {"ok": True}


# ── the nativity ────────────────────────────────────────────────────────────

class NativityIn(BaseModel):
    label: str = Field(default="", max_length=120)
    birth_date: str
    birth_time: str | None = None
    time_unknown: bool = False
    place_name: str = Field(default="", max_length=200)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    elevation: float = 0.0
    timezone: str = Field(default="", max_length=64)
    utc_offset_minutes: int | None = None


@router.put("/nativity")
async def save_nativity(
    body: NativityIn, user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Store a birth moment — only if the explicit consent is currently given.

    Without it there is no lawful basis to hold the data, so this refuses
    rather than storing it and asking later.
    """
    latest = (
        await session.execute(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user.id, ConsentRecord.kind == "nativity")
            .order_by(ConsentRecord.created_at.desc())
        )
    ).scalars().first()
    if latest is None or not latest.granted:
        raise HTTPException(
            403,
            "storing birth data needs its own consent, which has not been given",
        )

    existing = (
        await session.execute(select(Nativity).where(Nativity.user_id == user.id))
    ).scalars().first()
    row = existing or Nativity(user_id=user.id, birth_date=body.birth_date)

    row.label = body.label
    row.birth_date = body.birth_date
    # "I don't know my birth time" is a first-class choice, so an unknown time
    # clears the field rather than failing validation.
    row.time_unknown = body.time_unknown
    row.birth_time = None if body.time_unknown else (body.birth_time or None)
    row.place_name = body.place_name
    row.lat, row.lon, row.elevation = body.lat, body.lon, body.elevation
    row.timezone = body.timezone
    row.utc_offset_minutes = body.utc_offset_minutes

    if existing is None:
        session.add(row)
    await session.commit()
    return {"ok": True, "nativity": _nativity_payload(row)}


# ── consents, revisited ─────────────────────────────────────────────────────

class ConsentChangeIn(BaseModel):
    kind: str
    granted: bool


@router.post("/consents")
async def change_consent(
    body: ConsentChangeIn, user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Change one decision. Withdrawing must be as easy as giving.

    **Withdrawing the nativity consent deletes the nativity with it.** Keeping
    birth data after its lawful basis is gone would be the whole point missed.
    """
    spec = BY_KIND.get(body.kind)
    if spec is None:
        raise HTTPException(400, f"unknown consent {body.kind!r}")
    if spec.required and not body.granted:
        raise HTTPException(
            422, "the account agreement cannot be withdrawn without deleting the account",
        )

    session.add(ConsentRecord(
        user_id=user.id, email=user.email, kind=spec.kind, granted=body.granted,
        version=CONSENT_VERSION, wording=spec.wording,
        lawful_basis=spec.lawful_basis, source="account-settings",
    ))

    deleted_nativity = False
    if spec.kind == "nativity" and not body.granted:
        await session.execute(delete(Nativity).where(Nativity.user_id == user.id))
        deleted_nativity = True

    if spec.kind == "newsletter":
        subscriber = (
            await session.execute(select(Subscriber).where(Subscriber.email == user.email))
        ).scalar_one_or_none()
        if body.granted:
            if subscriber is None:
                token = new_token()
                session.add(Subscriber(
                    email=user.email, user_id=user.id,
                    confirm_token=token, unsubscribe_token=new_token(),
                ))
                await _send_optin(user.email, token)
            else:
                subscriber.unsubscribed_at = None
        elif subscriber is not None:
            subscriber.unsubscribed_at = datetime.now(timezone.utc)

    await session.commit()
    return {"ok": True, "nativityDeleted": deleted_nativity}


# ── the rights ──────────────────────────────────────────────────────────────

@router.get("/export")
async def export_everything(
    user: User = Depends(require_user), session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Everything held about this person, as a download, now.

    No email round-trip and no "we will get back to you within thirty days" —
    the design promises a file in the page, so it is a file in the page.
    """
    nativity = (
        await session.execute(select(Nativity).where(Nativity.user_id == user.id))
    ).scalars().first()
    consents = (
        await session.execute(
            select(ConsentRecord)
            .where(ConsentRecord.email == user.email)
            .order_by(ConsentRecord.created_at)
        )
    ).scalars().all()
    subscriber = (
        await session.execute(select(Subscriber).where(Subscriber.email == user.email))
    ).scalar_one_or_none()

    return {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "email": user.email, "displayName": user.display_name,
            "timezone": user.timezone, "readingLanguage": user.reading_language,
            "preferredTradition": user.preferred_tradition,
            "houseSystem": user.house_system, "ayanamsa": user.ayanamsa,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
        },
        "nativity": _nativity_payload(nativity),
        "consentHistory": [
            {
                "kind": c.kind, "granted": c.granted, "version": c.version,
                "wording": c.wording, "lawfulBasis": c.lawful_basis,
                "source": c.source,
                "at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in consents
        ],
        "newsletter": None if subscriber is None else {
            "confirmedAt": subscriber.confirmed_at.isoformat() if subscriber.confirmed_at else None,
            "unsubscribedAt": subscriber.unsubscribed_at.isoformat() if subscriber.unsubscribed_at else None,
            "cadence": subscriber.cadence,
            "sections": {
                "horoscope": subscriber.wants_horoscope, "videos": subscriber.wants_videos,
                "streams": subscriber.wants_streams, "articles": subscriber.wants_articles,
            },
        },
    }


@router.delete("/", status_code=200)
async def delete_account(
    response: Response, user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Immediate, irreversible, no grace period — and it reaches the list.

    WHAT GOES: the account, the email address, the preferences, the nativity,
    and the newsletter subscription.

    WHAT IS KEPT, and why: a record that consent was given and withdrawn, with
    dates and NO birth data. That record is the proof the law asks for, and
    deleting it would remove the evidence that the deletion itself was
    lawful. It is anonymised to the point where it is no longer personal data
    about a living person we can identify — the email is replaced by the
    account id.
    """
    email = user.email
    uid = user.id

    await session.execute(delete(Nativity).where(Nativity.user_id == uid))

    # Deletion must reach the newsletter list too, not only the account.
    await session.execute(delete(Subscriber).where(Subscriber.email == email))

    # The consent trail survives, stripped of the address that identifies it.
    records = (
        await session.execute(select(ConsentRecord).where(ConsentRecord.email == email))
    ).scalars().all()
    for r in records:
        r.email = f"deleted-account-{uid}"
        r.user_id = None

    await session.execute(delete(User).where(User.id == uid))
    await session.commit()

    response.delete_cookie(SESSION_COOKIE, path="/")
    return {
        "ok": True,
        "deleted": ["account", "email address", "preferences", "nativity", "newsletter subscription"],
        "kept": ["a consent given/withdrawn record with dates and no birth data"],
    }


# ── mail ────────────────────────────────────────────────────────────────────

async def _send_magic_link(email: str) -> None:
    token = issue_link(email, purpose="signin")
    url = f"{_site_url()}/signin/link?token={token}"
    await send_mail(
        subject="Your sign-in link",
        body=(
            "Here is your sign-in link. It works once, and expires in 20 minutes.\n\n"
            f"{url}\n\n"
            "If you did not ask for this, nothing has happened and you can ignore it."
        ),
        to=email,
    )


async def _send_optin(email: str, token: str) -> None:
    """
    The mandatory double opt-in mail, in the designer's own template.

    Sent as HTML because the template's whole point is that it survives a
    hostile client, with a plain-text body alongside for the ones that want it.
    """
    from shruti.core.emails import optin_confirm, site_url

    url = f"{site_url()}/newsletter/confirm?token={token}"
    await send_mail(
        subject="Confirm the monthly letter",
        body=(
            "Confirm you want the monthly letter, including offers for "
            "astrological courses and magickal services when those open.\n\n"
            f"{url}\n\n"
            "If you did not ask for this, do nothing — an unconfirmed address "
            "is never sent to."
        ),
        html=optin_confirm(token),
        to=email,
    )


def _site_url() -> str:
    import os
    return os.environ.get("SHRUTI_SITE_URL", "http://localhost:8200").rstrip("/")
