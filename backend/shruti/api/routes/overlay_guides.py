# SPDX-License-Identifier: AGPL-3.0-only
"""
Guide overlays: a browser source that shows one run — a person's place on a
path — and keeps up while they stream.

Four elements, each its own page: guide-now (the current step), guide-sigil
(phase progress), guide-path (a six-item window of the path), guide-routine
(one checklist). The token is the whole authentication, as for every other
overlay: anybody with the URL sees it, nobody with it can change the run.

⚠ The state colours and shapes are the same in every theme; a theme changes
palette, type and ornament only. That is enforced in the stylesheet, not
here — this route hands over the run as the engine computes it and says
which theme the token wears.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.deps import require_admin
from shruti.api.routes.practice import _reader
from shruti.models import OverlayToken
from shruti.models.guides import Game, Guide, GuideRun, GuideVersion
from shrutisguides import progress

router = APIRouter(prefix="/api/overlay", tags=["overlay"])
runs_router = APIRouter(prefix="/api/runs", tags=["runs"])

GUIDE_KINDS, THEMES, MOTIONS = progress.GUIDE_KINDS, progress.THEMES, progress.MOTIONS


def _stored(row: GuideRun) -> dict:
    return {
        "name": row.name, "variant": row.variant, "checkin": row.checkin or {}, "steps": row.steps or {},
        "routines": row.routines or {}, "tracks": row.tracks or {}, "later": row.later or [],
        "note": row.note, "link_overrides": row.link_overrides or {},
    }


@router.get("/guide")
async def guide(t: str, session: AsyncSession = Depends(get_session)) -> dict:
    """
    The run as this token's element draws it. Polled; `version` changes when
    the run changes, so a page can compare and play the Done moment once.

    ⚠ A token whose run is gone answers with an empty frame, not an error —
    an overlay never blanks and never says "connecting".
    """
    token = (await session.execute(select(OverlayToken).where(OverlayToken.token == t))).scalar_one_or_none()
    if token is None or token.kind not in GUIDE_KINDS:
        raise HTTPException(404, "no such overlay")
    token.last_seen = datetime.now(timezone.utc)
    await session.commit()
    base = {"kind": token.kind, "theme": token.theme if token.theme in THEMES else "almanac",
            "motion": token.motion, "run": None, "element": None, "version": ""}
    run = await session.get(GuideRun, token.run_id) if token.run_id else None
    if run is None:
        return base
    g = await session.get(Guide, run.guide_id)
    v = await session.get(GuideVersion, g.published_version_id) if g and g.published_version_id else None
    if g is None or v is None:
        return base
    game = await session.get(Game, g.game_id)
    base["run"] = {"name": run.name, "guide": g.title, "game": game.name if game else ""}
    if token.kind == "guide-layout":
        base["elements"] = progress.layout_elements(progress.clean_layout(token.layout), _stored(run), v.body)
    else:
        base["element"] = progress.element(token.kind, _stored(run), v.body, token.routine_id)
    base["version"] = run.updated_at.isoformat() if run.updated_at else ""
    return base


# ── the person's own tokens ──────────────────────────────────────────────────

class TokenIn(BaseModel):
    kind: str
    theme: str = "almanac"
    motion: str = "reduced"
    routine_id: str = ""
    label: str = ""
    layout: list = []


async def _mine(session: AsyncSession, request: Request, run_id: int) -> GuideRun:
    user = await _reader(request, session)
    run = await session.get(GuideRun, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(404, "no such run")
    return run


@runs_router.get("/{run_id}/overlays")
async def list_tokens(run_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """This run's overlays, WITHOUT their tokens — a token is readable once, when minted."""
    run = await _mine(session, request, run_id)
    rows = (await session.execute(select(OverlayToken).where(OverlayToken.run_id == run.id).order_by(OverlayToken.id))).scalars().all()
    return [{"id": o.id, "kind": o.kind, "label": o.label, "theme": o.theme, "motion": o.motion,
             "routineId": o.routine_id, "layout": o.layout or [],
             "lastSeen": o.last_seen.isoformat() if o.last_seen else None} for o in rows]


@runs_router.post("/{run_id}/overlays", status_code=201)
async def mint_token(run_id: int, body: TokenIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Mints one overlay for this run and returns its token **once**. The token
    is the secret: anyone with the URL sees the overlay; nobody with it can
    change the run.
    """
    run = await _mine(session, request, run_id)
    if body.kind not in GUIDE_KINDS:
        raise HTTPException(422, "kind is guide-now, guide-sigil, guide-path, guide-routine or guide-layout")
    token = secrets.token_urlsafe(24)
    row = OverlayToken(token=token, kind=body.kind, label=body.label.strip()[:80], run_id=run.id,
                       routine_id=body.routine_id.strip()[:80],
                       theme=body.theme if body.theme in THEMES else "almanac",
                       motion=body.motion if body.motion in MOTIONS else "reduced",
                       layout=progress.clean_layout(body.layout))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "token": token, "kind": row.kind, "theme": row.theme, "motion": row.motion}


class LayoutIn(BaseModel):
    layout: list
    theme: str | None = None
    motion: str | None = None
    label: str | None = None


@runs_router.put("/{run_id}/overlays/{token_id}/layout")
async def set_layout(run_id: int, token_id: int, body: LayoutIn, request: Request,
                     session: AsyncSession = Depends(get_session)) -> dict:
    """Save a layout — the designer's one write. Positions are clamped to the canvas."""
    run = await _mine(session, request, run_id)
    row = await session.get(OverlayToken, token_id)
    if row is None or row.run_id != run.id:
        raise HTTPException(404, "no such overlay")
    row.layout = progress.clean_layout(body.layout)
    if body.theme in THEMES:
        row.theme = body.theme
    if body.motion in MOTIONS:
        row.motion = body.motion
    if body.label is not None:
        row.label = body.label.strip()[:80]
    await session.commit()
    return {"ok": True, "layout": row.layout}


class RebindIn(BaseModel):
    run_id: int


@runs_router.put("/{run_id}/overlays/{token_id}")
async def rebind_token(run_id: int, token_id: int, body: RebindIn, request: Request,
                       session: AsyncSession = Depends(get_session)) -> dict:
    """"Switch run": point an existing overlay at another of the person's runs."""
    run = await _mine(session, request, run_id)
    target = await _mine(session, request, body.run_id)
    row = await session.get(OverlayToken, token_id)
    if row is None or row.run_id != run.id:
        raise HTTPException(404, "no such overlay")
    row.run_id = target.id
    await session.commit()
    return {"ok": True, "runId": target.id}


@runs_router.delete("/{run_id}/overlays/{token_id}", status_code=204)
async def revoke_token(run_id: int, token_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """A delete, not a flag. A revoked token that still works is not revoked."""
    run = await _mine(session, request, run_id)
    row = await session.get(OverlayToken, token_id)
    if row is not None and row.run_id == run.id:
        await session.delete(row)
        await session.commit()


@router.get("/admin/guide-preview/{token_id}", dependencies=[Depends(require_admin)])
async def admin_preview(token_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    """
    The designer's live preview: what the overlay at this id draws right
    now, WITHOUT its token. Same shape as /guide, so the designer's canvas is
    the overlay, not a lookalike.
    """
    token = await session.get(OverlayToken, token_id)
    if token is None or token.kind not in GUIDE_KINDS:
        raise HTTPException(404, "no such overlay")
    base = {"id": token.id, "kind": token.kind, "theme": token.theme, "motion": token.motion, "label": token.label,
            "layout": progress.clean_layout(token.layout), "run": None, "elements": [], "version": ""}
    run = await session.get(GuideRun, token.run_id) if token.run_id else None
    if run is None:
        return base
    g = await session.get(Guide, run.guide_id)
    v = await session.get(GuideVersion, g.published_version_id) if g and g.published_version_id else None
    if g is None or v is None:
        return base
    base["run"] = {"id": run.id, "name": run.name, "guide": g.title}
    base["elements"] = progress.layout_elements(base["layout"], _stored(run), v.body)
    base["version"] = run.updated_at.isoformat() if run.updated_at else ""
    return base
