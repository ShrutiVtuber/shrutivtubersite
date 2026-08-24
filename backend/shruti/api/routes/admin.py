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
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from shruti.api.deps import require_admin
from shruti.core.auth import authenticate, issue_token
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models import (FanArt, 
    ContactMessage, Credit, Media, ProfileField, Project, Question,
    ScheduleEntry, Section, SocialLink, Tool,
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
async def login(payload: LoginIn, response: Response) -> dict:
    if not authenticate(payload.email, payload.password):
        # One message for both failures. Distinguishing "no such user" from
        # "wrong password" tells an attacker which half to work on.
        raise HTTPException(401, "email or password is wrong")

    token = issue_token(payload.email)
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

@router.post("/media", status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Upload one image.

    Named by content hash, so the same file uploaded twice is stored once and
    the URL is stable. The declared content type is checked against an
    allow-list rather than trusted — a browser will send whatever it is told.
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

    root = Path(s.media_root)
    root.mkdir(parents=True, exist_ok=True)
    (root / filename).write_bytes(data)

    existing = (await session.execute(
        select(Media).where(Media.filename == filename)
    )).scalars().first()
    if existing:
        return existing.model_dump()

    width = height = None
    try:
        from io import BytesIO

        from PIL import Image

        with Image.open(BytesIO(data)) as im:
            width, height = im.size
    except Exception:                              # noqa: BLE001 — SVG has no raster size
        pass

    row = Media(filename=filename, mime_type=file.content_type,
                width=width, height=height, size_bytes=len(data))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row.model_dump()


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
        row = model(**payload)
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
    for key, value in payload.items():
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
