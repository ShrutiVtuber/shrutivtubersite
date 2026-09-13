# SPDX-License-Identifier: AGPL-3.0-only
"""
Runs: one person's progress through one guide, kept on the site.

Only what a person SET is stored — done, skipped, later, ticks, the
check-in, a note. Locked, available and current are computed on every read
by the shared engine (`shrutisguides.engine`), the same code the overlays
and the tracker run, so nothing here can disagree with the guide.

⚠ **Nothing is applied silently.** A check-in returns proposals; `accept`
marks what the person ticked. A run starts with a bulk-skip PROPOSAL, not a
skip. That is the spec's A.4.12 and the design's principle 9.

⚠ **Nothing measures absence.** No streaks, no day counts. `last_seen_at`
exists for one thing: the re-entry block after six hours, which names a
weekday, never a count.

⚠ **A new version of the guide never deletes progress.** States are keyed
by step id; the engine reports ids the version no longer has as orphaned,
and the path shows them greyed.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.routes.practice import _reader
from shruti.models import User
from shruti.models.guides import Game, Guide, GuideRun, GuideVersion
from shrutisguides import engine

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/runs", tags=["runs"])

STATES = ("done", "skipped", "later", "open")
REENTRY_AFTER = timedelta(hours=6)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


async def _run_of(session: AsyncSession, user: User, run_id: int) -> GuideRun:
    """The person's own run, or 404 — never 403, a stranger learns nothing."""
    run = await session.get(GuideRun, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(404, "no such run")
    return run


async def _doc_for(session: AsyncSession, guide: Guide) -> tuple[GuideVersion, dict]:
    """The published version a run follows. A guide with none cannot be tracked."""
    if not guide.published_version_id:
        raise HTTPException(409, "this guide is not published")
    v = await session.get(GuideVersion, guide.published_version_id)
    if v is None:
        raise HTTPException(409, "this guide is not published")
    return v, v.body


def _engine_run(row: GuideRun) -> engine.Run:
    return engine.Run(
        variant=row.variant,
        checkin=dict(row.checkin or {}),
        states={sid: v.get("state", "") for sid, v in (row.steps or {}).items() if isinstance(v, dict)},
        routines={rid: list(v.get("ticked", [])) for rid, v in (row.routines or {}).items() if isinstance(v, dict)},
        tracks=dict(row.tracks or {}),
    )


def _zone(user: User) -> ZoneInfo:
    try:
        return ZoneInfo(getattr(user, "timezone", "") or "UTC")
    except Exception:                                  # noqa: BLE001
        return ZoneInfo("UTC")


def _reset_due(kind: str, reset_at: datetime | None, last_seen: datetime | None, now: datetime, zone: ZoneInfo) -> bool:
    """
    Whether a routine's ticks should be cleared: session (six hours since
    the run was last seen), daily (04:00 local), weekly (Tuesday 04:00 local).
    A routine never ticked has nothing to reset.
    """
    if kind == "manual":
        return False
    if kind == "session":
        return last_seen is not None and now - last_seen >= REENTRY_AFTER
    local = now.astimezone(zone)
    boundary = local.replace(hour=4, minute=0, second=0, microsecond=0)
    if local < boundary:
        boundary -= timedelta(days=1)
    if kind == "weekly":
        # Back to the most recent Tuesday 04:00.
        boundary -= timedelta(days=(boundary.weekday() - 1) % 7)
    return reset_at is None or reset_at < boundary.astimezone(timezone.utc)


def _apply_resets(row: GuideRun, doc: dict, user: User, now: datetime) -> bool:
    """Clear ticks whose reset has come. Returns whether anything changed."""
    changed = False
    zone = _zone(user)
    routines = dict(row.routines or {})
    for r in doc.get("routines", []):
        if not isinstance(r, dict):
            continue
        state = routines.get(r["id"])
        if not state or not state.get("ticked"):
            continue
        reset_at = datetime.fromisoformat(state["reset_at"]) if state.get("reset_at") else None
        if _reset_due(r.get("resets", "manual"), reset_at, row.last_seen_at, now, zone):
            routines[r["id"]] = {"ticked": [], "reset_at": now.isoformat()}
            changed = True
    if changed:
        row.routines = routines
    return changed


def _weekday_evening(dt: datetime, zone: ZoneInfo) -> str:
    """"Tuesday evening", never "3 days ago": a weekday is a place, a count is a measurement of absence."""
    local = dt.astimezone(zone)
    hour = local.hour
    part = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"
    return f"{local.strftime('%A')} {part}"


def _view(row: GuideRun, guide: Guide, game: Game, version: GuideVersion, doc: dict, user: User,
          now: datetime) -> dict:
    run = _engine_run(row)
    progress = engine.compute(doc, run)
    steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
    current = steps.get(progress.current) if progress.current else None
    reentry = None
    if row.last_seen_at and now - row.last_seen_at >= REENTRY_AFTER and row.last_done:
        last = steps.get(row.last_done)
        reentry = {
            "when": _weekday_evening(row.last_done_at or row.last_seen_at, _zone(user)),
            "lastDone": {"id": row.last_done, "title": last.get("title", "") if last else row.last_done},
            "note": row.note,
            "next": {"id": current["id"], "title": current.get("title", "")} if current else None,
        }
    return {
        "id": row.id, "name": row.name, "variant": row.variant,
        "guide": {"id": guide.id, "slug": guide.slug, "title": guide.title,
                  "game": {"slug": game.slug, "name": game.name}},
        "versionId": row.version_id, "publishedVersionId": version.id,
        "stale": bool(row.version_id) and row.version_id != version.id,
        "checkin": row.checkin or {},
        "steps": row.steps or {},
        "routines": row.routines or {},
        "tracks": row.tracks or {},
        "later": row.later or [],
        "note": row.note,
        "linkOverrides": row.link_overrides or {},
        "lastDone": {"id": row.last_done, "at": _iso(row.last_done_at)} if row.last_done else None,
        "lastSeenAt": _iso(row.last_seen_at),
        "reentry": reentry,
        # Which check-in fields the sheet shows now: a field with show_when
        # hidden until it holds — stated in one line, never shown disabled.
        "checkinShown": {
            f["id"]: engine.applies(f, run) and engine.holds(f.get("show_when"), doc, run)
            for f in doc.get("checkin", []) if isinstance(f, dict)
        },
        "progress": {
            "states": progress.states,
            "current": progress.current,
            "trackCurrent": progress.track_current,
            "codex": progress.codex,
            "routines": progress.routines,
            "orphaned": progress.orphaned,
            "proposals": progress.proposals,
            "phaseCounts": {k: list(v) for k, v in progress.phase_counts.items()},
            "sigil": engine.sigil_parts(doc, progress, run),
        },
    }


async def _context(session: AsyncSession, row: GuideRun) -> tuple[Guide, Game, GuideVersion, dict]:
    guide = await session.get(Guide, row.guide_id)
    if guide is None:
        raise HTTPException(404, "no such run")
    game = await session.get(Game, guide.game_id)
    version, doc = await _doc_for(session, guide)
    return guide, game, version, doc


async def _answer(session: AsyncSession, user: User, row: GuideRun, *, touch: bool = True) -> dict:
    """The view, after the resets that are due — and the run marked seen."""
    guide, game, version, doc = await _context(session, row)
    now = _now()
    out = _view(row, guide, game, version, doc, user, now)
    changed = _apply_resets(row, doc, user, now)
    if touch:
        row.last_seen_at = now
        changed = True
    if changed:
        await session.commit()
    return out


# ── runs ─────────────────────────────────────────────────────────────────────

@router.get("")
async def mine(request: Request, guide: int | None = None,
               session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The person's runs, newest first; `guide` narrows to one guide."""
    user = await _reader(request, session)
    q = select(GuideRun, Guide, Game).join(Guide, Guide.id == GuideRun.guide_id).join(Game, Game.id == Guide.game_id) \
        .where(GuideRun.user_id == user.id).order_by(GuideRun.updated_at.desc())
    if guide is not None:
        q = q.where(GuideRun.guide_id == guide)
    out = []
    for row, g, game in (await session.execute(q)).all():
        version = await session.get(GuideVersion, g.published_version_id) if g.published_version_id else None
        doc = version.body if version else {}
        progress = engine.compute(doc, _engine_run(row)) if doc else None
        steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
        now_step = steps.get(progress.current) if progress and progress.current else None
        out.append({
            "id": row.id, "name": row.name, "variant": row.variant,
            "guide": {"id": g.id, "slug": g.slug, "title": g.title, "game": {"slug": game.slug, "name": game.name}},
            "now": {"id": now_step["id"], "title": now_step.get("title", "")} if now_step else None,
            "sigil": engine.sigil_parts(doc, progress, _engine_run(row)) if progress else [],
            "updatedAt": _iso(row.updated_at),
        })
    return out


class RunIn(BaseModel):
    guide_id: int
    name: str = ""
    variant: str = ""
    # Step ids the person confirmed skipping on the bulk-skip proposal.
    skip_steps: list[str] = []
    checkin: dict = {}


@router.get("/skip-proposal")
async def skip_proposal(guide: int, groups: str = "", session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Starting a run: "finished the campaign before?" becomes a proposal of the
    phases in those skip groups, with their steps — confirmed, never applied.
    """
    g = await session.get(Guide, guide)
    if g is None:
        raise HTTPException(404, "no such guide")
    _, doc = await _doc_for(session, g)
    wanted = [x.strip() for x in groups.split(",") if x.strip()]
    return engine.bulk_skip_proposal(doc, wanted)


@router.post("", status_code=201)
async def create(body: RunIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    guide = await session.get(Guide, body.guide_id)
    if guide is None or guide.hidden:
        raise HTTPException(404, "no such guide")
    version, doc = await _doc_for(session, guide)
    variants = {v.get("id") for v in doc.get("game", {}).get("variants", []) if isinstance(v, dict)}
    variant = body.variant if body.variant in variants else (sorted(variants)[0] if variants else "")
    known = {s["id"] for s in doc.get("steps", []) if isinstance(s, dict)}
    now = _now().isoformat()
    row = GuideRun(
        guide_id=guide.id, user_id=user.id, version_id=version.id,
        name=body.name.strip()[:80] or guide.title, variant=variant,
        checkin=_clean_checkin(body.checkin, doc),
        steps={sid: {"state": "skipped", "at": now} for sid in body.skip_steps if sid in known},
        routines={}, tracks={}, later=[], link_overrides={},
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return await _answer(session, user, row)


def _clean_checkin(values: dict, doc: dict) -> dict:
    """Only the fields the guide declares, typed as it declares them."""
    out: dict = {}
    for f in doc.get("checkin", []):
        if not isinstance(f, dict) or f["id"] not in values:
            continue
        v = values[f["id"]]
        if v is None or v == "":
            continue
        if f.get("type") == "number":
            try:
                n = float(v)
            except (TypeError, ValueError):
                continue
            lo, hi = f.get("min"), f.get("max")
            if lo is not None:
                n = max(float(lo), n)
            if hi is not None:
                n = min(float(hi), n)
            out[f["id"]] = int(n) if n == int(n) else n
        else:
            if v in (f.get("options") or []):
                out[f["id"]] = v
    return out


@router.get("/{run_id}")
async def one(run_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    return await _answer(session, user, row)


class RunPatch(BaseModel):
    name: str | None = None
    variant: str | None = None


@router.put("/{run_id}")
async def rename(run_id: int, body: RunPatch, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    _, _, _, doc = await _context(session, row)
    if body.name is not None:
        row.name = body.name.strip()[:80] or row.name
    if body.variant is not None:
        variants = {v.get("id") for v in doc.get("game", {}).get("variants", []) if isinstance(v, dict)}
        if body.variant in variants:
            row.variant = body.variant
    return await _answer(session, user, row)


@router.delete("/{run_id}")
async def delete(run_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    await session.delete(row)
    await session.commit()
    return {"ok": True}


# ── progress ─────────────────────────────────────────────────────────────────

class CheckIn(BaseModel):
    values: dict


@router.post("/{run_id}/checkin")
async def checkin(run_id: int, body: CheckIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Save the sheet; the answer carries the proposals it produced. Nothing is marked."""
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    _, _, _, doc = await _context(session, row)
    merged = dict(row.checkin or {})
    merged.update(_clean_checkin(body.values, doc))
    row.checkin = merged
    return await _answer(session, user, row)


class StepIn(BaseModel):
    state: str


@router.post("/{run_id}/steps/{step_id}")
async def set_step(run_id: int, step_id: str, body: StepIn, request: Request,
                   session: AsyncSession = Depends(get_session)) -> dict:
    """
    done · skipped · later · open. `open` is the undo — "Not done after all"
    — and takes the step off the Later list too.
    """
    user = await _reader(request, session)
    if body.state not in STATES:
        raise HTTPException(422, "state is done, skipped, later or open")
    row = await _run_of(session, user, run_id)
    _, _, _, doc = await _context(session, row)
    steps = dict(row.steps or {})
    later = list(row.later or [])
    titles = {s["id"]: s.get("title", "") for s in doc.get("steps", []) if isinstance(s, dict)}
    now = _now()
    if body.state == "open":
        steps.pop(step_id, None)
        later = [x for x in later if x.get("step") != step_id]
    else:
        steps[step_id] = {"state": body.state, "at": now.isoformat()}
        if body.state == "later" and not any(x.get("step") == step_id for x in later):
            later.append({"text": titles.get(step_id, step_id), "step": step_id, "at": now.isoformat()})
        if body.state != "later":
            later = [x for x in later if x.get("step") != step_id]
        if body.state == "done":
            row.last_done, row.last_done_at = step_id, now
    row.steps, row.later = steps, later
    return await _answer(session, user, row)


class AcceptIn(BaseModel):
    steps: list[str]


@router.post("/{run_id}/accept")
async def accept(run_id: int, body: AcceptIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """What the person ticked on a proposal sheet — and only that — is marked done."""
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    _, _, _, doc = await _context(session, row)
    known = {s["id"] for s in doc.get("steps", []) if isinstance(s, dict)}
    steps = dict(row.steps or {})
    now = _now()
    for sid in body.steps:
        if sid in known:
            steps[sid] = {"state": "done", "at": now.isoformat()}
    row.steps = steps
    return await _answer(session, user, row)


class TicksIn(BaseModel):
    ticked: list[str]


@router.post("/{run_id}/routines/{routine_id}")
async def tick(run_id: int, routine_id: str, body: TicksIn, request: Request,
               session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    routines = dict(row.routines or {})
    prior = routines.get(routine_id) or {}
    routines[routine_id] = {"ticked": body.ticked, "reset_at": prior.get("reset_at") or _now().isoformat()}
    row.routines = routines
    return await _answer(session, user, row)


@router.post("/{run_id}/routines/{routine_id}/reset")
async def reset_routine(run_id: int, routine_id: str, request: Request,
                        session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    routines = dict(row.routines or {})
    routines[routine_id] = {"ticked": [], "reset_at": _now().isoformat()}
    row.routines = routines
    return await _answer(session, user, row)


class LaterIn(BaseModel):
    text: str
    step: str | None = None


@router.post("/{run_id}/later")
async def park(run_id: int, body: LaterIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Park a distraction. Nothing here is ordered by urgency and nothing expires."""
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    text = body.text.strip()[:280]
    if not text:
        raise HTTPException(422, "say what to park")
    later = list(row.later or [])
    later.append({"text": text, "step": body.step, "at": _now().isoformat()})
    row.later = later
    return await _answer(session, user, row)


@router.delete("/{run_id}/later/{index}")
async def unpark(run_id: int, index: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    later = list(row.later or [])
    if 0 <= index < len(later):
        gone = later.pop(index)
        # A parked STEP returns to the path when it leaves the list.
        if gone.get("step"):
            steps = dict(row.steps or {})
            if steps.get(gone["step"], {}).get("state") == "later":
                steps.pop(gone["step"], None)
            row.steps = steps
    row.later = later
    return await _answer(session, user, row)


class NoteIn(BaseModel):
    text: str


@router.put("/{run_id}/note")
async def note(run_id: int, body: NoteIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """One note per run, overwritten, never versioned — a diary is something you can fall behind on."""
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    row.note = body.text.strip()[:2000]
    return await _answer(session, user, row)


class TrackIn(BaseModel):
    rank: int | None = None
    day_one: list[str] | None = None
    counters: dict | None = None


@router.put("/{run_id}/track/{track_id}")
async def track(run_id: int, track_id: str, body: TrackIn, request: Request,
                session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    tracks = dict(row.tracks or {})
    state = dict(tracks.get(track_id) or {})
    if body.rank is not None:
        state["rank"] = max(0, int(body.rank))
    if body.day_one is not None:
        state["day_one"] = [str(x) for x in body.day_one]
    if body.counters is not None:
        state["counters"] = {str(k): int(v) for k, v in body.counters.items() if isinstance(v, (int, float))}
    tracks[track_id] = state
    row.tracks = tracks
    return await _answer(session, user, row)


class LinksIn(BaseModel):
    links: list[dict]


@router.put("/{run_id}/links/{step_id}")
async def links(run_id: int, step_id: str, body: LinksIn, request: Request,
                session: AsyncSession = Depends(get_session)) -> dict:
    """"Edit links": the person's own links on a step of their own run."""
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    overrides = dict(row.link_overrides or {})
    clean = [{"label": str(l.get("label", ""))[:120], "url": str(l.get("url", ""))[:500], "type": str(l.get("type", ""))[:20]}
             for l in body.links if isinstance(l, dict) and str(l.get("url", "")).startswith(("http://", "https://"))]
    if clean:
        overrides[step_id] = clean
    else:
        overrides.pop(step_id, None)
    row.link_overrides = overrides
    return await _answer(session, user, row)


# ── nobody's progress is trapped ─────────────────────────────────────────────

@router.get("/{run_id}/export")
async def export_run(run_id: int, request: Request, session: AsyncSession = Depends(get_session)):
    user = await _reader(request, session)
    row = await _run_of(session, user, run_id)
    guide, game, version, _ = await _context(session, row)
    body = {
        "format": 1, "kind": "run",
        "guide": {"game": game.slug, "slug": guide.slug, "title": guide.title, "versionId": version.id},
        "name": row.name, "variant": row.variant, "checkin": row.checkin, "steps": row.steps,
        "routines": row.routines, "tracks": row.tracks, "later": row.later, "note": row.note,
        "linkOverrides": row.link_overrides, "lastDone": row.last_done, "lastDoneAt": _iso(row.last_done_at),
        "exportedAt": _now().isoformat(),
    }
    return JSONResponse(body, headers={"Content-Disposition": f'attachment; filename="{guide.slug}.run.json"'})


class ImportIn(BaseModel):
    guide_id: int
    run: dict


@router.post("/import", status_code=201)
async def import_run(body: ImportIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """A run file, as exported — from here or from a self-hosted tracker."""
    user = await _reader(request, session)
    guide = await session.get(Guide, body.guide_id)
    if guide is None or guide.hidden:
        raise HTTPException(404, "no such guide")
    version, doc = await _doc_for(session, guide)
    r = body.run
    if r.get("kind") != "run":
        raise HTTPException(422, "that is not a run file")
    steps = {str(k): v for k, v in (r.get("steps") or {}).items() if isinstance(v, dict) and v.get("state") in ("done", "skipped", "later")}
    row = GuideRun(
        guide_id=guide.id, user_id=user.id, version_id=version.id,
        name=str(r.get("name") or guide.title)[:80], variant=str(r.get("variant") or ""),
        checkin=_clean_checkin(r.get("checkin") or {}, doc), steps=steps,
        routines={str(k): v for k, v in (r.get("routines") or {}).items() if isinstance(v, dict)},
        tracks={str(k): v for k, v in (r.get("tracks") or {}).items() if isinstance(v, dict)},
        later=[x for x in (r.get("later") or []) if isinstance(x, dict) and x.get("text")][:200],
        note=str(r.get("note") or "")[:2000],
        link_overrides={str(k): v for k, v in (r.get("linkOverrides") or {}).items() if isinstance(v, list)},
        last_done=str(r.get("lastDone") or ""),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return await _answer(session, user, row)
