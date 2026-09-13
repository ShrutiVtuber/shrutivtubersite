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
import re
import json
import logging
import os
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
from shruti.models.guides import Game
from shruti.models.accounts import SavedChart, User
from shruti.models import (BannedEmail, Course, FanArt, Product, ProductPhoto, 
    ContactMessage, Credit, GrowthItem, Media, OfficialPlace, ProfileField,
    Project, Question,
    CardDesign, Outfit, ScheduleEntry, Section, SocialLink, Sponsor, Tool,
    Lesson, Module, Poll, PollOption, Tier,
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

# Alert sounds. WAV and OGG only, and small: every one of these is preloaded
# into the overlay on connect, so the total is what her streaming machine holds
# in memory for the whole session, not what it fetches when something happens.
ALLOWED_AUDIO = {
    "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/wave": ".wav",
    "audio/ogg": ".ogg", "application/ogg": ".ogg",
}
MAX_SOUND_BYTES = 512 * 1024


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
    secure = get_settings().is_production
    response.set_cookie(
        "shruti_session", token,
        httponly=True, samesite="lax",
        secure=secure,
        max_age=12 * 3600, path="/",
    )
    await _also_a_reader(session, response, payload.email, secure)
    return {"token": token, "expiresInHours": 12}


async def _also_a_reader(
    session: AsyncSession, response: Response, email: str, secure: bool,
) -> None:
    """
    Sign the operator in as a MEMBER too, on the same click.

    ⚠ **Two cookies, two systems, one person.** The admin session and the
    reader session are deliberately separate — one is scoped to the desk and
    lasts twelve hours, the other belongs to a visitor and lasts months — and
    holding one has never implied the other. Which meant she could sign in,
    open the site she owns, and be a stranger to it: no account menu, no kept
    charts, no practice room. She could administer the room and not post in it.

    The fix is not to merge the two. It is to notice that whoever proved they
    are the operator has also, necessarily, proved they are that email's owner,
    and to hand them the reader session that follows from it.

    ⚠ **One password, by her decision.** The member account is given the
    operator's own password hash, so the address she already knows and the
    password she already types work at the ordinary sign-in form too — on her
    phone, in the app, anywhere the desk is not.

    The cost, stated because it is real: the member sign-in form becomes a
    second place her password can be tried. It is a strictly smaller prize —
    guessing it yields a reader session, never the desk, which needs the admin
    cookie and its own stamp — but it is another door and should be counted as
    one.

    The hash is COPIED, never re-derived, so changing the admin password
    propagates by itself at her next sign-in and nothing here ever holds the
    plaintext.
    """
    from shruti.core.sessions import SESSION_COOKIE, SESSION_DAYS, issue_session
    from shruti.core.operator import KEY_HASH, _get

    address = email.strip().lower()

    # The operator's stored hash, or the environment one a deployment still
    # runs on before it has been claimed. Same argon2 parameters either way, so
    # the reader's verifier reads it without needing to know where it came from.
    stored = (await _get(session, KEY_HASH)) or os.environ.get(
        "SHRUTI_ADMIN_PASSWORD_HASH", "").strip()

    user = (
        await session.execute(select(User).where(func.lower(User.email) == address))
    ).scalar_one_or_none()

    if user is None:
        user = User(
            email=address,
            display_name="",
            # She owns the mailbox the site sends FROM; asking her to click a
            # link to prove it would be a loop with one participant.
            email_verified_at=datetime.now(timezone.utc),
        )
        session.add(user)

    if stored and user.password_hash != stored:
        user.password_hash = stored

    await session.commit()
    await session.refresh(user)

    response.set_cookie(
        SESSION_COOKIE, issue_session(user.id, user.email),
        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=secure, path="/",
    )


@router.post("/logout")
async def logout(response: Response) -> dict:
    from shruti.core.sessions import SESSION_COOKIE

    response.delete_cookie("shruti_session", path="/")
    # ⚠ Both, because signing in gave her both. Leaving the reader cookie
    # behind would mean "sign out" left her signed in as herself on the site,
    # which is the opposite of what the word promises.
    response.delete_cookie(SESSION_COOKIE, path="/")
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

    stem = m.filename.rsplit(".", 1)[0]
    have = [v for v in (m.variants or "").split(",") if v]

    return {
        "id": m.id,
        "filename": m.filename,
        "url": public_url(m.filename, m.storage_backend),
        # Sorted best-first, which is the order <picture> needs: a browser
        # takes the FIRST source it understands, so avif must precede webp.
        "sources": [
            {"type": f"image/{v}", "url": public_url(f"{stem}.{v}", m.storage_backend)}
            for v in ("avif", "webp") if v in have
        ],
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



# What can usefully be re-encoded. SVG is already small and lossless, and a GIF
# would lose its animation — both are left exactly as uploaded.
RECODEABLE = {"image/png", "image/jpeg", "image/webp"}


async def _write_variants(filename: str, data: bytes, content_type: str) -> str:
    """
    Write AVIF and WebP beside the original, and say which ones landed.

    Not a nicety: the four project thumbnails on the landing page are PNGs, and
    Lighthouse put 121 KiB on that one page alone. The site's own hero art went
    from 226 KB to 14 KB on the same treatment.

    The ORIGINAL is always kept and always remains the `src`. These are extra
    sources a browser may prefer, never a replacement — a re-encode is lossy,
    and the file she uploaded is the one she chose.

    A failure here is logged and swallowed. Losing a smaller copy of an image
    is a slower page; losing the upload because the smaller copy failed is her
    work gone.
    """
    if content_type not in RECODEABLE:
        return ""

    from io import BytesIO

    from PIL import Image

    from shruti.core.storage import put as store_media

    # The variant is downscaled past this. The ORIGINAL is untouched — this
    # only bounds the alternative a browser may prefer, and 2400px is already
    # more than any layout on this site draws.
    #
    # It is a memory guard as much as a size one: encoders scale with pixel
    # count, and an unbounded upload can take a worker with it. A kill is not
    # an exception, so it cannot be caught — it can only be not reached.
    MAX_EDGE = 2400

    stem = filename.rsplit(".", 1)[0]
    written: list[str] = []
    for fmt, ext, mime, opts in (
        ("AVIF", ".avif", "image/avif", {"quality": 70}),
        ("WEBP", ".webp", "image/webp", {"quality": 88, "method": 6}),
    ):
        try:
            buf = BytesIO()
            with Image.open(BytesIO(data)) as im:
                if max(im.size) > MAX_EDGE:
                    im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
                if fmt == "AVIF" and im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA")
                im.save(buf, fmt, **opts)
            body = buf.getvalue()
            # Only if it actually helps. A small PNG can re-encode LARGER, and
            # shipping a bigger file as the preferred source is worse than
            # shipping none.
            if len(body) >= len(data):
                log.info("%s of %s was not smaller; skipped", fmt, filename)
                continue
            await store_media(f"{stem}{ext}", body, mime)
            written.append(ext.lstrip("."))
        except Exception as exc:                   # noqa: BLE001
            log.warning("could not write %s for %s: %s", fmt, filename, type(exc).__name__)

    return ",".join(written)


def _dimensions(data: bytes, content_type: str) -> tuple[int | None, int | None]:
    """
    How big the image is, for both kinds of image.

    Pillow reads rasters and cannot read SVG, which used to mean every vector
    upload stored `null` for both — and a null width is an `<img>` with nothing
    to reserve space with, so the page reflows when it arrives. That is a real
    layout shift, and it was showing up in Lighthouse as an unsized image.

    An SVG's size comes from its `viewBox` where it has one, because that is
    the ratio that survives whatever `width` says; `width`/`height` attributes
    are the fallback, and a percentage in either is correctly no answer at all.
    """
    if content_type == "image/svg+xml":
        head = data[:4096].decode("utf-8", "replace")
        box = re.search(
            r'viewBox\s*=\s*["\']\s*[-\d.eE]+[ ,]+[-\d.eE]+[ ,]+'
            r'([\d.eE]+)[ ,]+([\d.eE]+)', head)
        if box:
            try:
                return round(float(box.group(1))), round(float(box.group(2)))
            except ValueError:
                return None, None
        got: list[int | None] = []
        for attr in ("width", "height"):
            m = re.search(rf'<svg[^>]*?\b{attr}\s*=\s*["\']([\d.]+)(px)?["\']', head)
            got.append(round(float(m.group(1))) if m else None)
        return got[0], got[1]

    try:
        from io import BytesIO

        from PIL import Image

        with Image.open(BytesIO(data)) as im:
            return im.size
    except Exception:                              # noqa: BLE001
        return None, None


@router.post("/sounds", status_code=201)
async def upload_sound(
    file: UploadFile = File(...),
    title: str = Form(""),
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Upload one alert sound.

    The same store as the images, on purpose — one uploader, one hash-named
    file, one place things live. What differs is the allow-list and the
    ceiling: WAV or OGG at 512 KB, because these are held in memory on her
    streaming machine for the whole session rather than fetched when needed.

    Uploading does not assign it to anything. Choosing which noise belongs to a
    gift is a separate decision from having the file, and merging the two would
    mean an upload could start playing on her stream before she had heard it.
    """
    if file.content_type not in ALLOWED_AUDIO:
        raise HTTPException(
            415, f"unsupported type {file.content_type!r}; "
                 f"allowed: WAV or OGG"
        )

    data = await file.read()
    if len(data) > MAX_SOUND_BYTES:
        raise HTTPException(413, "the file is larger than 512 KB")
    if not data:
        raise HTTPException(422, "the file is empty")

    digest = hashlib.sha256(data).hexdigest()[:32]
    filename = f"{digest}{ALLOWED_AUDIO[file.content_type]}"

    existing = (await session.execute(
        select(Media).where(Media.filename == filename)
    )).scalars().first()
    if existing:
        return _media_payload(existing) | {"deduped": True}

    from shruti.core.storage import put as store_media

    stored = await store_media(filename, data, file.content_type)
    row = Media(filename=filename, mime_type=file.content_type,
                size_bytes=len(data), storage_backend=stored.backend,
                title=title.strip(), tags="alert-sound")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _media_payload(row)


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

    width, height = _dimensions(data, file.content_type)
    variants = await _write_variants(filename, data, file.content_type)

    # Storage decides where it goes: R2 when configured, disk otherwise, and
    # disk again if R2 is unreachable — an upload should not be lost because a
    # bucket is having a bad day.
    from shruti.core.storage import put as store_media

    stored = await store_media(filename, data, file.content_type)

    row = Media(filename=filename, mime_type=file.content_type,
                width=width, height=height, size_bytes=len(data),
                storage_backend=stored.backend, variants=variants,
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


# ── every prose field on the site, in one list ──────────────────────────────
#
# ⚠ MUST STAY ABOVE the generic /{kind} routes. FastAPI matches in definition
# order and /{kind} will happily answer for "editables". The note further down
# says this has bitten twice already.
#
# Why this exists: the page editor could reach copy strings and page blocks and
# nothing else, so a tool's description, its FAQ, a tier's perks and a sponsor's
# blurb were words on the site that nobody could change — her words, "I should
# be able to edit everything from the editor, not just some things."
#
# The rule for what belongs here: **prose a reader reads.** Not slugs (they are
# addresses, and changing one breaks every link to it), not prices, not Stripe
# ids, not colours, not enums that decide layout. Those have their own screens
# where the consequences are visible. Everything a person READS is here.

# source → (model, field naming the row, [(field, label, is_long)])
PROSE: dict[str, tuple[type[SQLModel], str, list[tuple[str, str, bool]]]] = {
    "tools": (Tool, "name", [
        ("name", "Name", False),
        ("native", "Name in its own script", False),
        ("glyph", "Glyph", False),
        ("summary", "Summary", False),
        ("landing_blurb", "Blurb on the tools page", True),
        ("body_md", "Body", True),
        ("reckoned", "How it is reckoned", True),
        ("faq_md", "Questions and answers", True),
    ]),
    "tiers": (Tier, "name", [
        ("name", "Name", False),
        ("tagline", "Tagline", False),
        ("perks", "Perks", True),
        ("cta", "Button", False),
        ("badge", "Badge", False),
    ]),
    "products": (Product, "name", [
        ("name", "Name", False),
        ("tagline", "Tagline", False),
        ("body_md", "Description", True),
        ("lead_time", "Lead time", False),
    ]),
    "questions": (Question, "body", [
        ("body", "The question", True),
        ("answered_md", "Your answer", True),
    ]),
    "sponsors": (Sponsor, "name", [
        ("name", "Name", False),
        ("tagline", "Tagline", False),
        ("body_md", "Body", True),
        ("cta_label", "Button", False),
    ]),
    "projects": (Project, "name", [
        ("name", "Name", False),
        ("tagline", "Tagline", False),
        ("body_md", "Body", True),
        ("role", "Your part in it", False),
        ("stack", "Built with", False),
        ("licence", "Licence", False),
        ("contributors", "Contributors", False),
    ]),
    "courses": (Course, "title", [
        ("title", "Title", False),
        ("tagline", "Tagline", False),
        ("body_md", "Description", True),
    ]),
    "modules": (Module, "title", [("title", "Title", False)]),
    "lessons": (Lesson, "title", [
        ("title", "Title", False),
        ("body_md", "Body", True),
    ]),
    "links": (SocialLink, "label", [("label", "Label", False)]),
    "profile-fields": (ProfileField, "label", [
        ("label", "Label", False),
        ("value", "Value", False),
    ]),
    "credits": (Credit, "name", [
        ("role", "Role", False),
        ("name", "Name", False),
    ]),
    "schedule": (ScheduleEntry, "title", [
        ("title", "Title", False),
        ("notes_md", "Notes", True),
    ]),
    "fan-art": (FanArt, "title", [
        ("title", "Title", False),
        ("artist", "Artist", False),
    ]),
    "outfits": (Outfit, "name", [
        ("name", "Name", False),
        ("note", "Note", True),
        ("artist", "Artist", False),
    ]),
    "card-designs": (CardDesign, "name", [
        ("name", "Name", False),
        ("blurb", "Blurb", True),
    ]),
    "official": (OfficialPlace, "label", [
        ("label", "Label", False),
        ("note", "Note", True),
    ]),
    "polls": (Poll, "question", [
        ("question", "Question", False),
        ("note", "Note", True),
    ]),
    "poll-options": (PollOption, "label", [("label", "Answer", False)]),
}

# The sources whose rows also carry a picture. Ten tables have a media_id and
# until now exactly one of them — sections — could be pointed at a different
# image without a database client.
WITH_PICTURES = {
    "tools", "sponsors", "products", "projects", "outfits", "fan-art",
    "courses", "card-designs",
}


@router.get("/editables")
async def list_editables(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """
    Every editable prose field on the site, flat.

    The page editor matches these against the text the page actually renders
    and throws away the ones it cannot find, exactly as it already does for
    component strings — which page shows which tool is a fact about the
    rendered page, not something this query could know.

    Empty fields are included. A blurb that has never been written is precisely
    the one she is looking for a box to type into.
    """
    out: list[dict] = []
    for source, (model, names, fields) in PROSE.items():
        rows = (await session.execute(
            select(model).order_by(_order(model))
        )).scalars().all()
        for row in rows:
            title = str(getattr(row, names, "") or "").strip()
            for field, label, long in fields:
                out.append({
                    "source": source,
                    "id": row.id,
                    "field": field,
                    "label": label,
                    "long": long,
                    "value": getattr(row, field, "") or "",
                    "row": (title[:60] or f"#{row.id}"),
                })
            if source in WITH_PICTURES and hasattr(row, "media_id"):
                out.append({
                    "source": source,
                    "id": row.id,
                    "field": "media_id",
                    "label": "Picture",
                    "long": False,
                    "picture": True,
                    # The id, not a URL: the editor already holds the whole
                    # media list for its picker and can look the file up.
                    "value": row.media_id,
                    "row": (title[:60] or f"#{row.id}"),
                })
    return out


class ProseIn(BaseModel):
    field: str
    # A picture is an id or nothing; prose is a string. One route, because the
    # panel should not make her care which kind of thing she is changing.
    value: str | int | None = None


@router.patch("/editables/{source}/{item_id}")
async def set_editable(
    source: str,
    item_id: int,
    body: ProseIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Change one prose field.

    ⚠ The whitelist is the point, not a formality. This route is reachable from
    a page that lists every row on the site, so without it a stray field name
    would let the editor write a slug, a price or a Stripe id — none of which
    are prose, and two of which take money.
    """
    if source not in PROSE:
        raise HTTPException(404, f"nothing editable called {source!r}")
    model, _names, fields = PROSE[source]
    picture = body.field == "media_id" and source in WITH_PICTURES
    if not picture and body.field not in {f for f, _l, _long in fields}:
        raise HTTPException(422, f"{source} has no editable prose called {body.field!r}")

    row = await session.get(model, item_id)
    if row is None:
        raise HTTPException(404, "no such item")
    if picture:
        # "" from an empty form field means no picture, not a picture called "".
        setattr(row, "media_id", int(body.value) if body.value not in (None, "") else None)
    else:
        setattr(row, body.field, str(body.value or ""))
    if hasattr(row, "updated_at"):
        row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"ok": True}




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
    secure = get_settings().is_production
    response.set_cookie(
        "shruti_session", token, httponly=True, samesite="lax",
        secure=secure, max_age=12 * 3600, path="/",
    )
    await _also_a_reader(session, response, body.email, secure)
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
    secure = get_settings().is_production
    response.set_cookie(
        "shruti_session", token, httponly=True, samesite="lax",
        secure=secure, max_age=12 * 3600, path="/",
    )
    await _also_a_reader(session, response, email, secure)
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
    # ⚠ Shruti's Guides: a game's art. The guard caught this missing the day
    # the model was written, which is what the guard is for.
    (Game, "guide game"),
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


@router.get("/media/orphans")
async def media_orphans(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Files in the bucket that no row knows about, and rows whose file is gone.

    Deleting through the admin has always removed the object too, so nothing
    here should ever find anything — which is exactly why it is worth being
    able to look. The ways an orphan appears are all outside that route: an
    upload that stored the file and then failed to commit, a database restored
    from before an upload, or somebody clearing rows in SQL.

    The reverse direction is reported in the same breath because it is the same
    question asked the other way round, and it is the more visible failure: a
    row whose file has gone renders as a broken image on a live page.

    **"Orphan" means orphaned according to THIS database.** Development and
    production point at the same bucket, so every production image looks like
    an orphan from a laptop — which is why the answer carries the environment
    and why sweeping is refused anywhere but production. Found the hard way:
    this check, run locally, called four live project thumbnails orphans.
    """
    from shruti.core.storage import list_objects, r2_configured

    env = get_settings().env
    if not r2_configured():
        return {"configured": False, "env": env, "canSweep": False,
                "orphans": [], "missing": [], "checked": 0}

    known = {
        m.filename: m
        for m in (await session.execute(
            select(Media).where(Media.storage_backend == "r2")
        )).scalars().all()
    }
    objects = await list_objects()
    in_bucket = {name for name, _ in objects}

    return {
        "configured": True,
        "env": env,
        # Only the environment that owns the bucket may act on this list.
        "canSweep": env == "production",
        "checked": len(objects),
        # In the bucket, in no row.
        "orphans": [
            {"filename": name, "sizeBytes": size}
            for name, size in sorted(objects) if name not in known
        ],
        # In a row, not in the bucket.
        "missing": [
            {"id": m.id, "filename": f, "title": m.title}
            for f, m in sorted(known.items()) if f not in in_bucket
        ],
    }


class SweepIn(BaseModel):
    filenames: list[str] = Field(default_factory=list)


@router.post("/media/orphans/sweep")
async def sweep_orphans(
    body: SweepIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Delete named objects from the bucket.

    Named explicitly rather than "delete everything the last check found":
    a sweep that re-derives its own list would race an upload happening in
    another tab and delete a file whose row had not been committed yet. She
    sees a list, and what she confirms is what goes.

    Every name is re-checked against the database first. A file that has
    acquired a row since the listing is skipped and said so, rather than
    deleted because a page was stale.

    **Refused outside production.** Development shares the production bucket,
    so a laptop's database calls every live image an orphan — running this
    there would delete the site's pictures from a machine that had never
    displayed them. The listing is safe to read anywhere; only the environment
    that owns the bucket may act on it.
    """
    if get_settings().env != "production":
        raise HTTPException(
            409,
            "sweeping is only allowed in production. This environment shares "
            "the bucket, so its idea of an orphan includes every file that "
            "belongs to the live site.",
        )

    from shruti.core.storage import delete as delete_stored

    deleted: list[str] = []
    skipped: list[str] = []
    for name in body.filenames[:500]:
        claimed = (await session.execute(
            select(Media).where(Media.filename == name)
        )).scalars().first()
        if claimed is not None:
            skipped.append(name)
            continue
        await delete_stored(name, "r2")
        deleted.append(name)

    if deleted:
        log.info("swept %d orphaned object(s) from the bucket", len(deleted))
    return {"deleted": deleted, "skipped": skipped}


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

    # And every format written beside it. Missing this was caught by testing
    # the upload path end to end: deleting a picture left its AVIF and WebP
    # in the bucket, reachable by nothing and paid for forever — a new source
    # of exactly the orphans the sweep exists to clean up.
    stem = row.filename.rsplit(".", 1)[0]
    for variant in (v for v in (row.variants or "").split(",") if v):
        await delete_stored(f"{stem}.{variant}", row.storage_backend)
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

# ── editable strings ────────────────────────────────────────────────────────
#
# ABOVE the generic /{kind} collection routes on purpose. Those match any
# single path segment, so registered after them "copy" is read as a collection
# name and answered with "unknown collection" — which is what happened, and
# looked like the new routes simply not existing.


class CopySeedItem(BaseModel):
    key: str
    label: str = ""
    default: str = ""
    position: int = 0
    multiline: bool = False


class CopySeedIn(BaseModel):
    page: str
    items: list[CopySeedItem] = Field(default_factory=list)


@router.post("/copy/seed")
async def seed_copy(
    body: CopySeedIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Register the strings a page uses, so the admin can list them.

    **This never touches a value she has written.** It records what the
    template offers — the label, the default, where it falls on the page — and
    for a row that already exists it updates only those. The seeder reads the
    templates; the templates are never told what to say.

    Run after a deploy that adds or moves a string. Safe to run repeatedly:
    the same page seeded twice is the same rows.
    """
    from shruti.models import Copy

    known = {
        r.key: r
        for r in (await session.execute(
            select(Copy).where(Copy.page == body.page)
        )).scalars().all()
    }

    added = 0
    for item in body.items:
        row = known.get(item.key)
        if row is None:
            session.add(Copy(
                page=body.page, key=item.key, label=item.label,
                # Seeded WITH the default as its value, so the admin shows the
                # words that are on the site rather than an empty box she has
                # to fill before the page reads right.
                value=item.default, default_value=item.default,
                position=item.position, multiline=item.multiline,
            ))
            added += 1
            continue
        # An UNTOUCHED row tracks the template. If she has never edited this
        # string, its value is still exactly the default it was seeded with —
        # so when the default changes, the value follows.
        #
        # Without this, changing a line in a template silently does nothing:
        # the row seeded with the old words wins, the page shows the old words,
        # and nothing anywhere says why. Found exactly that way — a rewritten
        # sentence on /press rendered as the fragment it used to be.
        #
        # The moment she edits it the two diverge and this stops touching it,
        # which is the whole point: her words are hers.
        if row.value == row.default_value and row.value != item.default:
            row.value = item.default

        row.label = item.label or row.label
        row.default_value = item.default
        row.position = item.position
        row.multiline = item.multiline

    await session.commit()
    return {"page": body.page, "seen": len(body.items), "added": added}


@router.get("/copy")
async def list_copy(
    page: str = "",
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """Every string, or one page's, in the order it appears on the page."""
    from shruti.models import Copy

    q = select(Copy).order_by(Copy.page, Copy.position, Copy.key)
    if page:
        q = q.where(Copy.page == page)
    rows = (await session.execute(q)).scalars().all()
    return [{
        "id": r.id, "page": r.page, "key": r.key, "label": r.label,
        "value": r.value, "default": r.default_value,
        "multiline": r.multiline, "position": r.position,
        # So the admin can show what has been changed and offer it back.
        "changed": r.value != r.default_value,
    } for r in rows]


class CopyIn(BaseModel):
    value: str = ""


@router.put("/copy/{copy_id}")
async def set_copy(
    copy_id: int,
    body: CopyIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    from shruti.models import Copy

    row = await session.get(Copy, copy_id)
    if row is None:
        raise HTTPException(404, "no such string")
    row.value = body.value
    await session.commit()
    return {"id": row.id, "value": row.value,
            "changed": row.value != row.default_value}


@router.post("/copy/{copy_id}/revert")
async def revert_copy(
    copy_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """Put back the words the page was written with."""
    from shruti.models import Copy

    row = await session.get(Copy, copy_id)
    if row is None:
        raise HTTPException(404, "no such string")
    row.value = row.default_value
    await session.commit()
    return {"id": row.id, "value": row.value, "changed": False}


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
