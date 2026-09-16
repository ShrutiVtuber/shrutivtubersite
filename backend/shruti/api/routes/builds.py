# SPDX-License-Identifier: AGPL-3.0-only
"""
Builds: a set of goals for one character, tracked slot by slot.

A TEMPLATE, hers, says what a build of one game is made of — categories of
items, each a slot to fill, a counter to reach or a thing to tick. It is
generic enough for Diablo IV today and Path of Exile 2 tomorrow, and edited
from the admin, so a new game is a new template and not a new deploy.

A BUILD is one person's: the template with their own targets written in
("Shroud of False Death, 2 greater affixes") and how far they have got. It
is drawn on stream by its own overlay element and ticked from the app.

⚠ Nothing measures absence. A goal is met, partly met or not yet; there is
no "since", no rate, no percentage of a person. The one number on the
plate is met-of-total, which is a fact about the build.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session, require_admin
from shruti.api.routes.practice import _reader, _refuse_if_suspended
from shruti.models import OverlayToken
from shruti.models.guides import Build, BuildTemplate, Game, GuideRun

router = APIRouter(prefix="/api/builds", tags=["builds"])

ITEM_KINDS = ("slot", "counter", "check")
MAX_CATEGORIES = 24
MAX_ITEMS = 60


# ── the template's shape, cleaned once ──────────────────────────────────────

def _ident(value, fallback: str) -> str:
    v = "".join(ch for ch in str(value or "").strip().lower().replace(" ", "-") if ch.isalnum() or ch in "-_")[:40]
    return v or fallback


def clean_categories(raw) -> list[dict]:
    """[{id, name, items: [{id, label, kind, hint, max, unit}]}] — unknown kinds become checks."""
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    seen: set[str] = set()
    for ci, c in enumerate(raw[:MAX_CATEGORIES]):
        if not isinstance(c, dict):
            continue
        cid = _ident(c.get("id") or c.get("name"), f"c{ci + 1}")
        while cid in seen:
            cid += "-2"
        seen.add(cid)
        items: list[dict] = []
        used: set[str] = set()
        for ii, it in enumerate((c.get("items") or [])[:MAX_ITEMS]):
            if not isinstance(it, dict):
                continue
            iid = _ident(it.get("id") or it.get("label"), f"{cid}-{ii + 1}")
            while iid in used:
                iid += "-2"
            used.add(iid)
            kind = it.get("kind") if it.get("kind") in ITEM_KINDS else "check"
            try:
                mx = max(0, int(it.get("max") or 0))
            except (TypeError, ValueError):
                mx = 0
            items.append({"id": iid, "label": str(it.get("label") or iid)[:80], "kind": kind,
                          "hint": str(it.get("hint") or "")[:120], "max": mx, "unit": str(it.get("unit") or "")[:20]})
        out.append({"id": cid, "name": str(c.get("name") or cid)[:60], "items": items, "grid": bool(c.get("grid"))})
    # One grid per template: the first flagged category keeps the flag.
    seen_grid = False
    for c in out:
        if c["grid"] and not seen_grid:
            seen_grid = True
        else:
            c["grid"] = False
    return out


# ── progress, computed here so every surface agrees ─────────────────────────

def _goal(goals: dict, item_id: str) -> dict:
    g = goals.get(item_id) if isinstance(goals, dict) else None
    return g if isinstance(g, dict) else {}


def item_state(item: dict, goal: dict) -> tuple[str, float]:
    """met | partial | open, and how far along, for one item."""
    if item["kind"] == "counter":
        want = goal.get("want")
        try:
            want = int(want) if want not in (None, "") else int(item.get("max") or 0)
        except (TypeError, ValueError):
            want = int(item.get("max") or 0)
        try:
            have = int(goal.get("have") or 0)
        except (TypeError, ValueError):
            have = 0
        if want <= 0:
            return ("met" if goal.get("met") else "open"), (1.0 if goal.get("met") else 0.0)
        ratio = max(0.0, min(1.0, have / want))
        return ("met" if have >= want else ("partial" if have > 0 else "open")), ratio
    met = bool(goal.get("met"))
    if item["kind"] == "slot" and not met and goal.get("partial"):
        return "partial", 0.5
    return ("met" if met else "open"), (1.0 if met else 0.0)


def progress_of(template: BuildTemplate, build: Build) -> dict:
    goals = build.goals or {}
    cats = []
    met_all = total_all = 0
    next_open: list[dict] = []
    partly_all = 0
    for c in template.categories or []:
        met = total = partly = 0
        ratio_sum = 0.0
        items = []
        for it in c.get("items", []):
            g = _goal(goals, it["id"])
            state, ratio = item_state(it, g)
            total += 1
            met += 1 if state == "met" else 0
            partly += 1 if state == "partial" else 0
            ratio_sum += ratio
            row = {"id": it["id"], "label": it["label"], "kind": it["kind"], "state": state, "ratio": round(ratio, 3),
                   "target": str(g.get("target") or "")[:120], "note": str(g.get("note") or "")[:200]}
            if it["kind"] == "counter":
                try:
                    row["have"] = int(g.get("have") or 0)
                except (TypeError, ValueError):
                    row["have"] = 0
                try:
                    row["want"] = int(g.get("want")) if g.get("want") not in (None, "") else int(it.get("max") or 0)
                except (TypeError, ValueError):
                    row["want"] = int(it.get("max") or 0)
                row["unit"] = it.get("unit", "")
            items.append(row)
            if state != "met" and len(next_open) < 6:
                next_open.append({"id": it["id"], "kind": it["kind"], "category": c["name"], "categoryId": c["id"],
                                  "label": it["label"], "target": row["target"], "state": state,
                                  "have": row.get("have"), "want": row.get("want"), "unit": row.get("unit", "")})
        cats.append({"id": c["id"], "name": c["name"], "met": met, "partly": partly, "total": total,
                     "ratio": round(ratio_sum / total, 3) if total else 0.0, "grid": bool(c.get("grid")), "items": items})
        met_all += met
        total_all += total
        partly_all += partly
    return {"met": met_all, "partly": partly_all, "total": total_all,
            "ratio": round(met_all / total_all, 3) if total_all else 0.0,
            "categories": cats, "next": next_open, "complete": total_all > 0 and met_all == total_all}


def _template_view(t: BuildTemplate, game: Game | None) -> dict:
    return {"id": t.id, "name": t.name, "description": t.description, "visible": t.visible, "position": t.position,
            "game": {"id": game.id, "slug": game.slug, "name": game.name} if game else None,
            "categories": t.categories or []}


async def _build_view(session: AsyncSession, b: Build) -> dict:
    t = await session.get(BuildTemplate, b.template_id)
    game = await session.get(Game, t.game_id) if t else None
    return {"id": b.id, "name": b.name, "variant": b.variant, "runId": b.run_id,
            "template": _template_view(t, game) if t else None,
            "goals": b.goals or {},
            "progress": progress_of(t, b) if t else {"met": 0, "total": 0, "ratio": 0.0, "categories": [], "next": [], "complete": False},
            "updatedAt": b.updated_at.isoformat() if b.updated_at else None}


async def _mine(session: AsyncSession, request: Request, build_id: int) -> tuple[Build, object]:
    user = await _reader(request, session)
    b = await session.get(Build, build_id)
    if b is None or b.user_id != user.id:
        raise HTTPException(404, "no such build")
    return b, user


# ── templates: read by anybody, written by her ──────────────────────────────

@router.get("/templates")
async def templates(game: str = "", session: AsyncSession = Depends(get_session)) -> list[dict]:
    q = select(BuildTemplate, Game).join(Game, Game.id == BuildTemplate.game_id).where(BuildTemplate.visible.is_(True))
    if game:
        q = q.where(Game.slug == game)
    rows = (await session.execute(q.order_by(BuildTemplate.position, BuildTemplate.id))).all()
    return [_template_view(t, g) for t, g in rows]


class TemplateIn(BaseModel):
    game: str = Field(min_length=1, max_length=80)       # the game's slug; a new one is made by name
    game_name: str = ""
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=400)
    categories: list = Field(default_factory=list)
    visible: bool = True
    position: int = 0


@router.get("/admin/templates", dependencies=[Depends(require_admin)])
async def admin_templates(session: AsyncSession = Depends(get_session)) -> list[dict]:
    from sqlalchemy import func
    rows = (await session.execute(
        select(BuildTemplate, Game).join(Game, Game.id == BuildTemplate.game_id).order_by(BuildTemplate.position, BuildTemplate.id)
    )).all()
    counts = dict((await session.execute(select(Build.template_id, func.count()).group_by(Build.template_id))).all())
    return [{**_template_view(t, g), "builds": int(counts.get(t.id, 0))} for t, g in rows]


@router.post("/admin/templates", status_code=201, dependencies=[Depends(require_admin)])
async def create_template(body: TemplateIn, session: AsyncSession = Depends(get_session)) -> dict:
    slug = _ident(body.game, "game")
    game = (await session.execute(select(Game).where(Game.slug == slug))).scalars().first()
    if game is None:
        game = Game(slug=slug, name=body.game_name.strip() or body.game.strip(), variants=[])
        session.add(game)
        await session.flush()
    t = BuildTemplate(game_id=game.id, name=body.name.strip(), description=body.description.strip(),
                      categories=clean_categories(body.categories), visible=body.visible, position=body.position)
    session.add(t)
    await session.commit()
    await session.refresh(t)
    return _template_view(t, game)


@router.put("/admin/templates/{template_id}", dependencies=[Depends(require_admin)])
async def update_template(template_id: int, body: TemplateIn, session: AsyncSession = Depends(get_session)) -> dict:
    t = await session.get(BuildTemplate, template_id)
    if t is None:
        raise HTTPException(404, "no such template")
    t.name = body.name.strip()
    t.description = body.description.strip()
    t.categories = clean_categories(body.categories)
    t.visible = body.visible
    t.position = body.position
    await session.commit()
    await session.refresh(t)
    return _template_view(t, await session.get(Game, t.game_id))


@router.delete("/admin/templates/{template_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_template(template_id: int, session: AsyncSession = Depends(get_session)) -> None:
    t = await session.get(BuildTemplate, template_id)
    if t is None:
        raise HTTPException(404, "no such template")
    used = (await session.execute(select(Build.id).where(Build.template_id == template_id).limit(1))).first()
    if used:
        # People's builds stand on it: hide it instead of pulling it away.
        t.visible = False
    else:
        await session.delete(t)
    await session.commit()


# ── a person's builds ───────────────────────────────────────────────────────

class BuildIn(BaseModel):
    template_id: int
    name: str = Field(min_length=1, max_length=80)
    variant: str = Field(default="", max_length=80)
    run_id: int | None = None


@router.get("")
async def my_builds(request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    user = await _reader(request, session)
    rows = (await session.execute(select(Build).where(Build.user_id == user.id).order_by(Build.updated_at.desc()))).scalars().all()
    out = []
    for b in rows:
        v = await _build_view(session, b)
        v.pop("goals", None)
        v["progress"] = {k: v["progress"][k] for k in ("met", "total", "ratio", "complete")} | {
            "categories": [{"id": c["id"], "name": c["name"], "met": c["met"], "total": c["total"], "ratio": c["ratio"]} for c in v["progress"]["categories"]]}
        out.append(v)
    return out


@router.post("", status_code=201)
async def create_build(body: BuildIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    t = await session.get(BuildTemplate, body.template_id)
    if t is None or not t.visible:
        raise HTTPException(404, "no such template")
    run_id = None
    if body.run_id:
        run = await session.get(GuideRun, body.run_id)
        run_id = run.id if run is not None and run.user_id == user.id else None
    b = Build(user_id=user.id, template_id=t.id, run_id=run_id, name=body.name.strip(), variant=body.variant.strip(), goals={})
    session.add(b)
    await session.commit()
    await session.refresh(b)
    return await _build_view(session, b)


@router.get("/{build_id}")
async def one(build_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, _ = await _mine(session, request, build_id)
    return await _build_view(session, b)


class BuildPatch(BaseModel):
    name: str | None = None
    variant: str | None = None
    run_id: int | None = None


@router.put("/{build_id}")
async def rename(build_id: int, body: BuildPatch, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, user = await _mine(session, request, build_id)
    if body.name is not None:
        b.name = body.name.strip()[:80] or b.name
    if body.variant is not None:
        b.variant = body.variant.strip()[:80]
    if body.run_id is not None:
        run = await session.get(GuideRun, body.run_id) if body.run_id else None
        b.run_id = run.id if run is not None and run.user_id == user.id else None
    await session.commit()
    return await _build_view(session, b)


class GoalIn(BaseModel):
    """One goal's own words and state. Absent fields are left as they are."""
    target: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=200)
    met: bool | None = None
    partial: bool | None = None
    have: int | None = Field(default=None, ge=0, le=1_000_000)
    want: int | None = Field(default=None, ge=0, le=1_000_000)


@router.put("/{build_id}/goals/{item_id}")
async def set_goal(build_id: int, item_id: str, body: GoalIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, _ = await _mine(session, request, build_id)
    t = await session.get(BuildTemplate, b.template_id)
    known = {it["id"] for c in (t.categories if t else []) for it in c.get("items", [])}
    if item_id not in known:
        raise HTTPException(404, "no such goal in this build")
    goals = dict(b.goals or {})
    g = dict(goals.get(item_id) or {})
    for field in ("target", "note", "met", "partial", "have", "want"):
        value = getattr(body, field)
        if value is not None:
            g[field] = value
    if body.met:
        g["partial"] = False
    goals[item_id] = g
    b.goals = goals
    b.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return await _build_view(session, b)


@router.delete("/{build_id}")
async def delete_build(build_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, _ = await _mine(session, request, build_id)
    for tok in (await session.execute(select(OverlayToken).where(OverlayToken.build_id == b.id))).scalars().all():
        await session.delete(tok)
    await session.delete(b)
    await session.commit()
    return {"ok": True}


# ── the build on stream ─────────────────────────────────────────────────────

class BuildTokenIn(BaseModel):
    label: str = ""
    theme: str = "almanac"
    motion: str = "reduced"


def build_element(view: dict) -> dict:
    """What the build overlay draws: the name, met-of-total, one arc per category, the next open goals."""
    p = view["progress"]
    grid = next((c for c in p["categories"] if c.get("grid")), None)
    game = (view.get("template") or {}).get("game") or {}
    return {
        "name": view["name"], "variant": view["variant"], "game": game.get("name", ""),
        "eyebrow": " · ".join(x for x in ("Build", game.get("name", ""), view["variant"]) if x),
        "met": p["met"], "partly": p["partly"], "total": p["total"], "ratio": p["ratio"], "complete": p["complete"],
        "count": f"{p['met']} of {p['total']}",
        # Two fills per arc: rose to met, blue on to met + partly — motion, not absence.
        "parts": [{"pct": (c["met"] / c["total"]) if c["total"] else 0.0,
                   "partly": ((c["met"] + c["partly"]) / c["total"]) if c["total"] else 0.0,
                   "state": "done" if c["total"] and c["met"] == c["total"] else ("now" if (c["met"] + c["partly"]) > 0 else "todo"),
                   "name": c["name"], "met": c["met"], "total": c["total"]} for c in p["categories"]],
        "gridName": grid["name"] if grid else "",
        "slots": [{"label": it["label"], "state": it["state"]} for it in (grid["items"] if grid else []) if it["kind"] == "slot"][:25],
        "next": [{"category": n["category"], "label": n["label"], "detail": n["target"] or (f"{n['have']} of {n['want']} {n['unit']}".strip() if n["kind"] == "counter" else ""),
                  "word": "partly" if n["state"] == "partial" else "not yet"} for n in p["next"][:3]],
    }


async def build_frame(session: AsyncSession, build_id: int | None) -> dict | None:
    b = await session.get(Build, build_id) if build_id else None
    if b is None:
        return None
    return build_element(await _build_view(session, b))


@router.get("/{build_id}/overlays")
async def build_tokens(build_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    b, _ = await _mine(session, request, build_id)
    rows = (await session.execute(select(OverlayToken).where(OverlayToken.build_id == b.id).order_by(OverlayToken.id))).scalars().all()
    return [{"id": o.id, "kind": o.kind, "label": o.label, "theme": o.theme, "motion": o.motion,
             "lastSeen": o.last_seen.isoformat() if o.last_seen else None} for o in rows]


@router.post("/{build_id}/overlays", status_code=201)
async def mint_build_token(build_id: int, body: BuildTokenIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """The build as a browser source; the token is returned once."""
    from shrutisguides.progress import MOTIONS, THEMES
    from shruti.api.routes.overlay_guides import refuse_if_out_of_allowance
    b, user = await _mine(session, request, build_id)
    await _refuse_if_suspended(session, user)
    await refuse_if_out_of_allowance(session, user)
    token = secrets.token_urlsafe(24)
    row = OverlayToken(token=token, kind="build", label=body.label.strip()[:80] or b.name, user_id=user.id, build_id=b.id,
                       theme=body.theme if body.theme in THEMES else "almanac",
                       motion=body.motion if body.motion in MOTIONS else "reduced")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "token": token, "kind": row.kind, "theme": row.theme, "motion": row.motion}


@router.delete("/{build_id}/overlays/{token_id}", status_code=204)
async def drop_build_token(build_id: int, token_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    b, _ = await _mine(session, request, build_id)
    row = (await session.execute(select(OverlayToken).where(OverlayToken.id == token_id, OverlayToken.build_id == b.id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such overlay")
    await session.delete(row)
    await session.commit()
