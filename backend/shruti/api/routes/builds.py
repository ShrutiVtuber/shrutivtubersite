# SPDX-License-Identifier: AGPL-3.0-only
"""
Builds on the site: templates, hers; a build, one person's; the build on
stream. The logic lives in the shared package (`shrutisguides.builds`) so
the self-hosted tracker and the site cannot disagree — these routes keep
the rows, check who is asking, and hand the rest to it.

⚠ Nothing measures absence. A goal is met, partly met or not yet.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shrutisguides import builds as shared
from shrutisguides.builds import clean_categories, item_state, parse_list  # noqa: F401  (re-exported for callers and tests)
from shrutisguides.gamedata import clean_plan, plan_goals, plan_summary, plan_to_categories

from shruti.api.deps import get_session, require_admin
from shruti.api.routes.gamedata import data as gamedata
from shruti.api.routes.practice import _reader, _refuse_if_suspended
from shruti.models import OverlayToken
from shruti.models.guides import Build, BuildTemplate, Game, GuideRun

router = APIRouter(prefix="/api/builds", tags=["builds"])


# ── the shapes every surface reads ──────────────────────────────────────────

def categories_of(template: BuildTemplate | None, build: Build) -> list:
    """A planned build carries its own categories; one made from a template reads the template's."""
    return build.categories or (template.categories if template else None) or []


def progress_of(template: BuildTemplate | None, build: Build) -> dict:
    return shared.progress(categories_of(template, build), build.goals or {})


def build_element(view: dict) -> dict:
    game = ((view.get("template") or {}).get("game") or {}).get("name", "")
    return shared.element(view["name"], view["variant"], game, view["progress"])


def _template_view(t: BuildTemplate, game: Game | None) -> dict:
    return {"id": t.id, "name": t.name, "description": t.description, "visible": t.visible, "position": t.position,
            "game": {"id": game.id, "slug": game.slug, "name": game.name} if game else None,
            "categories": t.categories or []}


def _planned_template(b: Build, game: Game | None) -> dict:
    """
    A planned build shown in the shape of a template, so the phone and the
    overlay — which read `template.categories` and `template.game` — need
    no second shape for it.
    """
    return {"id": None, "name": "Planned", "description": "", "visible": True, "position": 0,
            "game": {"id": game.id, "slug": game.slug, "name": game.name} if game else None,
            "categories": b.categories or []}


async def _build_view(session: AsyncSession, b: Build) -> dict:
    t = await session.get(BuildTemplate, b.template_id) if b.template_id else None
    game = await session.get(Game, t.game_id if t else b.game_id) if (t or b.game_id) else None
    view = {"id": b.id, "name": b.name, "variant": b.variant, "runId": b.run_id,
            "template": _template_view(t, game) if t else _planned_template(b, game),
            "goals": b.goals or {},
            "progress": progress_of(t, b),
            "updatedAt": b.updated_at.isoformat() if b.updated_at else None}
    if b.plan:
        view["plan"] = b.plan
        view["planned"] = plan_summary(b.plan, gamedata())
    return view


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
    rows = (await session.execute(
        select(BuildTemplate, Game).join(Game, Game.id == BuildTemplate.game_id).order_by(BuildTemplate.position, BuildTemplate.id)
    )).all()
    counts = dict((await session.execute(select(Build.template_id, func.count()).group_by(Build.template_id))).all())
    return [{**_template_view(t, g), "builds": int(counts.get(t.id, 0))} for t, g in rows]


@router.post("/admin/templates", status_code=201, dependencies=[Depends(require_admin)])
async def create_template(body: TemplateIn, session: AsyncSession = Depends(get_session)) -> dict:
    slug = shared.ident(body.game, "game")
    game = (await session.execute(select(Game).where(Game.slug == slug))).scalars().first()
    if game is None:
        game = Game(slug=slug, name=body.game_name.strip() or body.game.strip(), variants=[])
        session.add(game)
        await session.flush()
    t = BuildTemplate(game_id=game.id, name=body.name.strip(), description=body.description.strip(),
                      categories=shared.clean_categories(body.categories), visible=body.visible, position=body.position)
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
    t.categories = shared.clean_categories(body.categories)
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
        p = v["progress"]
        v["progress"] = {k: p[k] for k in ("met", "partly", "total", "ratio", "complete")} | {
            "categories": [{k: c[k] for k in ("id", "name", "met", "partly", "total", "ratio")} for c in p["categories"]]}
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


# ── a planned build: the game's own terms, written as goals ─────────────────

class PlanIn(BaseModel):
    """A plan in the game's own terms; see shrutisguides.gamedata.planner for the shape."""
    game: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=80)
    variant: str = Field(default="", max_length=80)
    run_id: int | None = None
    plan: dict = Field(default_factory=dict)


class RePlanIn(BaseModel):
    plan: dict = Field(default_factory=dict)


async def _game_row(session: AsyncSession, slug: str, name: str) -> Game:
    game = (await session.execute(select(Game).where(Game.slug == slug))).scalars().first()
    if game is None:
        game = Game(slug=slug, name=name, variants=[])
        session.add(game)
        await session.flush()
    return game


def _planned(raw_plan: dict, game_slug: str) -> tuple[dict, list, list[str]]:
    """The plan cleaned against the game's data, and the categories it makes. Refused in words when there is nothing to plan with."""
    d = gamedata()
    plan, problems = clean_plan({**raw_plan, "game": game_slug}, d)
    if not plan:
        raise HTTPException(422, problems[0] if problems else "that plan cannot be read")
    cats = plan_to_categories(plan, d)
    if not cats:
        raise HTTPException(422, "the plan chooses nothing yet")
    return plan, cats, problems


@router.post("/plan", status_code=201)
async def create_planned_build(body: PlanIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """A build from a plan: no template, the game's data instead. Answers with the build and what the plan could not keep."""
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    slug = shared.ident(body.game, "game")
    plan, cats, problems = _planned(body.plan, slug)
    pack = gamedata().game(slug) or {}
    game = await _game_row(session, slug, pack.get("name") or body.game.strip())
    run_id = None
    if body.run_id:
        run = await session.get(GuideRun, body.run_id)
        run_id = run.id if run is not None and run.user_id == user.id else None
    b = Build(user_id=user.id, template_id=None, game_id=game.id, run_id=run_id, name=body.name.strip(),
              variant=body.variant.strip() or plan_summary(plan, gamedata()).get("className", ""),
              plan=plan, categories=cats, goals=plan_goals(cats))
    session.add(b)
    await session.commit()
    await session.refresh(b)
    return {**(await _build_view(session, b)), "problems": problems}


@router.put("/{build_id}/plan")
async def replan(build_id: int, body: RePlanIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """The plan changed: the categories are rewritten, and every goal whose id survives keeps its words and its state."""
    b, _ = await _mine(session, request, build_id)
    if not b.plan and b.template_id:
        raise HTTPException(409, "this build was made from a template, not a plan")
    game = await session.get(Game, b.game_id) if b.game_id else None
    if game is None:
        raise HTTPException(409, "this build has no game to plan against")
    plan, cats, problems = _planned(body.plan, game.slug)
    b.plan = plan
    b.categories = cats
    b.goals = plan_goals(cats, b.goals)
    b.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(b)
    return {**(await _build_view(session, b)), "problems": problems}


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
    have: int | None = Field(default=None, ge=0, le=shared.MAX_COUNT)
    want: int | None = Field(default=None, ge=0, le=shared.MAX_COUNT)


@router.put("/{build_id}/goals/{item_id}")
async def set_goal(build_id: int, item_id: str, body: GoalIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, _ = await _mine(session, request, build_id)
    t = await session.get(BuildTemplate, b.template_id) if b.template_id else None
    if item_id not in shared.known_items(categories_of(t, b)):
        raise HTTPException(404, "no such goal in this build")
    b.goals = shared.apply_goal(b.goals, item_id, body.model_dump(exclude_none=True))
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


class BuildRebindIn(BaseModel):
    build_id: int


@router.put("/{build_id}/overlays/{token_id}")
async def rebind_build_token(build_id: int, token_id: int, body: BuildRebindIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Point a build overlay at another of the person's builds — the stream switches without a new source in OBS."""
    b, user = await _mine(session, request, build_id)
    row = (await session.execute(select(OverlayToken).where(OverlayToken.id == token_id, OverlayToken.build_id == b.id))).scalar_one_or_none()
    target = await session.get(Build, body.build_id)
    if row is None or target is None or target.user_id != user.id:
        raise HTTPException(404, "no such overlay or build")
    row.build_id = target.id
    await session.commit()
    return {"ok": True, "id": row.id, "buildId": target.id}


@router.delete("/{build_id}/overlays/{token_id}", status_code=204)
async def drop_build_token(build_id: int, token_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    b, _ = await _mine(session, request, build_id)
    row = (await session.execute(select(OverlayToken).where(OverlayToken.id == token_id, OverlayToken.build_id == b.id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such overlay")
    await session.delete(row)
    await session.commit()
