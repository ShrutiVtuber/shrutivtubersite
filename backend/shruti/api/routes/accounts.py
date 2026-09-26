# SPDX-License-Identifier: AGPL-3.0-only
"""
Accounts, consents, the nativity, and the rights that are not a support email.

Export and delete are IN-PAGE CONTROLS that work now, not a promise to get back
to someone within thirty days. Deletion is immediate, irreversible, has no
hostage grace period, and reaches the newsletter list as well as the account.
"""
from __future__ import annotations

import copy
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlmodel import delete, select

from shruti.core.consents import BY_KIND, CONSENT_VERSION, PUBLISH
from shruti.core.bans import is_banned
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

def session_token(request: Request) -> str | None:
    """
    The session credential this request carries, cookie first.

    ⚠ Cookie FIRST, and it matters. Anything that sends a cookie is a browser,
    and its cookie was issued httpOnly, samesite and secure; letting a header
    override it would mean a script that cannot read the cookie could still
    choose the identity by adding one.
    """
    cookie = request.cookies.get(SESSION_COOKIE)
    if cookie:
        return cookie
    header = request.headers.get("authorization") or ""
    if header[:7].lower() == "bearer ":
        return header[7:].strip() or None
    return None


async def current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User | None:
    """
    Who is asking — from the browser's cookie, or the app's bearer token.

    Same signed value either way, because it is the same account: she asked
    that somebody who signs up on their phone be signed in on the site too. A
    phone has no cookie jar worth the name, so the app holds the token itself
    and sends it as a bearer; the website carries on with the httpOnly cookie
    it has always had.

    ⚠ The cookie is tried FIRST. A browser that somehow sends both is a browser,
    and its cookie is the credential that was issued with httpOnly, samesite and
    secure on it.
    """
    claims = read_session(session_token(request))
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

#: What a password has to be, said once, in words meant for a person.
#:
#: ⚠ **Pydantic's own message reached a screen.** `min_length=10` on the schema
#: produces "String should have at least 10 characters", which the app shows
#: verbatim because it trusts the server to say the useful thing. It appeared
#: in the video recorded for App Review on 12 September 2026, which is where it
#: was caught — a reviewer reading developer output concludes the app is not
#: finished, and they would not be wrong.
PASSWORD_MINIMUM = 10
PASSWORD_TOO_SHORT = "A password needs ten characters or more."


def _refuse_a_short_password(password: str | None) -> None:
    if password is not None and len(password) < PASSWORD_MINIMUM:
        raise HTTPException(422, PASSWORD_TOO_SHORT)


class ConsentIn(BaseModel):
    kind: str
    granted: bool = False


class SignUpIn(BaseModel):
    email: EmailStr
    # ⚠ No min_length here on purpose — see the check in `sign_up`. Pydantic
    # words its own failures, and "String should have at least 10
    # characters" is developer output that was shown to a person.
    password: str | None = Field(default=None, max_length=200)
    display_name: str = Field(default="", max_length=120)
    consents: list[ConsentIn] = Field(default_factory=list)
    # ⚠ Opt-in, so the website's behaviour does not change. A browser gets the
    # session as an httpOnly cookie and nothing else; asking for it in the body
    # would hand any injected script the credential the cookie flag exists to
    # keep away from it. The app cannot use a cookie, so it asks.
    bearer: bool = False


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


@router.get("/consents")
async def consent_wording() -> dict:
    """
    The three decisions, with the exact words that will be filed.

    Public, and read by the app so it can show what it is about to store. The
    wording lives in one place for a reason the module says plainly: a form that
    displays one sentence and files another is worse than no record at all. The
    website mirrors it in TypeScript with a test holding the two together; the
    app asks instead, which is one fewer copy to drift.
    """
    from shruti.core.consents import ALL, CONSENT_VERSION, PUBLISH

    def spec(c) -> dict:
        return {
            "kind": c.kind,
            "label": c.label,
            "wording": c.wording,
            "basis": c.lawful_basis,
            "required": c.required,
            "explanation": c.explanation,
        }

    return {
        "version": CONSENT_VERSION,
        "consents": [spec(c) for c in ALL],
        # ⚠ Apart from `consents` on purpose: an app renders that list at
        # signup, and this one belongs to the first publish, when a publish
        # endpoint answers 428. The app shows these words and files them.
        "publish": spec(PUBLISH),
    }


@router.post("/signup", status_code=201)
async def sign_up(
    body: SignUpIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    email = body.email.lower().strip()
    given = {c.kind: c.granted for c in body.consents}
    _refuse_a_short_password(body.password)

    # Only the contract consent can ever be required. A special-category
    # consent that blocked a submit would not be freely given.
    if not given.get("account"):
        raise HTTPException(422, "the account agreement is required to create an account")

    # A banned address is turned away, and told nothing more than anyone else
    # is told — the same answer as an address that already has an account, for
    # the same reason: a form does not get to be an oracle about who is here.
    if await is_banned(email, session):
        return {"ok": True, "checkEmail": True}

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
        await _send_optin(email, token, session)

    await session.commit()

    # ⚠ **No session yet.** An account is not usable until the address behind
    # it has been proved, and proving it is following a link sent to it. The
    # practice room carries other people's writing, and an unproved address is
    # how that gets abused — somebody banned makes another account in seconds
    # with an address nobody can reach.
    #
    # ⚠ The answer here is the SAME as the answer for an address that already
    # has an account, deliberately. A form does not get to be an oracle about
    # who is already here.
    await _send_verification(email)
    return {"ok": True, "checkEmail": True}


# ── signing in ──────────────────────────────────────────────────────────────

class SignInIn(BaseModel):
    email: EmailStr
    password: str | None = None
    bearer: bool = False       # see SignUpIn.bearer


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
        # ⚠ Checked AFTER the password, never before. Refusing an unverified
        # address before the password is checked would tell a stranger which
        # addresses have accounts here, which is the thing every other answer
        # in this file is careful not to say.
        #
        # ⚠ 403 with a code the app can act on, rather than a 401 that reads as
        # "wrong password" — somebody typing the right password and being told
        # it is wrong will change it, and still not get in.
        if user is not None and user.email_verified_at is None:
            raise HTTPException(
                403,
                "that address has not been confirmed yet — follow the link in "
                "your email, or ask for a new one",
            )
        secure = request.url.scheme == "https" or \
            request.headers.get("x-forwarded-proto") == "https"
        _set_session(response, user, secure)
        out = {"ok": True, "signedIn": True,
               "id": user.id, "email": user.email,
               "displayName": user.display_name}
        if body.bearer:
            out["token"] = issue_session(user.id, user.email)
        return out

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


class ResendIn(BaseModel):
    email: EmailStr


@router.post("/verify/resend", status_code=202)
async def resend_verification(
    body: ResendIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send the confirmation link again.

    ⚠ The same answer either way, like every other address-shaped question
    here: whether an address has an account, and whether it is confirmed, are
    both things a stranger does not get to learn from a form.
    """
    email = body.email.lower().strip()
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is not None and user.email_verified_at is None:
        await _send_verification(email)
    return {"ok": True, "checkEmail": True}


@router.get("/verify")
async def confirm_address(
    token: str, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Follow the link from the email, and the account starts working.

    ⚠ Signs them in as well. Somebody who has just proved they hold the address
    has done everything sign-in asks for, and making them type a password they
    set ninety seconds ago is a step that protects nobody.

    ⚠ Already-confirmed is a SUCCESS, not an error. Mail clients follow links
    to check them, people press back, and a second visit saying "that link has
    expired" for an account that is perfectly fine is a support request.
    """
    email = read_link(token, purpose="verify")
    if not email:
        raise HTTPException(
            400, "that link has expired — ask for a new one and it will send"
        )
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(
            400, "that link has expired — ask for a new one and it will send"
        )

    user.email_verified_at = user.email_verified_at or datetime.now(timezone.utc)
    await session.commit()

    secure = request.url.scheme == "https" or \
        request.headers.get("x-forwarded-proto") == "https"
    _set_session(response, user, secure)
    return {"ok": True, "confirmed": True, "email": user.email}


@router.post("/signout")
async def sign_out(response: Response) -> dict:
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


# ── forgotten passwords ─────────────────────────────────────────────────────


class ResetRequestIn(BaseModel):
    email: EmailStr


@router.post("/reset/request", status_code=202)
async def request_reset(
    body: ResetRequestIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send a reset link, and say the same thing either way.

    Whether an address has an account here is not something a stranger gets to
    learn from a form, so the reply is identical whether one was sent or not.
    """
    email = body.email.lower().strip()
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is not None:
        url = f"{_site_url()}/reset?token={issue_link(email, purpose='reset')}"
        await send_mail(
            subject="Reset your password",
            body=(
                "A password reset was requested for your shrutivtuber.com account.\n\n"
                f"{url}\n\n"
                "It works once and expires in 20 minutes. If this was not you, "
                "nothing has happened and you can ignore it."
            ),
            to=email,
        )
    return {"ok": True, "checkEmail": True}


class ResetIn(BaseModel):
    token: str
    # ⚠ Same reasoning as SignUpIn — the sentence is ours.
    password: str = Field(max_length=200)


@router.post("/reset")
async def do_reset(
    body: ResetIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Set a new password from a reset link, and sign in.

    A reset link cannot be used as a sign-in link and vice versa: the purpose
    is claimed in the token and checked, so one cannot stand in for the other.
    """
    _refuse_a_short_password(body.password)
    email = read_link(body.token, purpose="reset")
    if not email:
        raise HTTPException(400, "that link has expired or has already been used")
    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(400, "that link has expired or has already been used")

    user.password_hash = hash_password(body.password)
    user.email_verified_at = user.email_verified_at or datetime.now(timezone.utc)
    await session.commit()

    secure = request.url.scheme == "https" or \
        request.headers.get("x-forwarded-proto") == "https"
    _set_session(response, user, secure)
    return {"ok": True, "signedIn": True}


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
        "place": {
            "name": user.place_name,
            "lat": user.place_lat,
            "lon": user.place_lon,
        } if user.place_name or user.place_lat is not None else None,
        "readingLanguage": user.reading_language,
        "preferredTradition": user.preferred_tradition,
        "houseSystem": user.house_system,
        "ayanamsa": user.ayanamsa,
        "nativity": _nativity_payload(nativity),
        "consents": [
            {
                # ⚠ The publishing agreement counts only for the words in
                # force (core.publishing): an old yes to other words reads as
                # not given, which is what the publish endpoints will say too.
                "kind": k,
                "granted": c.granted and (k != PUBLISH.kind or c.wording == PUBLISH.wording),
                "version": c.version,
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
    from shruti.core.moments import birth_moment, timezone_known

    return {
        "label": n.label, "birthDate": n.birth_date, "birthTime": n.birth_time,
        "timeUnknown": n.time_unknown, "placeName": n.place_name,
        "lat": n.lat, "lon": n.lon, "elevation": n.elevation,
        "timezone": n.timezone, "utcOffsetMinutes": n.utc_offset_minutes,
        # The instant, offset and all. The zone was being stored here and read
        # back by nothing at all, while Today cast this nativity from a naive
        # string the ephemeris took for UTC.
        "when": birth_moment(n.birth_date, n.birth_time, n.time_unknown, n.timezone),
        "timezoneKnown": timezone_known(n.timezone),
    }


class PlaceIn(BaseModel):
    """Where they are. Blank clears it."""

    name: str = Field(default="", max_length=160)
    lat: float | None = None
    lon: float | None = None


@router.put("/me/place")
async def set_place(
    body: PlaceIn,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Remember where somebody is, or forget it.

    One field for the whole set: clearing the name clears the coordinates too,
    because a place with coordinates and no name renders as a pair of numbers
    nobody recognises, and a name with no coordinates cannot be computed from.
    """
    name = body.name.strip()
    if not name or body.lat is None or body.lon is None:
        user.place_name, user.place_lat, user.place_lon = "", None, None
    else:
        # A latitude outside the poles is a typo or a probe, not a place.
        if not (-90 <= body.lat <= 90) or not (-180 <= body.lon <= 180):
            raise HTTPException(422, "that is not a point on the earth")
        user.place_name = name
        user.place_lat = float(body.lat)
        user.place_lon = float(body.lon)
    await session.commit()
    return {"place": None if not user.place_name else {
        "name": user.place_name, "lat": user.place_lat, "lon": user.place_lon}}


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
    # Where the decision was made, filed with the record. Only the names in
    # CONSENT_SOURCES: anything else a client sends is filed as the settings page.
    source: str = "account-settings"


CONSENT_SOURCES = ("account-settings", "publish-dialog", "app")


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
        lawful_basis=spec.lawful_basis,
        source=body.source if body.source in CONSENT_SOURCES else "account-settings",
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
                await _send_optin(user.email, token, session)
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
    return await export_for(user, session)


async def export_for(user: User, session: AsyncSession) -> dict:
    """
    The export itself.

    Shared with the admin, which has to send someone their data before closing
    their account. One definition of "everything held about you" — two would
    drift, and the one that drifted would be the one nobody was looking at.
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
            "timezone": user.timezone,
        "place": {
            "name": user.place_name,
            "lat": user.place_lat,
            "lon": user.place_lon,
        } if user.place_name or user.place_lat is not None else None, "readingLanguage": user.reading_language,
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
        # Everything else held about them, table by table: what they wrote,
        # made, joined, kept and bought. GDPR's right of access is "all of
        # it", and one definition shared with the ban keeps it that way.
        **(await _everything_else(user, session)),
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


# Never in a download: the export is also EMAILED when an account is closed
# (admin.ban), and a token in an email is a key to somebody's chart, overlay
# or share in an inbox nobody here controls.
_NEVER_EXPORTED = ("password_hash", "public_key", "endpoint", "p256dh", "auth", "fcm_token")


def _plain(row) -> dict:
    """One row as the person may read it: every column, minus keys and secrets."""
    out = {}
    for key, value in row.model_dump().items():
        if key in _NEVER_EXPORTED or key.endswith("token") or key.endswith("_hash"):
            continue
        out[key] = value.isoformat() if hasattr(value, "isoformat") else value
    return out


async def _everything_else(user: User, session: AsyncSession) -> dict:
    """
    Every table with a row about this person, as rows.

    ⚠ `test_an_account_can_be_deleted` holds this against the list of foreign
    keys to `site_user`: a table added later that points at people and is
    missing here fails there, rather than quietly leaving the download short.
    """
    from shruti.models import (
        Enrolment, Entitlement, Hosting, LessonProgress, OverlayToken, PushSubscription, Supporter,
    )
    from shruti.models.accounts import CollabGroup, Comparison, Passkey, SavedChart, StandingTest
    from shruti.models.devices import AppDevice
    from shruti.models.guides import (
        Build, Group, GroupContribution, GroupMember, Guide, GuideReport, GuideRun, GuideVersion,
        GuideVote,
    )
    from shruti.models.carnatic import (
        CarnaticComment, CarnaticDeviceLink, CarnaticLike, CarnaticPost, CarnaticPracticeDay,
        CarnaticProfile, CarnaticProgress, CarnaticSong,
    )
    from shruti.models.ledger import Ledger, LedgerBusiness, LedgerWeek
    from shruti.models.practice import (
        PracticeBlock, PracticeComment, PracticeReading, PracticeReport, PracticeStrike,
        PracticeVote, PracticeWork,
    )

    uid = user.id

    async def rows(model, *where) -> list[dict]:
        found = (await session.execute(select(model).where(*where))).scalars().all()
        return [_plain(r) for r in found]

    works = (await session.execute(select(PracticeWork).where(PracticeWork.user_id == uid))).scalars().all()
    work_ids = [w.id for w in works]

    # The Ledger, nested as it is kept: a ledger, its businesses, their weeks.
    ledgers = await rows(Ledger, Ledger.user_id == uid)
    businesses = await rows(LedgerBusiness, LedgerBusiness.ledger_id.in_([g["id"] for g in ledgers])) if ledgers else []
    weeks = await rows(LedgerWeek, LedgerWeek.business_id.in_([b["id"] for b in businesses])) if businesses else []
    for b in businesses:
        b["weeks"] = sorted((w for w in weeks if w["business_id"] == b["id"]), key=lambda w: w["n"])
    ledgers.sort(key=lambda g: (g["position"], g["id"]))
    for g in ledgers:
        g["businesses"] = sorted((b for b in businesses if b["ledger_id"] == g["id"]),
                                 key=lambda b: (b["position"], b["id"]))
    return {
        "guides": await rows(Guide, Guide.created_by == uid),
        "guideVersions": await rows(GuideVersion, (GuideVersion.created_by == uid)
                                    | (GuideVersion.contributed_by == uid)),
        "guideRuns": await rows(GuideRun, GuideRun.user_id == uid),
        "guideVotes": await rows(GuideVote, GuideVote.user_id == uid),
        "guideReports": await rows(GuideReport, GuideReport.user_id == uid),
        "groupsStarted": await rows(Group, Group.created_by == uid),
        "groupMemberships": await rows(GroupMember, GroupMember.user_id == uid),
        "groupContributions": await rows(GroupContribution, GroupContribution.user_id == uid),
        "builds": await rows(Build, Build.user_id == uid),
        "ledgers": ledgers,
        "overlays": await rows(OverlayToken, OverlayToken.user_id == uid),
        "practiceWorks": [_plain(w) for w in works],
        "practiceReadings": await rows(PracticeReading, PracticeReading.work_id.in_(work_ids)) if work_ids else [],
        "practiceComments": await rows(PracticeComment, PracticeComment.user_id == uid),
        "practiceVotes": await rows(PracticeVote, PracticeVote.user_id == uid),
        "practiceReports": await rows(PracticeReport, PracticeReport.user_id == uid),
        "practiceStrikes": await rows(PracticeStrike, PracticeStrike.user_id == uid),
        "practiceBlocks": await rows(PracticeBlock, PracticeBlock.user_id == uid),
        "savedCharts": await rows(SavedChart, SavedChart.user_id == uid),
        "comparisons": await rows(Comparison, Comparison.user_id == uid),
        "standingTests": await rows(StandingTest, StandingTest.user_id == uid),
        "collabGroups": await rows(CollabGroup, CollabGroup.user_id == uid),
        "passkeys": await rows(Passkey, Passkey.user_id == uid),
        "pushSubscriptions": await rows(PushSubscription, PushSubscription.user_id == uid),
        "appDevices": await rows(AppDevice, AppDevice.user_id == uid),
        "entitlements": await rows(Entitlement, Entitlement.user_id == uid),
        "enrolments": await rows(Enrolment, Enrolment.user_id == uid),
        "lessonProgress": await rows(LessonProgress, LessonProgress.user_id == uid),
        "supporter": await rows(Supporter, Supporter.user_id == uid),
        "hosting": await rows(Hosting, Hosting.user_id == uid),
        # Swara Studio (models/carnatic.py): all of it goes with the account.
        "carnatic": {
            "settings": await rows(CarnaticProfile, CarnaticProfile.user_id == uid),
            "progress": await rows(CarnaticProgress, CarnaticProgress.user_id == uid),
            "practiceDays": await rows(CarnaticPracticeDay, CarnaticPracticeDay.user_id == uid),
            "songs": await rows(CarnaticSong, CarnaticSong.user_id == uid),
            "listenPosts": await rows(CarnaticPost, CarnaticPost.user_id == uid),
            "likes": await rows(CarnaticLike, CarnaticLike.user_id == uid),
            "comments": await rows(CarnaticComment, CarnaticComment.user_id == uid),
            "appSignIns": await rows(CarnaticDeviceLink, CarnaticDeviceLink.user_id == uid),
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
    saved charts and their comparisons, drafts, runs, unshared builds, ledgers,
    passkeys, devices, votes, reports, blocks, and the newsletter subscription.

    WHAT STAYS, WITHOUT THEIR NAME: what they made public, because other
    people are following it (see `erase`). They agreed to that before they
    published anything (`core.publishing`).

    WHAT IS KEPT, and why: a record that consent was given and withdrawn, with
    dates and NO birth data. That record is the proof the law asks for, and
    deleting it would remove the evidence that the deletion itself was
    lawful. It is anonymised to the point where it is no longer personal data
    about a living person we can identify — the email is replaced by the
    account id.
    """
    result = await erase(user, session)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return result


async def erase(user: User, session: AsyncSession) -> dict:
    """
    The deletion itself, shared with the admin's ban.

    A banned account is a deleted account — the same deletion, reaching the
    same places, keeping the same anonymised consent trail. Writing it twice
    would mean one of them forgetting the newsletter.

    Three kinds of thing, in this order:

    1. **What is nobody's but theirs** is deleted: the nativity, saved charts
       and the comparisons made with them, passkeys, devices, push
       subscriptions, class progress, drafts, runs, unshared builds, votes,
       reports, blocks, the newsletter subscription.
    2. **What they made public is kept, with their name taken off**
       (`_anonymise_public`): other people are following a published guide,
       answering a reading, filling a group, copying a shared build. They
       agreed to this before they published (`core.publishing`).
    3. **The consent trail** stays, stripped of the address that identified
       it — the proof that the deletion itself was lawful.

    ⚠ Every table pointing at `site_user` has to be answered for here or by
    its own ON DELETE (migration k9i6f2g7h854). One that is not makes the
    final DELETE fail, the transaction roll back, and the person believe they
    are gone when nothing has gone — which is how this function behaved until
    that migration. `test_an_account_can_be_deleted` names every table.
    """
    email = user.email
    uid = user.id
    names = _public_names(user)

    kept = await _anonymise_public(session, uid, names)
    await _erase_private(session, uid)
    await session.execute(delete(Nativity).where(Nativity.user_id == uid))

    # Deletion must reach the newsletter list too, not only the account —
    # by the address, and by the account in case the address was changed.
    await session.execute(
        delete(Subscriber).where((Subscriber.email == email) | (Subscriber.user_id == uid)))

    # The consent trail survives, stripped of the address that identifies it.
    records = (
        await session.execute(
            select(ConsentRecord).where(
                (ConsentRecord.email == email) | (ConsentRecord.user_id == uid)))
    ).scalars().all()
    for r in records:
        r.email = f"deleted-account-{uid}"
        r.user_id = None

    await session.execute(delete(User).where(User.id == uid))
    await session.commit()

    return {
        "ok": True,
        "deleted": [
            "account", "email address", "preferences", "nativity", "saved charts and comparisons",
            "passkeys and devices", "newsletter subscription", "drafts", "runs",
            "builds you had not shared", "votes and reports", "class progress", "ledgers",
            "Swara Studio settings, progress, practice log, songs, sheets and Listen posts",
        ],
        "kept": [
            "a consent given/withdrawn record with dates and no birth data",
            *(f"{what}: {n}, still public, with your name taken off" for what, n in kept.items() if n),
        ],
    }


def _public_names(user: User) -> set[str]:
    """
    Every name this person could have been credited under in a guide's own
    JSON (`guide.authors` is a list of strings, written from the display name
    — and, before 26 September 2026, from the front of the email address when
    there was no display name).

    ⚠ A name changed since a guide was written is not found here. The credit
    was a string copied at the time, and there is no record of what it was.
    """
    names = {(user.display_name or "").strip(), (user.email or "").split("@")[0].strip()}
    return {n for n in names if n and n != "somebody"}


def _without_notes(value):
    """A copy with every `note` and `notes` removed — what a person wrote to themselves."""
    if isinstance(value, dict):
        return {k: _without_notes(v) for k, v in value.items() if k not in ("note", "notes")}
    if isinstance(value, list):
        return [_without_notes(v) for v in value]
    return value


async def _anonymise_public(session: AsyncSession, uid: int, names: set[str]) -> dict:
    """
    What this person made public stays, and stops being theirs.

    PUBLIC, and kept with the author column set to NULL (which reads as
    "somebody" wherever a name is shown):

    - a guide with a published version, unless they had withdrawn it — its
      published and superseded versions; their unpublished drafts of it go
    - a change they proposed that was accepted into somebody's guide
    - a reading they submitted to the practice room, unless withdrawn, and
      every comment they left on anyone's reading
    - a group somebody else had joined, and every amount they gave to a group
    - a build they had shared by code, with every note taken out of it

    Their name is also taken out of `guide.authors` in the JSON of every guide
    they are credited on — their own, and every fork of it down the line,
    whoever made the fork.

    Everything else they wrote — drafts, proposals nobody accepted, withdrawn
    work, a group nobody else joined, an unshared build — is private and goes
    in `_erase_private`, after this.
    """
    from shruti.models import OverlayToken
    from shruti.models.guides import (
        Build, Group, GroupContribution, GroupMember, Guide, GuideReport, GuideRun,
        GuideVersion, GuideVote,
    )
    from shruti.models.practice import PracticeComment, PracticeWork
    from shrutisguides.builds import public_goals

    kept = {"guides": 0, "accepted changes": 0, "readings": 0, "comments": 0,
            "groups": 0, "shared builds": 0}
    # Every row anonymised here says when: a null author with no date is a
    # bug, a null author with one is a person who left.
    gone = datetime.now(timezone.utc)
    public_versions = ("published", "superseded")

    # ── guides ─────────────────────────────────────────────────────────────
    theirs = (await session.execute(select(Guide).where(Guide.created_by == uid))).scalars().all()
    credited: list[int] = []
    for g in theirs:
        withdrawn = g.hidden and g.hidden_by == "author"
        if g.published_version_id and not withdrawn:
            g.created_by, g.author_deleted_at = None, gone
            credited.append(g.id)
            kept["guides"] += 1
            # Their unpublished drafts of the guide are private; what was
            # published, and what it replaced, is what people read.
            await session.execute(
                delete(GuideVersion).where(
                    GuideVersion.guide_id == g.id, GuideVersion.created_by == uid,
                    GuideVersion.contributed_by.is_(None),
                    GuideVersion.state.not_in(public_versions)))
            continue
        # Never public, or withdrawn by them: the guide goes, and with it
        # every run of it — nobody else can have been following a guide that
        # was never out, and a withdrawn one was already gone for them.
        runs_of = [r for (r,) in (await session.execute(
            select(GuideRun.id).where(GuideRun.guide_id == g.id))).all()]
        if runs_of:
            await session.execute(delete(OverlayToken).where(OverlayToken.run_id.in_(runs_of)))
            await session.execute(update(Build).where(Build.run_id.in_(runs_of)).values(run_id=None))
            await session.execute(delete(GuideRun).where(GuideRun.id.in_(runs_of)))
        await session.execute(update(Guide).where(Guide.published_version_id.in_(
            select(GuideVersion.id).where(GuideVersion.guide_id == g.id))).values(published_version_id=None))
        await session.execute(delete(GuideVote).where(GuideVote.guide_id == g.id))
        await session.execute(delete(GuideReport).where(GuideReport.guide_id == g.id))
        await session.execute(delete(GuideVersion).where(GuideVersion.guide_id == g.id))
        await session.delete(g)
    await session.flush()

    # A change they proposed to somebody else's guide: kept once accepted
    # (it is part of what people read), deleted while it was only a proposal.
    accepted = (await session.execute(
        update(GuideVersion)
        .where(GuideVersion.contributed_by == uid, GuideVersion.state.in_(public_versions))
        .values(contributed_by=None, created_by=None, author_deleted_at=gone))).rowcount or 0
    kept["accepted changes"] = accepted
    await session.execute(delete(GuideVersion).where(GuideVersion.created_by == uid,
                                                     GuideVersion.state.not_in(public_versions)))
    await session.execute(update(GuideVersion).where(GuideVersion.created_by == uid)
                          .values(created_by=None, author_deleted_at=gone))
    await session.execute(update(GuideVersion).where(GuideVersion.contributed_by == uid)
                          .values(contributed_by=None, author_deleted_at=gone))

    # Their name, out of the credits of every guide descended from theirs.
    if names and credited:
        lineage, frontier = set(credited), list(credited)
        while frontier:
            children = [c for (c,) in (await session.execute(
                select(Guide.id).where(Guide.forked_from_id.in_(frontier)))).all()]
            frontier = [c for c in children if c not in lineage]
            lineage.update(frontier)
        versions = (await session.execute(
            select(GuideVersion).where(GuideVersion.guide_id.in_(lineage)))).scalars().all()
        for v in versions:
            meta = (v.body or {}).get("guide") or {}
            authors = meta.get("authors")
            if isinstance(authors, list) and any(a in names for a in authors):
                body = copy.deepcopy(v.body)
                body["guide"]["authors"] = [("somebody" if a in names else a) for a in authors]
                v.body = body

    # ── groups ─────────────────────────────────────────────────────────────
    groups = (await session.execute(select(Group).where(Group.created_by == uid))).scalars().all()
    for grp in groups:
        others = (await session.execute(
            select(GroupMember.id).where(GroupMember.group_id == grp.id, GroupMember.user_id != uid)
        )).first()
        if others is not None:
            grp.created_by, grp.author_deleted_at = None, gone
            kept["groups"] += 1
            continue
        await session.execute(delete(OverlayToken).where(OverlayToken.group_id == grp.id))
        await session.execute(delete(GroupContribution).where(GroupContribution.group_id == grp.id))
        await session.execute(delete(GroupMember).where(GroupMember.group_id == grp.id))
        await session.delete(grp)
    await session.flush()
    # What they gave still counts toward the goal other people are filling.
    await session.execute(update(GroupContribution).where(GroupContribution.user_id == uid)
                          .values(user_id=None, author_deleted_at=gone))

    # ── the practice room ──────────────────────────────────────────────────
    kept["readings"] = (await session.execute(
        update(PracticeWork)
        .where(PracticeWork.user_id == uid, PracticeWork.submitted_at.is_not(None),
               ~((PracticeWork.hidden.is_(True)) & (PracticeWork.hidden_by == "author")))
        .values(user_id=None, author_deleted_at=gone))).rowcount or 0
    await session.execute(delete(PracticeComment).where(
        PracticeComment.user_id == uid, PracticeComment.hidden.is_(True),
        PracticeComment.hidden_by == "author"))
    kept["comments"] = (await session.execute(
        update(PracticeComment).where(PracticeComment.user_id == uid)
        .values(user_id=None, author_deleted_at=gone))).rowcount or 0

    # ── shared builds ──────────────────────────────────────────────────────
    shared = (await session.execute(
        select(Build).where(Build.user_id == uid, Build.share_code.is_not(None)))).scalars().all()
    for b in shared:
        await session.execute(delete(OverlayToken).where(OverlayToken.build_id == b.id))
        b.user_id, b.author_deleted_at = None, gone
        b.run_id = None
        b.goals = public_goals(b.goals)
        b.plan = _without_notes(b.plan or {})
        kept["shared builds"] += 1

    await session.flush()
    return kept


async def _erase_private(session: AsyncSession, uid: int) -> None:
    """
    Everything that was only ever theirs. Runs after `_anonymise_public`, so
    whatever still points at them here is, by elimination, private.
    """
    from shruti.models import (
        Enrolment, Entitlement, Hosting, LessonProgress, OverlayToken, PushSubscription, Supporter,
    )
    from shruti.models.accounts import Comparison, Passkey, SavedChart
    from shruti.models.guides import (
        Build, Group, GroupMember, Guide, GuideReport, GuideRun, GuideVersion, GuideVote,
    )
    from shruti.models.practice import PracticeBlock, PracticeWork

    # Runs, and every overlay they minted.
    runs = [r for (r,) in (await session.execute(select(GuideRun.id).where(GuideRun.user_id == uid))).all()]
    await session.execute(delete(OverlayToken).where(OverlayToken.user_id == uid))
    if runs:
        await session.execute(delete(OverlayToken).where(OverlayToken.run_id.in_(runs)))
        await session.execute(update(Build).where(Build.run_id.in_(runs)).values(run_id=None))
        await session.execute(delete(GuideRun).where(GuideRun.id.in_(runs)))

    # Builds nobody else was given.
    unshared = [b for (b,) in (await session.execute(select(Build.id).where(Build.user_id == uid))).all()]
    if unshared:
        await session.execute(delete(OverlayToken).where(OverlayToken.build_id.in_(unshared)))
        await session.execute(delete(Build).where(Build.id.in_(unshared)))

    await session.execute(delete(GroupMember).where(GroupMember.user_id == uid))
    await session.execute(delete(GuideVote).where(GuideVote.user_id == uid))
    await session.execute(delete(GuideReport).where(GuideReport.user_id == uid))

    # Practice drafts and withdrawn work. Readings, votes and comments on
    # them go by their own ON DELETE CASCADE.
    await session.execute(delete(PracticeWork).where(PracticeWork.user_id == uid))
    await session.execute(delete(PracticeBlock).where(
        (PracticeBlock.user_id == uid) | (PracticeBlock.blocked_id == uid)))

    # Charts are birth data — never kept, published or not. Their own
    # comparisons first; the comparisons OTHER people made with these charts
    # and the standing tests on them go by ON DELETE CASCADE with the chart.
    await session.execute(delete(Comparison).where(Comparison.user_id == uid))
    await session.execute(delete(SavedChart).where(SavedChart.user_id == uid))

    for table in (Passkey, PushSubscription, Entitlement, Enrolment, LessonProgress):
        await session.execute(delete(table).where(table.user_id == uid))

    # Billing keeps its own records for as long as tax law asks; the link to
    # the account is what goes.
    await session.execute(update(Hosting).where(Hosting.user_id == uid).values(user_id=None))
    await session.execute(update(Supporter).where(Supporter.user_id == uid).values(user_id=None))

    # ⚠ Anything left pointing at them now is a bug in `_anonymise_public`,
    # not something to delete quietly: say so in the log and let the
    # foreign keys decide.
    for model, column in ((Guide, Guide.created_by), (GuideVersion, GuideVersion.created_by),
                          (Group, Group.created_by)):
        left = (await session.execute(select(model.id).where(column == uid))).first()
        if left is not None:
            log.error("erase: %s %s still points at the account being deleted", model.__name__, left[0])
    await session.flush()


# ── mail ────────────────────────────────────────────────────────────────────


async def _send_verification(email: str) -> None:
    """
    The one email an account cannot start without.

    ⚠ Twenty minutes, like every other link here. That is short for a
    confirmation, which is why `/verify/resend` exists and why the app offers
    it on the very screen that says to check your email.
    """
    token = issue_link(email, purpose="verify")
    url = f"{_site_url()}/verify?token={token}"
    # ⚠ **This is the one mail whose failure strands somebody.** `send` never
    # raises, deliberately — a failed message must not fail the request that
    # triggered it. That was harmless when signing up also signed you in; now
    # the account exists, cannot be used, and no link is coming. The way out is
    # the resend button, which is why it sits on the very screen that says to
    # check your email — but a silent failure should still be loud in the log.
    result = await send_mail(
        subject="Confirm your address",
        body=(
            "Welcome. Follow this link and your shrutivtuber.com account "
            "starts working — it also signs you in.\n\n"
            f"{url}\n\n"
            "It expires in 20 minutes; if it has, ask for another from the "
            "sign-in screen. If you did not make an account, nothing has "
            "happened and you can ignore this."
        ),
        to=email,
    )
    if not result.sent:
        log.error(
            "the confirmation mail did not send (%s) — that account cannot be "
            "used until somebody asks for the link again", result.error,
        )


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


async def _send_optin(
    email: str, token: str, session: AsyncSession | None = None
) -> None:
    """
    The mandatory double opt-in mail, in the designer's own template.

    Sent as HTML because the template's whole point is that it survives a
    hostile client, with a plain-text body alongside for the ones that want it.
    """
    from shruti.core.emails import optin_confirm, site_url
    from shruti.core.settings_store import imprint as imprint_settings

    # Registered details only when they are real. See `legal_footer`.
    imprint = {"visible": False}
    if session is not None:
        try:
            imprint = await imprint_settings(session)
        except Exception:                          # noqa: BLE001
            pass

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
        html=optin_confirm(token, imprint),
        to=email,
    )


def _site_url() -> str:
    import os
    return os.environ.get("SHRUTI_SITE_URL", "http://localhost:8200").rstrip("/")
