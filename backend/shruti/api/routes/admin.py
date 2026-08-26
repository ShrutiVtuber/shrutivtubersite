# SPDX-License-Identifier: AGPL-3.0-only
"""
The admin surface — the reason the content model exists.

Everything here is behind `require_admin`. The design constraint this serves:
**the site ships before the art does**, so the two operations that matter most
are toggling a block's visibility and attaching an image to one that has none.
Both are one request.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, Response, UploadFile,
)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from shruti.api.deps import require_admin
from shruti.core.operator import session_stamp
from shruti.core.auth import authenticate, issue_token
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models.accounts import SavedChart, User
from shruti.models import (BannedEmail, Course, FanArt, Product, ProductPhoto, 
    ContactMessage, Credit, GrowthItem, Media, OfficialPlace, ProfileField,
    Project, Question,
    CardDesign, Outfit, ScheduleEntry, Section, SocialLink, Sponsor, Tool,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

# Every table the admin may edit, by the name used in the URL.
EDITABLE: dict[str, type[SQLModel]] = {
    "sections": Section,
    "projects": Project,
    "tools": Tool,
    "links": SocialLink,
    "profile-fields": ProfileField,
    "credits": Credit,
    "schedule": ScheduleEntry,
    "fan-art": FanArt,
    "sponsors": Sponsor,
    "outfits": Outfit,
    "card-designs": CardDesign,
    "growth": GrowthItem,
    "official": OfficialPlace,
}

ALLOWED_IMAGE = {
    "image/png": ".png", "image/jpeg": ".jpg",
    "image/webp": ".webp", "image/avif": ".avif", "image/svg+xml": ".svg",
}


# ── session ─────────────────────────────────────────────────────────────────

class LoginIn(BaseModel):
    email: str
    password: str = Field(min_length=1)


@router.post("/login")
async def login(
    payload: LoginIn, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.core.operator import verify as verify_operator

    if not await verify_operator(session, payload.email, payload.password):
        # One message for both failures. Distinguishing "no such user" from
        # "wrong password" tells an attacker which half to work on.
        raise HTTPException(401, "email or password is wrong")

    token = issue_token(payload.email, await session_stamp(session))
    response.set_cookie(
        "shruti_session", token,
        httponly=True, samesite="lax",
        secure=get_settings().is_production,
        max_age=12 * 3600, path="/",
    )
    return {"token": token, "expiresInHours": 12}


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("shruti_session", path="/")
    return {"status": "signed out"}


@router.get("/me")
async def me(subject: str = Depends(require_admin)) -> dict:
    return {"email": subject}


# Specific paths MUST be declared before the generic "/{kind}" routes below.
# FastAPI matches in definition order, so with the catch-all first, a POST to
# /api/admin/media is read as kind="media" and rejected for having a multipart
# body instead of JSON. It was.

# ── media ───────────────────────────────────────────────────────────────────

def _media_payload(m: Media) -> dict:
    """
    One shape for an image, wherever it is returned from.

    Upload, patch and the listing all answered differently before — tags as a
    string from one and a list from another — which makes a caller's handling
    depend on which call it happened to come from.
    """
    from shruti.core.storage import public_url

    return {
        "id": m.id,
        "filename": m.filename,
        "url": public_url(m.filename, m.storage_backend),
        "mimeType": m.mime_type,
        "width": m.width,
        "height": m.height,
        "sizeBytes": m.size_bytes,
        "title": m.title,
        "tags": [t for t in m.tags.split(",") if t],
        "altText": m.alt_text,
        "credit": m.credit,
        "creditUrl": m.credit_url,
        "storage": m.storage_backend,
        "createdAt": m.created_at.isoformat() if m.created_at else None,
    }


def _clean_tags(raw: str) -> str:
    """
    Comma-separated, trimmed, de-duplicated, order kept.

    Order is kept because she typed it in an order; sorting would be tidier and
    would also quietly rearrange what she wrote every time she saved.
    """
    out: list[str] = []
    for tag in (raw or "").split(","):
        tag = " ".join(tag.split())
        if tag and tag.lower() not in {t.lower() for t in out}:
            out.append(tag)
    return ",".join(out)



@router.post("/media", status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(""),
    tags: str = Form(""),
    alt_text: str = Form(""),
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Upload one image.

    Named by content hash, so the same file uploaded twice is stored once and
    the URL is stable. The declared content type is checked against an
    allow-list rather than trusted — a browser will send whatever it is told.

    A title and tags may be given at the same time, because the moment of
    uploading is the moment you know what the thing is. They are stored beside
    the hash, never in place of it.
    """
    s = get_settings()
    if file.content_type not in ALLOWED_IMAGE:
        raise HTTPException(
            415, f"unsupported type {file.content_type!r}; "
                 f"allowed: {sorted(ALLOWED_IMAGE)}"
        )

    data = await file.read()
    limit = s.max_upload_mb * 1024 * 1024
    if len(data) > limit:
        raise HTTPException(413, f"file is larger than {s.max_upload_mb} MB")
    if not data:
        raise HTTPException(422, "the file is empty")

    digest = hashlib.sha256(data).hexdigest()[:32]
    filename = f"{digest}{ALLOWED_IMAGE[file.content_type]}"

    existing = (await session.execute(
        select(Media).where(Media.filename == filename)
    )).scalars().first()
    if existing:
        # The same bytes, so the same file — but this upload may carry a name
        # the first one did not, and dropping it would be silently ignoring
        # what was just typed. Only fills gaps; never overwrites.
        changed = False
        for field, value in (("title", title), ("tags", tags), ("alt_text", alt_text)):
            if value.strip() and not getattr(existing, field):
                setattr(existing, field, value.strip())
                changed = True
        if changed:
            await session.commit()
            await session.refresh(existing)
        return _media_payload(existing) | {"deduped": True}

    width = height = None
    try:
        from io import BytesIO

        from PIL import Image

        with Image.open(BytesIO(data)) as im:
            width, height = im.size
    except Exception:                              # noqa: BLE001 — SVG has no raster size
        pass

    # Storage decides where it goes: R2 when configured, disk otherwise, and
    # disk again if R2 is unreachable — an upload should not be lost because a
    # bucket is having a bad day.
    from shruti.core.storage import put as store_media

    stored = await store_media(filename, data, file.content_type)

    row = Media(filename=filename, mime_type=file.content_type,
                width=width, height=height, size_bytes=len(data),
                storage_backend=stored.backend,
                title=title.strip(), tags=_clean_tags(tags),
                alt_text=alt_text.strip())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _media_payload(row)


# ── inbox ───────────────────────────────────────────────────────────────────

@router.get("/inbox/messages")
async def inbox(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    rows = (await session.execute(
        select(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(200)
    )).scalars().all()
    return [r.model_dump() for r in rows]


@router.get("/inbox/questions")
async def question_queue(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """Everything, approved or not — nothing is public until it is approved."""
    rows = (await session.execute(
        select(Question).order_by(Question.created_at.desc()).limit(200)
    )).scalars().all()
    return [r.model_dump() for r in rows]


# ── generic CRUD over the editable tables ───────────────────────────────────

def _model(kind: str) -> type[SQLModel]:
    if kind not in EDITABLE:
        raise HTTPException(404, f"unknown collection; try one of {sorted(EDITABLE)}")
    return EDITABLE[kind]


def _order(model: type[SQLModel]):
    return model.position if hasattr(model, "position") else model.id



# NOTE ON ORDER: everything below this line must stay ABOVE the generic
# /{kind} routes. FastAPI matches in definition order, so a /{kind} route
# declared first will happily match /claim and /reset as table names and
# answer 401 for a route that should be public. That has now bitten twice
# in this file — the first time it was /media.

# ── claiming the site, and resetting the password ───────────────────────────


class ClaimIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=200)
    token: str


@router.get("/claim")
async def claim_status(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Whether the site has an operator yet.

    Public, and safe to be: an unclaimed site is a fact anyone can establish by
    trying to log in, and saying so plainly is what lets the admin show a setup
    screen instead of a login that cannot succeed. Minting the token on this
    call means it reaches the log the first time someone actually looks.
    """
    from shruti.core.operator import is_claimed, setup_token

    claimed = await is_claimed(session)
    if not claimed:
        await setup_token(session)     # logged, not returned
    return {"claimed": claimed}


@router.post("/claim", status_code=201)
async def claim_site(
    body: ClaimIn, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Claim the site once, with the setup token from the server log.

    Reading the log means having the box, which is the fact being proven. An
    unclaimed admin on a public site is otherwise a takeover waiting for
    whoever loads the page first.
    """
    from shruti.core.operator import claim

    if not await claim(session, body.email, body.password, body.token):
        # One message for every failure: already claimed, wrong token, or a
        # race. Distinguishing them tells an attacker which half to work on.
        raise HTTPException(400, "that setup token is not valid, or the site is already claimed")

    token = issue_token(body.email, await session_stamp(session))
    response.set_cookie(
        "shruti_session", token, httponly=True, samesite="lax",
        secure=get_settings().is_production, max_age=12 * 3600, path="/",
    )
    return {"ok": True}


class ResetRequestIn(BaseModel):
    email: EmailStr


@router.post("/reset/request", status_code=202)
async def request_reset(
    body: ResetRequestIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Send a password-reset link to the operator's address.

    The reply is identical whether or not the address is the operator's —
    otherwise this form tells a stranger who runs the site.
    """
    from shruti.core.mail import send
    from shruti.core.operator import operator_email
    from shruti.core.sessions import issue_link

    address = await operator_email(session)
    if address and address == body.email.strip().lower():
        import os

        site_url = os.environ.get("SHRUTI_SITE_URL", "http://localhost:8200").rstrip("/")
        link = issue_link(address, purpose="admin-reset")
        await send(
            subject="Reset your admin password",
            body=(
                "A password reset was requested for the shrutivtuber.com admin.\n\n"
                f"{site_url}/admin/reset?token={link}\n\n"
                "It works once and expires in 20 minutes. If this was not you, "
                "nothing has happened and you can ignore it."
            ),
            to=address,
        )
    return {"ok": True, "checkEmail": True}


class ResetIn(BaseModel):
    token: str
    password: str = Field(min_length=12, max_length=200)


@router.post("/reset")
async def do_reset(
    body: ResetIn, response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from shruti.core.operator import operator_email, set_password
    from shruti.core.sessions import read_link

    email = read_link(body.token, purpose="admin-reset")
    if not email or email != await operator_email(session):
        raise HTTPException(400, "that link has expired or has already been used")

    await set_password(session, body.password)
    token = issue_token(email, await session_stamp(session))
    response.set_cookie(
        "shruti_session", token, httponly=True, samesite="lax",
        secure=get_settings().is_production, max_age=12 * 3600, path="/",
    )
    return {"ok": True}

@router.get("/media")
async def list_media(
    q: str = "",
    tag: str = "",
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """
    Everything uploaded, newest first, with where it actually lives.

    `q` searches the name, the tags and the alt text — the three things she
    wrote — and the filename, which is only useful when someone already has a
    URL in hand and wants to know what it is.
    """

    stmt = select(Media).order_by(Media.id.desc())
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            Media.title.ilike(like)
            | Media.tags.ilike(like)
            | Media.alt_text.ilike(like)
            | Media.filename.ilike(like)
        )
    if tag.strip():
        # Padded on both sides so "art" cannot match "fan-art": tags are stored
        # comma-separated and matching the bare word would match inside one.
        stmt = stmt.where(
            func.concat(",", Media.tags, ",").ilike(f"%,{tag.strip()},%")
        )

    rows = (await session.execute(stmt)).scalars().all()
    return [_media_payload(m) for m in rows]


class MediaPatch(BaseModel):
    """
    Everything about an image except the image.

    All optional, and only what is sent is applied: a patch that renames a file
    must not blank its alt text just by not mentioning it. That mistake has
    been made in this codebase before, with an upsert that replaced instead of
    patching and wiped the fields it was not given.
    """

    title: str | None = None
    tags: str | None = None
    alt_text: str | None = None
    credit: str | None = None
    credit_url: str | None = None


@router.patch("/media/{media_id}")
async def update_media(
    media_id: int,
    body: MediaPatch,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """Rename, retag or re-describe. Never touches the file or the URL."""
    row = await session.get(Media, media_id)
    if row is None:
        raise HTTPException(404, "no such media")

    for field, value in body.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        setattr(row, field, _clean_tags(value) if field == "tags" else value.strip())

    await session.commit()
    await session.refresh(row)
    return _media_payload(row)


# Everything that can point at an image, and what to call it when it does.
MEDIA_USERS: tuple[tuple[type, str], ...] = (
    (Section, "page block"),
    (Project, "project"),
    (Tool, "tool"),
    (FanArt, "fan work"),
    (Product, "product"),
    (ProductPhoto, "product photograph"),
    (Course, "class or workshop"),
    (Sponsor, "sponsor"),
    (Outfit, "outfit"),
    # Lives in models.accounts rather than models, which is exactly why the
    # test below now walks BOTH modules — scanning one and calling it "every
    # model" is how this one slipped through unguarded.
    (SavedChart, "kept chart"),
    (CardDesign, "share card design"),
)


def _media_columns(model: type) -> tuple[str, ...]:
    """
    Every column on this model that points at `media.id`, found rather than
    listed.

    The loop used to check `model.media_id` and nothing else. Sponsor carries
    two — a mark for light backgrounds and one for dark — and the second would
    have been invisible to the guard: deleting that image would have succeeded,
    blanked the logo on a live page, and turned up later looking like a
    different bug. Reading the foreign keys means the next model with two is
    covered without anybody remembering.
    """
    out = []
    for column in model.__table__.columns:                       # type: ignore[attr-defined]
        for fk in column.foreign_keys:
            if fk.target_fullname == "media.id":
                out.append(column.name)
    return tuple(out)


@router.delete("/media/{media_id}", status_code=204)
async def delete_media(
    media_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> Response:
    """
    Remove an image, file and row together.

    **Refused while anything still uses it**, and the refusal says what. The
    alternative is to null the references, which silently blanks a picture on a
    live page: the deletion succeeds and the damage turns up later, somewhere
    else, looking like a different bug.
    """
    row = await session.get(Media, media_id)
    if row is None:
        raise HTTPException(404, "no such media")

    used: list[str] = []
    for model, noun in MEDIA_USERS:
        for column in _media_columns(model):
            rows = (
                await session.execute(
                    select(model).where(getattr(model, column) == media_id)
                )
            ).scalars().all()
            for r in rows:
                label = (
                    getattr(r, "title", None) or getattr(r, "name", None)
                    or getattr(r, "key", None) or f"#{r.id}"
                )
                used.append(f"{noun} \u201c{label}\u201d")

    if used:
        raise HTTPException(
            409,
            "still in use by " + ", ".join(used)
            + ". Point those at something else first, and then this can go.",
        )

    # The file first. A row removed while its file survives leaves an orphan
    # nothing can find or delete; a file removed while its row survives shows
    # as a broken image, which at least says out loud that something is wrong.
    from shruti.core.storage import delete as delete_stored

    await delete_stored(row.filename, row.storage_backend)
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


# ── people ──────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    q: str = "",
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """
    Everyone with an account, newest first.

    Deliberately thin. This screen exists to help someone who cannot get in and
    to close an account when it has to be closed — not to browse what people
    have told the site about themselves. Birth data is never in this payload.
    """
    from shruti.models import Supporter

    stmt = select(User).order_by(User.id.desc())
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(User.email.ilike(like) | User.display_name.ilike(like))
    users = (await session.execute(stmt.limit(500))).scalars().all()

    supporters = {
        s.email: s
        for s in (await session.execute(select(Supporter))).scalars().all()
        if s.email
    }

    return [
        {
            "id": u.id,
            "email": u.email,
            "displayName": u.display_name,
            "verified": u.email_verified_at is not None,
            "hasPassword": bool(u.password_hash),
            "supporter": u.email in supporters,
            "lastSeenAt": u.last_seen_at.isoformat() if u.last_seen_at else None,
            "createdAt": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/users/{user_id}/signin-link", status_code=202)
async def resend_signin_link(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Send someone the link that gets them in.

    The whole of "help them fix it": there is no password to read and none to
    set on their behalf, which is the point of the design. A link to their own
    address is the only door, and it is the same door they would have used.
    """
    from shruti.api.routes.accounts import _send_magic_link

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "no such account")
    await _send_magic_link(user.email)
    return {"ok": True, "sentTo": user.email}


class BanIn(BaseModel):
    reason: str = ""


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    body: BanIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Close an account for good, and bar the address.

    The order is the whole of it:

      1. Build their export — the same one they could have downloaded.
      2. **Send it, and say what is happening, before anything is deleted.**
         Afterwards there is no address left to send to, and a deletion nobody
         was told about is the version of this that gets complained about.
      3. Delete, by the same path self-service deletion takes, so it reaches
         the newsletter and keeps the anonymised consent trail that proves the
         deletion was lawful.
      4. Record the ban as a hash, so the address cannot register again and
         cannot be read back out of the list either.

    If the mail does not go, nothing is deleted. Losing someone's data while
    failing to give them a copy is the one outcome worth refusing outright.
    """
    from shruti.api.routes.accounts import erase, export_for
    from shruti.core import mail
    from shruti.core.bans import fingerprint, hint

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "no such account")

    email = user.email
    payload = await export_for(user, session)

    sent = await mail.send(
        subject="Your account on shrutivtuber.com has been closed",
        to=email,
        body=(
            "Your account has been closed and will not be reopened, and this "
            "address cannot be used to register again.\n\n"
            "Everything the site held about you is below, as a copy for your "
            "records. It has now been deleted, apart from a dated record that "
            "consent was given and withdrawn, which carries no birth data and "
            "no longer carries your address — that record is what shows the "
            "deletion itself was lawful.\n\n"
            "If you believe this is a mistake, reply to this message.\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        ),
    )
    if not sent.sent:
        raise HTTPException(
            502,
            "nothing was deleted: their copy could not be sent "
            f"({sent.error or 'the mail did not go'}). "
            "Fix the mail and try again — deleting someone's data without "
            "giving them a copy is not something to do quietly.",
        )

    await erase(user, session)

    session.add(
        BannedEmail(email_hash=fingerprint(email), reason=body.reason.strip(),
                    hint=hint(email))
    )
    await session.commit()
    return {"ok": True, "closed": hint(email), "exportSentTo": hint(email)}


@router.get("/bans")
async def list_bans(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    rows = (
        await session.execute(select(BannedEmail).order_by(BannedEmail.id.desc()))
    ).scalars().all()
    return [
        {
            "id": b.id,
            "hint": b.hint,
            "reason": b.reason,
            "createdAt": b.created_at.isoformat() if b.created_at else None,
        }
        for b in rows
    ]


class UnbanIn(BaseModel):
    """Lifting a ban needs the address, because the list only holds a hash."""

    email: str


@router.post("/bans/lift")
async def lift_ban(
    body: UnbanIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Let an address register again.

    It takes the address rather than a row id on purpose: the list cannot tell
    her which address a row is, so lifting one means knowing whose it is. That
    is a feature — an unban should be a decision about a person, not a click on
    a row whose owner nobody can name.
    """
    from shruti.core.bans import fingerprint

    row = (
        await session.execute(
            select(BannedEmail).where(BannedEmail.email_hash == fingerprint(body.email))
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "that address is not banned")
    await session.delete(row)
    await session.commit()
    return {"ok": True}


# ── site settings ───────────────────────────────────────────────────────────

class SettingsIn(BaseModel):
    """Arbitrary key/value, validated by the caller knowing the keys."""

    values: dict[str, str]


@router.get("/settings")
async def read_settings(
    prefix: str = "",
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    from shruti.core.settings_store import get_all

    return {"settings": await get_all(session, prefix)}


@router.put("/settings")
async def write_settings(
    body: SettingsIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    from shruti.core.settings_store import SECTIONS, get_all, put_many

    # Keys are namespaced and short; nothing here is a path or a template.
    clean = {
        k: v for k, v in body.values.items()
        if k and len(k) <= 64 and len(v) <= 500
    }

    # **Hiding a section must never take away something somebody bought.**
    #
    # Hiding the shop or the horoscopes costs a visitor a browse page. Hiding
    # classes would 404 the page a student watches their lessons on, and they
    # paid for those — a section being "not ready" is a fact about the site,
    # not about their purchase. So this refuses rather than quietly locking
    # them out, and says how many people it would have affected.
    if clean.get(SECTIONS["classes"]) == "0":
        from shruti.models import Entitlement

        held = (
            await session.execute(
                select(Entitlement).where(Entitlement.revoked_at.is_(None))
            )
        ).scalars().all()
        if held:
            raise HTTPException(
                409,
                f"{len(held)} " + ("person has" if len(held) == 1 else "people have")
                + " access to a class. Hiding the section would 404 the page they"
                " watch on, and they paid for it. Unpublish the individual"
                " courses instead — that stops new sales without taking anything"
                " away.",
            )

    await put_many(session, clean)
    return {"ok": True, "settings": await get_all(session)}


# ─────────────────────────────────────────────────────────────────────────────
# THE GENERIC COLLECTION ROUTES. THEY MUST STAY LAST IN THIS FILE.
#
# FastAPI matches in declaration order, so `/{kind}` swallows every specific
# path declared after it. This has now bitten three times: POST /media, then
# GET /claim, then — found by actually clicking through the admin — GET /media
# and GET /settings, both of which had been 404ing since the day they were
# written. Neither looked broken: the media library rendered as empty, and the
# imprint form rendered as blank fields, which is exactly what an unused
# feature looks like.
#
# Twice the fix was "move this one route up", and twice it worked and left the
# trap armed. So the rule is structural now: every specific route goes ABOVE
# this banner, the catch-alls stay below it, and a test asserts the ordering
# rather than trusting the next person to read a comment.
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{kind}")
async def list_items(
    kind: str,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """Everything, hidden rows included — this is the editing view."""
    model = _model(kind)
    rows = (await session.execute(select(model).order_by(_order(model)))).scalars().all()
    return [r.model_dump() for r in rows]


def _coerced(model: type, payload: dict) -> dict:
    """
    Values shaped the way their columns expect.

    A SQLModel table class does not validate on construction, so a datetime
    column handed the string a form posted takes it verbatim and asyncpg
    refuses it at the very last moment — "expected a datetime, got 'str'" —
    as a 500 with nothing useful said. The admin sends JSON, and JSON has no
    datetime, so somebody has to do this and it is better done once here than
    remembered at every call site.

    Only what is actually understood is touched; anything else passes through
    to be rejected by the database as before.
    """
    fields = getattr(model, "model_fields", {})
    out: dict = {}
    for key, value in payload.items():
        field = fields.get(key)
        annotation = getattr(field, "annotation", None) if field else None
        wants_dt = annotation is datetime or (
            # Optional[datetime] and friends
            datetime in getattr(annotation, "__args__", ())
        )
        if wants_dt and isinstance(value, str):
            if not value.strip():
                out[key] = None
                continue
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(422, f"{key} is not a date and time I can read")
            # Naive means the sender did not say; the whole schema is UTC.
            out[key] = parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        else:
            out[key] = value
    return out


@router.post("/{kind}", status_code=201)
async def create_item(
    kind: str,
    payload: dict,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    model = _model(kind)
    payload.pop("id", None)
    try:
        row = model(**_coerced(model, payload))
    except Exception as exc:                       # noqa: BLE001
        raise HTTPException(422, f"could not create: {exc}")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row.model_dump()


@router.patch("/{kind}/{item_id}")
async def update_item(
    kind: str,
    item_id: int,
    payload: dict,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    model = _model(kind)
    row = await session.get(model, item_id)
    if row is None:
        raise HTTPException(404, "no such item")

    payload.pop("id", None)
    payload.pop("created_at", None)
    for key, value in _coerced(model, payload).items():
        if not hasattr(row, key):
            raise HTTPException(422, f"{kind} has no field {key!r}")
        setattr(row, key, value)
    if hasattr(row, "updated_at"):
        row.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(row)
    return row.model_dump()


@router.post("/{kind}/{item_id}/visibility")
async def set_visibility(
    kind: str,
    item_id: int,
    visible: bool,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    The one-click operation the whole content model exists for.

    Blocks default to hidden and are revealed as the art for them arrives.
    """
    model = _model(kind)
    row = await session.get(model, item_id)
    if row is None:
        raise HTTPException(404, "no such item")
    if not hasattr(row, "visible"):
        raise HTTPException(422, f"{kind} cannot be hidden")
    row.visible = visible
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"id": item_id, "visible": visible}


@router.post("/{kind}/reorder")
async def reorder(
    kind: str,
    order: list[int],
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """Positions are rewritten from the given id order, spaced by ten."""
    model = _model(kind)
    if not hasattr(model, "position"):
        raise HTTPException(422, f"{kind} is not ordered")
    for index, item_id in enumerate(order):
        row = await session.get(model, item_id)
        if row is None:
            raise HTTPException(404, f"no such item: {item_id}")
        row.position = (index + 1) * 10
    await session.commit()
    return {"reordered": len(order)}


@router.delete("/{kind}/{item_id}", status_code=204)
async def delete_item(
    kind: str,
    item_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> Response:
    model = _model(kind)
    row = await session.get(model, item_id)
    if row is None:
        raise HTTPException(404, "no such item")
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)
