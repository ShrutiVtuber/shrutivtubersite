# SPDX-License-Identifier: AGPL-3.0-only
"""
Passkeys — WebAuthn registration and sign-in, for readers and the operator.

**Why passkeys and not "sign in with Google".** A passkey is a keypair held by
the device or the platform keychain. Signing in with one sends Apple or Google
no request, tells them nothing about this site, and hands this site no
third-party identity to store. It is a phone unlock rather than a federated
login: nicer to use, and on a site whose whole posture is minimal data sharing,
the only one that fits.

Practically it means Face ID, Touch ID, a fingerprint, or a Windows Hello PIN —
and because platform keychains sync, a passkey made on the phone works on the
laptop.

**The challenge is server-side state and must be.** A challenge the client
chooses is not a challenge. Each one is single-use, short-lived, and bound to
the browser by a cookie so a replay from elsewhere cannot use it.

**The relying party ID is the site's domain and cannot be guessed from a
request header.** A forged Host would otherwise let a credential be minted for
somewhere else, so it comes from configuration.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from webauthn import (
    generate_authentication_options, generate_registration_options,
    options_to_json, verify_authentication_response, verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor,
    ResidentKeyRequirement, UserVerificationRequirement,
)

from shruti.core.auth import SESSION_HOURS as ADMIN_SESSION_HOURS, issue_token
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.core.operator import operator_email
from shruti.core.sessions import SESSION_COOKIE, SESSION_DAYS, issue_session
from shruti.api.deps import require_admin
from shruti.models.accounts import Passkey, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/passkeys", tags=["passkeys"])

# The browser holds the challenge id here; the challenge itself never leaves
# the server.
CHALLENGE_COOKIE = "shruti_wak"
CHALLENGE_SECONDS = 300

# Challenges live in memory. They are single-use and expire in five minutes, so
# losing them on a restart costs one retry — and keeping them in Postgres would
# be writing a row per button press for data that is dead in seconds.
_challenges: dict[str, tuple[bytes, float, str]] = {}


def _allowed_origins() -> list[str]:
    """
    The origins a passkey may be created for or used from.

    The relying party is the site's own domain, and it CANNOT come from the
    Host or Origin header alone — a forged one would otherwise mint a
    credential scoped to somewhere else. So the header is only ever matched
    against this list, never trusted on its own.

    Local development is on the list because WebAuthn treats localhost as a
    secure context and there is no other way to try this on a laptop. A
    credential made at localhost is scoped to localhost and is useless
    anywhere else, which is exactly the property that makes including it safe.
    """
    site = os.environ.get("SHRUTI_SITE_URL", "http://localhost:8200").rstrip("/")
    allowed = [site]
    if os.environ.get("SHRUTI_ENV", "dev") != "prod":
        allowed += [
            "http://localhost:8200", "http://127.0.0.1:8200",
            "http://localhost:4321", "http://127.0.0.1:4321",
        ]
    extra = os.environ.get("SHRUTI_PASSKEY_ORIGINS", "")
    allowed += [o.strip().rstrip("/") for o in extra.split(",") if o.strip()]
    # Dedupe, order preserved: the configured site URL stays the default.
    return list(dict.fromkeys(allowed))


def _relying_party(request: Request) -> tuple[str, str]:
    """
    Return `(rp_id, origin)` for this request.

    The Origin header picks WHICH of the allowed origins is in play; it cannot
    introduce one. An unrecognised origin falls back to the configured site,
    where the WebAuthn check will then fail — refusing is the right outcome.
    """
    sent = (request.headers.get("origin") or "").rstrip("/")
    allowed = _allowed_origins()
    origin = sent if sent in allowed else allowed[0]
    return (urlparse(origin).hostname or "localhost"), origin


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _now() -> float:
    return datetime.now(timezone.utc).timestamp()


def _sweep() -> None:
    dead = [k for k, (_, expires, _) in _challenges.items() if expires < _now()]
    for k in dead:
        _challenges.pop(k, None)


def _store_challenge(response: Response, challenge: bytes, purpose: str, secure: bool) -> None:
    _sweep()
    key = secrets.token_urlsafe(16)
    _challenges[key] = (challenge, _now() + CHALLENGE_SECONDS, purpose)
    response.set_cookie(
        CHALLENGE_COOKIE, key, max_age=CHALLENGE_SECONDS, httponly=True,
        samesite="lax", secure=secure, path="/",
    )


def _take_challenge(request: Request, purpose: str) -> bytes:
    """Single use: taken, not read. A replayed challenge finds nothing."""
    key = request.cookies.get(CHALLENGE_COOKIE)
    if not key:
        raise HTTPException(400, "that attempt expired — start again")
    entry = _challenges.pop(key, None)
    if entry is None:
        raise HTTPException(400, "that attempt expired — start again")
    challenge, expires, stored_purpose = entry
    if expires < _now() or stored_purpose != purpose:
        raise HTTPException(400, "that attempt expired — start again")
    return challenge


def _secure(request: Request) -> bool:
    return request.url.scheme == "https" or \
        request.headers.get("x-forwarded-proto") == "https"


# ── registering a passkey ───────────────────────────────────────────────────

@router.post("/register/options")
async def register_options(
    request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Options for creating a passkey. Signed-in readers only."""
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")

    existing = (
        await session.execute(select(Passkey).where(Passkey.user_id == user.id))
    ).scalars().all()

    rp_id, _ = _relying_party(request)
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="Shruti",
        user_id=str(user.id).encode(),
        user_name=user.email,
        user_display_name=user.display_name or user.email,
        # Excluding what is already registered stops a device silently making a
        # second credential for itself, which looks like success and is not.
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=_unb64(p.credential_id)) for p in existing
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(
            # A discoverable credential is what lets someone sign in without
            # typing an email first — the whole point of "just use your phone".
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )
    _store_challenge(response, options.challenge, "register", _secure(request))
    return json.loads(options_to_json(options))


class RegisterIn(BaseModel):
    credential: dict
    label: str = ""


@router.post("/register", status_code=201)
async def register(
    body: RegisterIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")

    challenge = _take_challenge(request, "register")
    rp_id, origin = _relying_party(request)
    try:
        result = verify_registration_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_origin=origin,
            expected_rp_id=rp_id,
        )
    except Exception as exc:                       # noqa: BLE001
        log.info("passkey registration rejected: %s", type(exc).__name__)
        raise HTTPException(400, "that passkey could not be registered")

    session.add(Passkey(
        user_id=user.id,
        credential_id=_b64(result.credential_id),
        public_key=_b64(result.credential_public_key),
        sign_count=result.sign_count,
        transports=",".join(body.credential.get("response", {}).get("transports", []) or []),
        label=body.label.strip()[:60] or "Passkey",
    ))
    await session.commit()
    return {"ok": True}


# ── signing in with one ─────────────────────────────────────────────────────

@router.post("/signin/options")
async def signin_options(request: Request, response: Response) -> dict:
    """
    Options for signing in.

    No credential list and no email: with discoverable credentials the browser
    offers whatever it holds for this site, which is what makes "use your
    phone" a single tap. It also means this endpoint reveals nothing — asking
    it about an address is not possible, because it never takes one.
    """
    rp_id, _ = _relying_party(request)
    options = generate_authentication_options(
        rp_id=rp_id,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    _store_challenge(response, options.challenge, "signin", _secure(request))
    return json.loads(options_to_json(options))


class SignInIn(BaseModel):
    credential: dict


@router.post("/signin")
async def signin(
    body: SignInIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    challenge = _take_challenge(request, "signin")
    rp_id, origin = _relying_party(request)

    raw_id = body.credential.get("id") or body.credential.get("rawId")
    if not raw_id:
        raise HTTPException(400, "that passkey could not be used")

    row = (
        await session.execute(select(Passkey).where(Passkey.credential_id == raw_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(400, "that passkey could not be used")

    try:
        result = verify_authentication_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_origin=origin,
            expected_rp_id=rp_id,
            credential_public_key=_unb64(row.public_key),
            credential_current_sign_count=row.sign_count,
        )
    except Exception as exc:                       # noqa: BLE001
        log.info("passkey sign-in rejected: %s", type(exc).__name__)
        raise HTTPException(400, "that passkey could not be used")

    # A counter that goes BACKWARDS means the credential has probably been
    # cloned. Many platform authenticators always send zero, which is not a
    # warning — that is "not supported", and only a genuine decrease is refused.
    if result.new_sign_count and result.new_sign_count < row.sign_count:
        log.warning("passkey %s sign count went backwards; refusing", row.id)
        raise HTTPException(400, "that passkey could not be used")

    row.sign_count = result.new_sign_count
    row.last_used_at = datetime.now(timezone.utc)

    user = (
        await session.execute(select(User).where(User.id == row.user_id))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(400, "that passkey could not be used")
    await session.commit()

    response.set_cookie(
        SESSION_COOKIE, issue_session(user.id, user.email),
        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=_secure(request), path="/",
    )
    response.delete_cookie(CHALLENGE_COOKIE, path="/")
    return {"ok": True, "signedIn": True}


# ── managing them ───────────────────────────────────────────────────────────

@router.get("")
async def list_passkeys(
    request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")
    rows = (
        await session.execute(
            select(Passkey).where(Passkey.user_id == user.id).order_by(Passkey.id)
        )
    ).scalars().all()
    return {
        "passkeys": [
            {
                "id": p.id, "label": p.label,
                "addedAt": p.created_at.isoformat() if p.created_at else None,
                "lastUsedAt": p.last_used_at.isoformat() if p.last_used_at else None,
            }
            for p in rows
        ]
    }


@router.delete("/{passkey_id}")
async def remove_passkey(
    passkey_id: int, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first")
    row = (
        await session.execute(
            select(Passkey).where(Passkey.id == passkey_id, Passkey.user_id == user.id)
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such passkey")

    # Removing the last passkey is ALWAYS allowed, including when there is no
    # password. Every account here has a verified email and the emailed-link
    # sign-in, so there is no lockout to protect anyone from — and the moment
    # someone most needs this button is when a phone has been stolen, which is
    # exactly when a "set a password first" refusal would be at its worst.
    await session.delete(row)
    await session.commit()
    return {"ok": True}


# ── the operator's own passkeys ─────────────────────────────────────────────
#
# The admin is not a row in the user table — there is one operator and
# inventing a second user was never worth the surface — so its passkeys hang
# off `is_operator` rather than a foreign key. Same credentials, same
# verification, a different session cookie at the end.


@router.post("/admin/register/options")
async def admin_register_options(
    request: Request, response: Response,
    subject: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    rp_id, _ = _relying_party(request)
    existing = (
        await session.execute(select(Passkey).where(Passkey.is_operator.is_(True)))
    ).scalars().all()
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="Shruti — admin",
        user_id=b"operator",
        user_name=subject,
        user_display_name="Shruti",
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=_unb64(p.credential_id)) for p in existing
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            # The admin rewrites the site, so a passkey that unlocks it should
            # require the face, the finger or the PIN — not merely possession
            # of an unlocked phone.
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    _store_challenge(response, options.challenge, "admin-register", _secure(request))
    return json.loads(options_to_json(options))


@router.post("/admin/register", status_code=201)
async def admin_register(
    body: RegisterIn, request: Request,
    subject: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    challenge = _take_challenge(request, "admin-register")
    rp_id, origin = _relying_party(request)
    try:
        result = verify_registration_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_origin=origin,
            expected_rp_id=rp_id,
        )
    except Exception as exc:                       # noqa: BLE001
        log.info("admin passkey registration rejected: %s", type(exc).__name__)
        raise HTTPException(400, "that passkey could not be registered")

    session.add(Passkey(
        is_operator=True,
        credential_id=_b64(result.credential_id),
        public_key=_b64(result.credential_public_key),
        sign_count=result.sign_count,
        transports=",".join(body.credential.get("response", {}).get("transports", []) or []),
        label=body.label.strip()[:60] or "Passkey",
    ))
    await session.commit()
    return {"ok": True}


@router.post("/admin/signin/options")
async def admin_signin_options(request: Request, response: Response) -> dict:
    rp_id, _ = _relying_party(request)
    options = generate_authentication_options(
        rp_id=rp_id, user_verification=UserVerificationRequirement.REQUIRED,
    )
    _store_challenge(response, options.challenge, "admin-signin", _secure(request))
    return json.loads(options_to_json(options))


@router.post("/admin/signin")
async def admin_signin(
    body: SignInIn, request: Request, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    challenge = _take_challenge(request, "admin-signin")
    rp_id, origin = _relying_party(request)

    raw_id = body.credential.get("id") or body.credential.get("rawId")
    row = (
        await session.execute(
            select(Passkey).where(
                Passkey.credential_id == (raw_id or ""), Passkey.is_operator.is_(True)
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(400, "that passkey could not be used")

    try:
        result = verify_authentication_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_origin=origin,
            expected_rp_id=rp_id,
            credential_public_key=_unb64(row.public_key),
            credential_current_sign_count=row.sign_count,
            require_user_verification=True,
        )
    except Exception as exc:                       # noqa: BLE001
        log.info("admin passkey sign-in rejected: %s", type(exc).__name__)
        raise HTTPException(400, "that passkey could not be used")

    if result.new_sign_count and result.new_sign_count < row.sign_count:
        log.warning("admin passkey %s sign count went backwards; refusing", row.id)
        raise HTTPException(400, "that passkey could not be used")

    row.sign_count = result.new_sign_count
    row.last_used_at = datetime.now(timezone.utc)
    await session.commit()

    email = await operator_email(session) or ""
    response.set_cookie(
        "shruti_session", issue_token(email),
        httponly=True, samesite="lax", secure=get_settings().is_production,
        max_age=ADMIN_SESSION_HOURS * 3600, path="/",
    )
    response.delete_cookie(CHALLENGE_COOKIE, path="/")
    return {"ok": True, "signedIn": True}


@router.get("/admin")
async def admin_list(
    subject: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    rows = (
        await session.execute(
            select(Passkey).where(Passkey.is_operator.is_(True)).order_by(Passkey.id)
        )
    ).scalars().all()
    return {
        "passkeys": [
            {
                "id": p.id, "label": p.label,
                "addedAt": p.created_at.isoformat() if p.created_at else None,
                "lastUsedAt": p.last_used_at.isoformat() if p.last_used_at else None,
            }
            for p in rows
        ]
    }


@router.delete("/admin/{passkey_id}")
async def admin_remove(
    passkey_id: int,
    subject: str = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    row = (
        await session.execute(
            select(Passkey).where(
                Passkey.id == passkey_id, Passkey.is_operator.is_(True)
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such passkey")
    # The operator always keeps a password, so removing the last passkey never
    # locks her out — no guard needed here, unlike a reader account.
    await session.delete(row)
    await session.commit()
    return {"ok": True}
