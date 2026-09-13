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

import logging
import time
from collections import OrderedDict

import json
import re

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.deps import require_admin
from shruti.api.routes.practice import _reader
from shruti.models import OverlayToken
from shruti.models.guides import Game, Guide, GuideRun, GuideVersion
from shrutisguides import progress

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/overlay", tags=["overlay"])
runs_router = APIRouter(prefix="/api/runs", tags=["runs"])

GUIDE_KINDS, THEMES, MOTIONS = progress.GUIDE_KINDS, progress.THEMES, progress.MOTIONS
# The site's one extra kind: a group's goal, bound to a group rather than a run.
SITE_KINDS = GUIDE_KINDS + ("guide-goal",)


def _stored(row: GuideRun) -> dict:
    return {
        "name": row.name, "variant": row.variant, "checkin": row.checkin or {}, "steps": row.steps or {},
        "routines": row.routines or {}, "tracks": row.tracks or {}, "later": row.later or [],
        "note": row.note, "link_overrides": row.link_overrides or {},
    }


@router.get("/guide")
async def guide(t: str, v: str = "", session: AsyncSession = Depends(get_session)) -> dict:
    """
    The run as this token's element draws it. Polled; `version` changes when
    the run changes, so a page can compare and play the Done moment once.

    ⚠ A token whose run is gone answers with an empty frame, not an error —
    an overlay never blanks and never says "connecting".
    """
    token = (await session.execute(select(OverlayToken).where(OverlayToken.token == t))).scalar_one_or_none()
    if token is None or token.kind not in SITE_KINDS:
        raise HTTPException(404, "no such overlay")
    # ⚠ Seen-at is written at most once a minute: a source polls every two
    # seconds, and a row update per poll is the most expensive thing here.
    now = datetime.now(timezone.utc)
    if token.last_seen is None or (now - _aware(token.last_seen)).total_seconds() > 60:
        token.last_seen = now
        await _count_minute(session, token.id, now)
        await session.commit()
    base = {"kind": token.kind, "theme": token.theme if token.theme in THEMES else "almanac",
            "motion": token.motion, "run": None, "element": None, "version": ""}
    if token.kind == "guide-goal":
        return await _goal_frame(session, token, base)
    run = await session.get(GuideRun, token.run_id) if token.run_id else None
    if run is None:
        return base
    layout = progress.clean_layout(token.layout) if token.kind == "guide-layout" else []
    version = run.updated_at.isoformat() if run.updated_at else ""
    if token.kind == "guide-layout":
        version += await _instrument_stamp(session, layout)
    base["version"] = version
    # The cheap answer: the source already shows this version. Nothing is
    # loaded, nothing is computed — and this is nineteen polls in twenty.
    # A plus in an ISO time survives a browser's encoding; a hand-typed URL
    # turns it into a space. Both mean the same version.
    if v and v.replace(" ", "+") == version:
        base["unchanged"] = True
        return base
    g = await session.get(Guide, run.guide_id)
    doc = await _doc(session, g.published_version_id) if g and g.published_version_id else None
    if g is None or doc is None:
        return base
    game = await session.get(Game, g.game_id)
    base["run"] = {"name": run.name, "guide": g.title, "game": game.name if game else ""}
    if token.kind == "guide-layout":
        base["elements"] = progress.layout_elements(layout, _stored(run), doc)
        await _fill_goals(session, base["elements"])
    else:
        base["element"] = progress.element(token.kind, _stored(run), doc, token.routine_id)
    return base


async def _count_minute(session: AsyncSession, token_id: int, now: datetime) -> None:
    """One more minute on air today — the basis for hours streamed this month."""
    from sqlalchemy.dialects.postgresql import insert
    from shruti.models import OverlayUsage
    stmt = insert(OverlayUsage).values(token_id=token_id, day=now.date(), minutes=1)
    await session.execute(stmt.on_conflict_do_update(constraint="uq_overlay_usage_day", set_={"minutes": OverlayUsage.minutes + 1}))


async def hours_this_month(session: AsyncSession, token_ids: list[int]) -> dict[int, float]:
    """Hours on air since the first of the month, per token."""
    from shruti.models import OverlayUsage
    if not token_ids:
        return {}
    first = datetime.now(timezone.utc).date().replace(day=1)
    rows = (await session.execute(
        select(OverlayUsage.token_id, func.sum(OverlayUsage.minutes)).where(OverlayUsage.token_id.in_(token_ids), OverlayUsage.day >= first)
        .group_by(OverlayUsage.token_id)
    )).all()
    return {tid: round(int(m) / 60, 1) for tid, m in rows}


def _aware(t: datetime) -> datetime:
    return t if t.tzinfo is not None else t.replace(tzinfo=timezone.utc)


# A published version never changes; its document is decoded once per process.
_DOCS: "OrderedDict[int, dict]" = OrderedDict()


async def _doc(session: AsyncSession, version_id: int) -> dict | None:
    if version_id in _DOCS:
        _DOCS.move_to_end(version_id)
        return _DOCS[version_id]
    row = await session.get(GuideVersion, version_id)
    if row is None:
        return None
    _DOCS[version_id] = row.body
    while len(_DOCS) > 64:
        _DOCS.popitem(last=False)
    return row.body


# The instruments' answers, kept a little while: the sky and the hours move
# by the minute, support by the second at most; nobody needs them per poll.
_INSTRUMENTS: dict[str, tuple[float, object]] = {}


async def _cached(key: str, ttl: float, compute):
    now = time.monotonic()
    hit = _INSTRUMENTS.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    value = await compute()
    _INSTRUMENTS[key] = (now, value)
    if len(_INSTRUMENTS) > 256:
        for k in sorted(_INSTRUMENTS, key=lambda k: _INSTRUMENTS[k][0])[:64]:
            _INSTRUMENTS.pop(k, None)
    return value


async def _instrument_stamp(session: AsyncSession, elements: list[dict]) -> str:
    """
    A layout redraws when its version changes. The run's is the run's clock;
    an instrument's is the latest support event (alerts, ticker, counter) or
    the five-minute bucket (the sky, the hours). Nothing else polls faster.
    """
    kinds = {e.get("kind") for e in elements}
    stamp = ""
    if kinds & {"alerts", "ticker", "counter"}:
        from shruti.models import SupportEvent

        async def latest_event() -> int:
            return (await session.execute(select(func.max(SupportEvent.id)))).scalar() or 0
        stamp += f":e{await _cached('events:max', 2.0, latest_event)}"
    if kinds & {"guide-goal"}:
        from shruti.models.guides import GroupContribution
        codes = sorted({e.get("group", "") for e in elements if e.get("kind") == "guide-goal"})
        latest = (await session.execute(select(func.max(GroupContribution.id)))).scalar() or 0
        stamp += f":g{latest}:{','.join(codes)}"
    if kinds & {"sky", "hours", "countdown"}:
        stamp += f":t{int(datetime.now(timezone.utc).timestamp() // 300)}"
    return stamp


async def _goal_frame(session: AsyncSession, token: OverlayToken, base: dict) -> dict:
    """A goal token draws its group; a group that is gone is an empty frame, like a run."""
    from shruti.api.routes.groups import _view, goal_element
    from shruti.models.guides import Group
    group = await session.get(Group, token.group_id) if token.group_id else None
    if group is None:
        return base
    view = await _view(session, group, None)
    base["element"] = goal_element(view)
    base["run"] = {"name": group.name, "guide": group.goal, "game": ""}
    base["version"] = f"{view['total']}:{view['members']}:{group.updated_at.isoformat() if group.updated_at else ''}"
    return base


def _counter_element(c, prog: dict) -> dict:
    """€184 of €300, or 14 of 20 — the wording the site's own counter page uses."""
    cur, target = prog.get("current", 0), c.target or 0
    if c.unit == "money":
        sym = {"EUR": "€", "USD": "$", "GBP": "£"}.get((c.currency or "EUR").upper(), (c.currency or "") + " ")
        text, target_text = f"{sym}{cur:,.0f}", (f"of {sym}{target:,.0f}" if target else "")
    else:
        text, target_text = f"{cur:,}", (f"of {target:,}" if target else "")
    return {"name": c.name, "text": text, "target_text": target_text, "current": cur, "target": target, "unit": c.unit}


async def _fill_goals(session: AsyncSession, elements: list[dict]) -> None:
    """
    The host's elements of a layout: a goal names a group by its code, a
    counter names one of her counters by id. The site draws both; a tracker
    draws neither.
    """
    from shruti.api.routes import overlay as instruments
    from shruti.api.routes.groups import goal_by_code
    from shruti.core import counters
    from shruti.models import Counter, SupportEvent
    now = datetime.now(timezone.utc)

    async def counter_of(e: dict):
        c = await session.get(Counter, int(e["counter_id"])) if e.get("counter_id") else None
        return c if c is not None and c.visible else None

    for e in elements:
        kind = e.get("kind")
        try:
            if kind == "guide-goal" and e.get("group"):
                e["element"] = (await goal_by_code(session, e["group"])) or {}
            elif kind == "counter":
                c = await counter_of(e)
                e["element"] = _counter_element(c, await counters.progress(session, c)) if c is not None else {}
            elif kind == "ticker":
                c = await counter_of(e)
                e["element"] = await _cached(f"ticker:{c.id if c else 0}", 5.0, lambda: instruments.ticker_payload(session, c, 18))
            elif kind == "sky":
                e["element"] = await _cached(f"sky:{e.get('lat')}:{e.get('lon')}", 60.0, lambda: instruments.sky_now(e.get("lat", 37.9838), e.get("lon", 23.7275)))
            elif kind == "hours":
                e["element"] = await _cached(f"hours:{e.get('lat')}:{e.get('lon')}", 60.0, lambda: instruments.hours_now(e.get("lat", 37.9838), e.get("lon", 23.7275)))
            elif kind == "countdown":
                c = await counter_of(e)
                e["element"] = ({"name": c.name, "note": c.note, "now": now.isoformat(),
                                 "endsAt": c.ends_at.isoformat() if c.ends_at else None,
                                 "startsAt": c.starts_at.isoformat() if c.starts_at else None} if c is not None else {})
            elif kind == "alerts":
                rows = (await session.execute(select(SupportEvent).order_by(SupportEvent.id.desc()).limit(5))).scalars().all()
                e["element"] = {"events": [{"id": r.id, "source": r.source, "who": r.who or "Someone", "amountMinor": r.amount_minor,
                                            "currency": r.currency, "quantity": r.quantity,
                                            "message": r.message if r.message_approved else ""} for r in reversed(rows)]}
            elif kind == "wheel":
                query = "".join(ch for ch in str(e.get("shows") or "") if ch.isalnum() or ch in "=&-_")[:80]
                e["element"] = {"src": f"/overlay/wheel?size={int(e.get('w', 432))}&bg=" + (f"&{query}" if query else "")}
        except Exception as exc:                        # noqa: BLE001
            # An instrument that cannot answer leaves its element empty; the layout never blanks.
            log.warning("layout element %s unavailable: %s", kind, type(exc).__name__)
            e["element"] = {}


PRIVATE_FIELDS = ("routine_id", "group", "counter_id", "text", "url")

# ── the themes' tokens, editable by her ──────────────────────────────────────
#
# ⚠ A theme may change palette, type, ornament and the sigil's stroke. It may
# not change layout, legibility or the four state colours — so the editable
# set is exactly these, and nothing beginning with st-.
EDITABLE = ("panel", "panel-dim", "border", "ink", "soft", "faint", "eyebrow", "rule",
            "radius", "display-weight", "stroke", "left-rule", "ring")
THEMES_KEY = "overlay.themes"
_COLOUR = re.compile(r"^(#[0-9a-fA-F]{3,8}|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(,\s*(0|1|0?\.\d+))?\s*\)|transparent)$")
_LENGTH = re.compile(r"^\d{1,3}px$")
_NUMBER = re.compile(r"^\d{1,3}$")


def css_value(token: str, value: str) -> str:
    """The value if it is a colour, a length or a number as the token wants; empty otherwise."""
    v = str(value or "").strip()
    if token in ("radius", "left-rule"):
        return v if _LENGTH.match(v) else ""
    if token in ("stroke", "display-weight"):
        return v if _NUMBER.match(v) else ""
    return v if _COLOUR.match(v) else ""


def clean_themes(raw) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not isinstance(raw, dict):
        return out
    for name in THEMES:
        block = raw.get(name)
        if not isinstance(block, dict):
            continue
        kept = {t: css_value(t, block.get(t)) for t in EDITABLE if block.get(t) not in (None, "")}
        kept = {t: v for t, v in kept.items() if v}
        if kept:
            out[name] = kept
    return out


def theme_css(themes: dict[str, dict[str, str]]) -> str:
    """One rule per theme that has overrides, re-pointing only its own tokens."""
    rules = []
    for name, block in themes.items():
        if name in THEMES and block:
            rules.append(f'.gov[data-theme="{name}"]{{' + "".join(f"--gt-{t}:{v};" for t, v in block.items() if t in EDITABLE) + "}")
    return "\n".join(rules)


async def _themes(session: AsyncSession) -> dict[str, dict[str, str]]:
    from shruti.core.settings_store import get_many
    raw = (await get_many(session, (THEMES_KEY,))).get(THEMES_KEY, "")
    try:
        return clean_themes(json.loads(raw)) if raw else {}
    except ValueError:
        return {}


@router.get("/themes")
async def themes(session: AsyncSession = Depends(get_session)) -> dict:
    """Her adjustments to the three themes, and the stylesheet they make. Public: every overlay wears them."""
    overrides = await _themes(session)
    return {"themes": overrides, "editable": list(EDITABLE), "css": theme_css(overrides)}


class ThemesIn(BaseModel):
    themes: dict


@router.put("/admin/themes", dependencies=[Depends(require_admin)])
async def set_themes(body: ThemesIn, session: AsyncSession = Depends(get_session)) -> dict:
    """Replace her adjustments. Anything that is not a colour, a length or a number is dropped, not saved."""
    from shruti.core.settings_store import put_many
    cleaned = clean_themes(body.themes)
    await put_many(session, {THEMES_KEY: json.dumps(cleaned)})
    await session.commit()
    return {"ok": True, "themes": cleaned, "css": theme_css(cleaned)}


@router.get("/gallery")
async def gallery(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Her shared layouts, for anybody to start from: the kinds and their
    places, the theme and the motion. Never her tokens, and never the
    fields that name her routines, groups or counters — a person fills
    those with their own.
    """
    from shruti.core.operator import operator_email
    from shruti.models.accounts import User
    email = await operator_email(session)
    her = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none() if email else None
    if her is None:
        return []
    runs = [r.id for r in (await session.execute(select(GuideRun).where(GuideRun.user_id == her.id))).scalars().all()]
    if not runs:
        return []
    rows = (await session.execute(
        select(OverlayToken).where(OverlayToken.kind == "guide-layout", OverlayToken.shared.is_(True), OverlayToken.run_id.in_(runs))
        .order_by(OverlayToken.id)
    )).scalars().all()
    out = []
    for o in rows:
        layout = [{k: v for k, v in e.items() if k not in PRIVATE_FIELDS} for e in progress.clean_layout(o.layout)]
        out.append({"id": o.id, "label": o.label, "theme": o.theme, "motion": o.motion, "layout": layout})
    return out


@router.get("/mine")
async def my_tokens(request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Every guide overlay this person holds — the runs' and the groups' —
    WITHOUT their tokens (board W8's table: name, what it shows, theme,
    live or idle). A token is readable once, when minted.
    """
    from shruti.api.routes.practice import _reader
    from shruti.models.guides import Group
    user = await _reader(request, session)
    runs = {r.id: r for r in (await session.execute(select(GuideRun).where(GuideRun.user_id == user.id))).scalars().all()}
    rows = (await session.execute(
        select(OverlayToken).where(
            OverlayToken.kind.in_(SITE_KINDS),
            (OverlayToken.run_id.in_(list(runs)) if runs else False) | (OverlayToken.user_id == user.id),
        ).order_by(OverlayToken.id)
    )).scalars().all()
    now = datetime.now(timezone.utc)
    hours = await hours_this_month(session, [o.id for o in rows])
    out = []
    for o in rows:
        if o.kind == "guide-goal":
            group = await session.get(Group, o.group_id) if o.group_id else None
            showing, href = (group.name if group else ""), (f"/groups/{group.code}" if group else "")
        else:
            run = runs.get(o.run_id)
            showing, href = (run.name if run else ""), ""
            if run:
                g = await session.get(Guide, run.guide_id)
                game = await session.get(Game, g.game_id) if g else None
                href = f"/guides/{game.slug}/{g.slug}/track?run={run.id}" if g and game else ""
        seen = o.last_seen.replace(tzinfo=timezone.utc) if o.last_seen and o.last_seen.tzinfo is None else o.last_seen
        out.append({"id": o.id, "kind": o.kind, "label": o.label, "theme": o.theme, "motion": o.motion,
                    "showing": showing, "href": href,
                    "live": bool(seen and (now - seen).total_seconds() < 15),
                    "hoursThisMonth": hours.get(o.id, 0.0),
                    "lastSeen": o.last_seen.isoformat() if o.last_seen else None})
    return out


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
             "routineId": o.routine_id, "layout": o.layout or [], "shared": o.shared,
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
    # Hers only takes effect: the gallery shows the operator's shared layouts.
    shared: bool | None = None


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
    if body.shared is not None:
        row.shared = bool(body.shared)
    await session.commit()
    return {"ok": True, "layout": row.layout, "shared": row.shared}


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
