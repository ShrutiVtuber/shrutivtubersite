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
from shruti.api.routes.practice import _reader
from shruti.models import OverlayToken
from shruti.models.guides import Game, Guide, GuideRun, GuideVersion
from shrutisguides import engine

router = APIRouter(prefix="/api/overlay", tags=["overlay"])
runs_router = APIRouter(prefix="/api/runs", tags=["runs"])

GUIDE_KINDS = ("guide-now", "guide-sigil", "guide-path", "guide-routine")
THEMES = ("almanac", "grimoire", "plain")
MOTIONS = ("full", "reduced", "still")


def _run_of(row: GuideRun) -> engine.Run:
    return engine.Run(
        variant=row.variant, checkin=dict(row.checkin or {}),
        states={sid: v.get("state", "") for sid, v in (row.steps or {}).items() if isinstance(v, dict)},
        routines={rid: list(v.get("ticked", [])) for rid, v in (row.routines or {}).items() if isinstance(v, dict)},
        tracks=dict(row.tracks or {}),
    )


def _element(kind: str, token: OverlayToken, run: GuideRun, doc: dict, progress: engine.Progress) -> dict:
    """What one element draws — only that, so a source never carries the whole guide."""
    steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
    phases = {p["id"]: p for p in doc.get("phases", []) if isinstance(p, dict)}
    path = [s for ph in engine.phases_in_order(doc) if not ph.get("track") for s in engine.steps_in(doc, ph["id"])]
    cur = steps.get(progress.current) if progress.current else None
    phase = phases.get(cur["phase"]) if cur else None
    here = engine.steps_in(doc, phase["id"]) if phase else []
    counted = [s for s in here if s.get("kind") != "optional"]
    done_here = sum(1 for s in counted if progress.states.get(s["id"]) == "done")
    if kind == "guide-now":
        return {
            "phase": phase.get("name", "") if phase else "",
            "id": cur["id"] if cur else None,
            "title": cur.get("title", "") if cur else "",
            "line": (cur.get("oneliner") or cur.get("do", "").split("\n")[0]) if cur else "",
            "count": f"{done_here} of {len(counted)}" if phase else "",
            "finished": cur is None and bool(path) and all(progress.states.get(s["id"]) in ("done", "skipped") for s in path),
        }
    if kind == "guide-sigil":
        main = [ph for ph in engine.phases_in_order(doc) if not ph.get("track")]
        idx = main.index(phase) + 1 if phase in main else 0
        return {"parts": engine.sigil_parts(doc, progress, _run_of(run)),
                "label": f"{idx}/{len(main)}" if idx else "",
                "count": f"{done_here} of {len(counted)}" if phase else ""}
    if kind == "guide-path":
        i = next((k for k, s in enumerate(path) if s["id"] == progress.current), None)
        if i is None:
            window = path[-6:]
        else:
            window = path[max(0, i - 2): i + 4]
        return {"strip": [{"id": s["id"], "title": s.get("title", ""), "state": progress.states.get(s["id"], "locked")} for s in window]}
    if kind == "guide-routine":
        routine = next((r for r in doc.get("routines", []) if isinstance(r, dict) and r["id"] == token.routine_id), None)
        if routine is None:
            routine = next((r for r in doc.get("routines", []) if isinstance(r, dict)), None)
        if routine is None:
            return {"routine": None}
        ticked = set((run.routines or {}).get(routine["id"], {}).get("ticked", []))
        return {"routine": {"name": routine.get("name", ""), "open": progress.routines.get(routine["id"], False),
                            "items": [{"id": i["id"], "text": i["text"], "done": i["id"] in ticked} for i in routine.get("items", [])],
                            "count": f"{len(ticked)} / {len(routine.get('items', []))}"}}
    return {}


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
    progress = engine.compute(v.body, _run_of(run))
    base["run"] = {"name": run.name, "guide": g.title, "game": game.name if game else ""}
    base["element"] = _element(token.kind, token, run, v.body, progress)
    base["version"] = run.updated_at.isoformat() if run.updated_at else ""
    return base


# ── the person's own tokens ──────────────────────────────────────────────────

class TokenIn(BaseModel):
    kind: str
    theme: str = "almanac"
    motion: str = "reduced"
    routine_id: str = ""
    label: str = ""


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
             "routineId": o.routine_id, "lastSeen": o.last_seen.isoformat() if o.last_seen else None} for o in rows]


@runs_router.post("/{run_id}/overlays", status_code=201)
async def mint_token(run_id: int, body: TokenIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Mints one overlay for this run and returns its token **once**. The token
    is the secret: anyone with the URL sees the overlay; nobody with it can
    change the run.
    """
    run = await _mine(session, request, run_id)
    if body.kind not in GUIDE_KINDS:
        raise HTTPException(422, "kind is guide-now, guide-sigil, guide-path or guide-routine")
    token = secrets.token_urlsafe(24)
    row = OverlayToken(token=token, kind=body.kind, label=body.label.strip()[:80], run_id=run.id,
                       routine_id=body.routine_id.strip()[:80],
                       theme=body.theme if body.theme in THEMES else "almanac",
                       motion=body.motion if body.motion in MOTIONS else "reduced")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "token": token, "kind": row.kind, "theme": row.theme, "motion": row.motion}


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
