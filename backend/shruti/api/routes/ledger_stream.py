# SPDX-License-Identifier: AGPL-3.0-only
"""
The Ledger on stream: overlays minted from a ledger, the business on screen,
and the plan on stream (docs/LEDGER.md, "The Ledger on stream";
design_handoff_ledger_overlays README §3–§8 and A1–A6).

Seven kinds, all drawn by `/overlay/ledger?t=` from the frame below:

    ledger-plate · ledger-card · ledger-strip · ledger-limit · ledger-counter
    ledger-plan-panel · ledger-plan-card

⚠ **The frame is the whole of what chat can learn.** It carries the company's
name, the version and build, the OPEN businesses in the ledger's own order
with their neighbourhood and their latest written week, the company's latest
week, which business is on screen and that business's kept plan (so the
browser source reckons its limit with the same engine as the Ledger). The plan
kinds carry the live plan and nothing else of the ledger. Never cash on hand,
never a note, never a plan that was not opened, never another plan, and never
where a week came from: `test_the_ledger_on_stream` builds a frame from a
ledger that has all of those and looks for each.

⚠ **A week's total is money in minus the lines written.** A line that was not
written is left out of the sum, never read as zero; a week with no money in
has no total at all.

⚠ **Minting follows every other overlay:** the same fair use
(`refuse_if_out_of_allowance`), never a charge, the token shown once. These
routes live apart from `ledger.py` because the Ledger itself is ungated, and
its guard says so.
"""
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import Field
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.routes import ledger as ledger_routes
from shruti.api.routes.ledger import _In, _my_ledger, _plan
from shruti.api.routes.practice import _refuse_if_suspended
from shruti.models import OverlayToken
from shruti.models.ledger import Ledger, LedgerBusiness, LedgerWeek

router = APIRouter(prefix="/api/ledger", tags=["ledger"])

# The five elements of README §3, then the plan on stream (A1).
LEDGER_KINDS = ("ledger-plate", "ledger-card", "ledger-strip", "ledger-limit", "ledger-counter")
PLAN_KINDS = ("ledger-plan-panel", "ledger-plan-card")
ALL_KINDS = LEDGER_KINDS + PLAN_KINDS

# A game's own theme, over the fallback. Big Ambitions wore Plain until the
# Ledger theme existed (README §8: "Big Ambitions maps to ledger").
GAME_THEMES = {"big-ambitions": "ledger"}

# The written lines a week's total takes away from money in.
OUT_LINES = ("goods", "wages", "rent", "ads", "deliveries")

# The keys of a plan the engine reads (docs/LEDGER.md, Contract 2 and its
# additions). A stored plan is checked for shape, not content, so anything
# else in it (a note the planner kept, a figure somebody typed) stays home.
PLAN_KEYS = ("typeId", "buildingId", "prices", "fixtures", "hours", "campaigns", "satisfaction",
             "satisfactionTyped", "demand", "competitorPrice", "products", "displays", "staff")

CHANGE_CHARS = 160
DELTA_LIMIT = 1e13

# Where each element sits when nobody has moved it (1920 × 1080).
DEFAULT_PLACES = {
    "ledger-plate": {"x": 1112, "y": 48, "w": 760},
    "ledger-card": {"x": 72, "y": 72, "w": 900},
    "ledger-strip": {"x": 72, "y": 904, "w": 1776},
    "ledger-limit": {"x": 72, "y": 858, "w": 1100},
    "ledger-counter": {"x": 1416, "y": 300, "w": 432},
    "ledger-plan-panel": {"x": 1112, "y": 48, "w": 760},
    "ledger-plan-card": {"x": 72, "y": 72, "w": 900},
}
SHOWS = ("", "top")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(when: datetime | None) -> str | None:
    return when.isoformat() if when else None


# ── a week, as chat may see it ──────────────────────────────────────────────

def week_total(w: LedgerWeek) -> float | None:
    """Money in minus the lines written. ⚠ An unwritten line is left out, not read as zero."""
    if w.money_in is None:
        return None
    total = w.money_in
    for line in OUT_LINES:
        value = getattr(w, line)
        if value is not None:
            total -= value
    return total


def company_week(rows: list[dict]) -> dict | None:
    """
    The company's latest week: the highest week any open business has written,
    and the sum of that week's totals over the businesses that wrote it. A
    business whose latest week is older is not in the sum and is not a gap.
    """
    written = [r for r in rows if r.get("week") is not None]
    if not written:
        return None
    n = max(r["week"] for r in written)
    totals = [r["total"] for r in written if r["week"] == n and r["total"] is not None]
    return {"n": n, "total": sum(totals) if totals else None}


# ── the neighbourhood of a business, from the pack ──────────────────────────

_where_cache: dict[str, Any] = {"key": None, "buildings": {}}


def _where() -> dict[str, str]:
    """buildingId → neighbourhood name, read again only when the pack changes."""
    found = ledger_routes._pack()
    if found is None:
        return {}
    key = ledger_routes._pack_cache.get("key")
    if _where_cache["key"] != key:
        try:
            pack = json.loads(found[0])
            hoods = {h.get("id"): h.get("name", "") for h in pack.get("neighbourhoods") or [] if isinstance(h, dict)}
            _where_cache["buildings"] = {
                b.get("id"): hoods.get(b.get("neighbourhood"), "")
                for b in pack.get("buildings") or [] if isinstance(b, dict)}
        except (ValueError, AttributeError):
            _where_cache["buildings"] = {}
        _where_cache["key"] = key
    return _where_cache["buildings"]


def _game() -> dict:
    found = ledger_routes._pack()
    return found[1] if found else {}


def _plan_of(b: LedgerBusiness) -> dict:
    """The plan a business was opened on: the kept one, or the working one when nothing was kept."""
    return b.kept_plan if b.kept_plan is not None else (b.plan or {})


def engine_plan(plan: Any) -> dict:
    """Only what the engine reckons with. ⚠ Everything else a plan holds stays off stream."""
    return {k: plan[k] for k in PLAN_KEYS if isinstance(plan, dict) and k in plan}


# ── the frame ───────────────────────────────────────────────────────────────

def stamp(g: Ledger, kind: str) -> str:
    """
    What changes when the frame would. A week written, a business opened or
    renamed, the ledger renamed: `updated_at`. The business on screen: its id.
    The plan kinds: the live plan's clock and nothing else.
    """
    if kind in PLAN_KINDS:
        return f"p{g.id}@{_iso(g.live_updated_at) or ''}"
    return f"l{g.id}@{_iso(g.updated_at) or ''}:{g.on_screen_business_id if g.on_screen_business_id is not None else ''}"


async def frame(session: AsyncSession, g: Ledger, kind: str) -> dict:
    """
    What one element of this ledger draws. See the module's note: this is
    everything chat can learn, so every key here is one somebody chose.
    """
    game = _game()
    base = {
        "kind": kind,
        "company": g.name,
        "game": {"version": g.version or str(game.get("version") or ""), "build": str(game.get("build") or "")},
        "ctx": {"difficulty": g.difficulty, "courses": list(g.courses or []), "custom": g.custom},
    }
    if kind in PLAN_KINDS:
        live = g.live_plan if isinstance(g.live_plan, dict) else None
        if not live or not isinstance(live.get("plan"), dict):
            return {**base, "company": "", "live": None}
        change = g.live_change if isinstance(g.live_change, dict) else None
        return {**base, "company": "", "live": {
            "plan": engine_plan(live["plan"]), "name": str(live.get("name") or ""),
            "change": ({"label": str(change.get("label") or ""), "delta": change.get("delta")} if change else None),
            "updatedAt": _iso(g.live_updated_at)}}

    businesses = (await session.execute(
        select(LedgerBusiness).where(LedgerBusiness.ledger_id == g.id, LedgerBusiness.opened_at.is_not(None))
        .order_by(LedgerBusiness.position, LedgerBusiness.id)
    )).scalars().all()
    ids = [b.id for b in businesses]
    latest: dict[int, LedgerWeek] = {}
    if ids:
        top = (select(LedgerWeek.business_id, func.max(LedgerWeek.n).label("n"))
               .where(LedgerWeek.business_id.in_(ids)).group_by(LedgerWeek.business_id).subquery())
        rows = (await session.execute(
            select(LedgerWeek).join(top, and_(LedgerWeek.business_id == top.c.business_id, LedgerWeek.n == top.c.n))
        )).scalars().all()
        latest = {w.business_id: w for w in rows}
    where = _where()
    out = []
    for b in businesses:
        w = latest.get(b.id)
        out.append({"id": b.id, "name": b.name,
                    "neighbourhood": where.get(str(_plan_of(b).get("buildingId") or ""), ""),
                    "week": w.n if w else None, "total": week_total(w) if w else None})
    # The business on screen: the one chosen if it is still open, else the first in the ledger's order.
    on = g.on_screen_business_id if g.on_screen_business_id in ids else (ids[0] if ids else None)
    on_plan = next((engine_plan(_plan_of(b)) for b in businesses if b.id == on), None)
    return {**base, "businesses": out, "week": company_week(out), "onScreen": on, "onScreenPlan": on_plan}


async def token_frame(session: AsyncSession, token: OverlayToken, base: dict, v: str) -> dict:
    """
    The answer to `/api/overlay/guide?t=` for a ledger kind. The cheap path
    first: the source already shows this version, so nothing but the ledger's
    row is read.
    """
    g = await session.get(Ledger, token.ledger_id) if token.ledger_id else None
    if g is None:
        return base
    shows = next((str(e.get("shows") or "") for e in (token.layout or []) if isinstance(e, dict)), "")
    base["shows"] = shows if shows in SHOWS else ""
    base["version"] = stamp(g, token.kind)
    if v and v.replace(" ", "+") == base["version"]:
        return {"kind": token.kind, "theme": base["theme"], "motion": base["motion"], "version": base["version"],
                "unchanged": True}
    base["element"] = await frame(session, g, token.kind)
    return base


# ── a layout's ledger elements ──────────────────────────────────────────────

def clean_element(e: dict) -> dict:
    """A ledger element of a layout as stored: its place, which edge (the strip), and which ledger."""
    place = DEFAULT_PLACES[e["kind"]]

    def num(key: str, default: float, lo: float, hi: float) -> int:
        try:
            value = float(e.get(key, default))
        except (TypeError, ValueError):
            value = default
        return int(min(hi, max(lo, value)))
    shows = str(e.get("shows") or "")
    return {"kind": e["kind"], "x": num("x", place["x"], 0, 1920), "y": num("y", place["y"], 0, 1080),
            "w": num("w", place["w"], 120, 1920), "shows": shows if shows in SHOWS else "",
            "ledger_id": num("ledger_id", 0, 0, 10**9)}


def edge_of(e: dict) -> str:
    """Which edge a full-width strip sits on: the top half of the canvas is the top."""
    return "top" if int(e.get("y", 0)) < 540 else "bottom"


def strip_collision(layout: list[dict]) -> str | None:
    """
    README §2.5: a company strip and a path strip never share an edge. The
    sentence the editor shows, or None when they do not collide.
    """
    strips = {edge_of(e) for e in layout if e.get("kind") == "ledger-strip"}
    paths = {edge_of(e) for e in layout if e.get("kind") == "guide-path"}
    if strips & paths:
        return "A company strip and a path strip cannot share an edge. Put the strip on the edge the path strip leaves free."
    return None


async def layout_stamp(session: AsyncSession, elements: list[dict]) -> str:
    ids = sorted({int(e["ledger_id"]) for e in elements if e.get("kind") in ALL_KINDS and e.get("ledger_id")})
    if not ids:
        return ""
    rows = (await session.execute(select(Ledger).where(Ledger.id.in_(ids)))).scalars().all()
    kinds = {e.get("kind") for e in elements}
    return ":L" + ",".join(stamp(g, k) for g in rows for k in sorted(kinds & set(ALL_KINDS)))


async def fill_element(session: AsyncSession, e: dict, owner_id: int | None) -> dict:
    """A layout's ledger element: drawn only when the layout's owner owns that ledger."""
    g = await session.get(Ledger, int(e["ledger_id"])) if e.get("ledger_id") else None
    if g is None or owner_id is None or g.user_id != owner_id:
        return {}
    return await frame(session, g, e["kind"])


# ── the routes: overlays of a ledger ────────────────────────────────────────

class LedgerTokenIn(_In):
    kind: str
    theme: str = ""
    motion: str = "reduced"
    label: str = Field(default="", max_length=400)
    # The company strip only: "" (the bottom edge) or "top".
    shows: str = ""


def _token_view(o: OverlayToken) -> dict:
    shows = next((str(e.get("shows") or "") for e in (o.layout or []) if isinstance(e, dict)), "")
    return {"id": o.id, "kind": o.kind, "label": o.label, "theme": o.theme, "motion": o.motion, "shows": shows,
            "createdAt": _iso(o.created_at), "lastSeen": _iso(o.last_seen)}


@router.get("/ledgers/{ledger_id}/overlays")
async def ledger_tokens(ledger_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """This ledger's overlays by kind, theme and motion, WITHOUT their tokens (README §6: never by address)."""
    g, _ = await _my_ledger(session, request, ledger_id)
    rows = (await session.execute(
        select(OverlayToken).where(OverlayToken.ledger_id == g.id).order_by(OverlayToken.id))).scalars().all()
    return [_token_view(o) for o in rows]


@router.post("/ledgers/{ledger_id}/overlays", status_code=201)
async def mint_ledger_token(ledger_id: int, body: LedgerTokenIn, request: Request,
                            session: AsyncSession = Depends(get_session)) -> dict:
    """
    Mint one overlay of this ledger and return its token **once**. The same
    fair use as every overlay; never a charge. The theme defaults to the
    game's own (Ledger for Big Ambitions).
    """
    from shruti.api.routes.overlay_guides import MOTIONS, THEMES, refuse_if_out_of_allowance
    g, user = await _my_ledger(session, request, ledger_id)
    if body.kind not in ALL_KINDS:
        raise HTTPException(422, "kind is one of " + ", ".join(ALL_KINDS))
    await _refuse_if_suspended(session, user)
    await refuse_if_out_of_allowance(session, user)
    token = secrets.token_urlsafe(24)
    theme = body.theme if body.theme in THEMES else GAME_THEMES.get(g.game, "almanac")
    shows = body.shows if body.kind == "ledger-strip" and body.shows in SHOWS else ""
    row = OverlayToken(token=token, kind=body.kind, label=body.label.strip()[:80] or g.name, user_id=user.id,
                       ledger_id=g.id, theme=theme, motion=body.motion if body.motion in MOTIONS else "reduced",
                       layout=[{"kind": body.kind, "shows": shows}] if shows else [])
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {**_token_view(row), "token": token, "path": f"/overlay/ledger?t={token}"}


@router.delete("/ledgers/{ledger_id}/overlays/{token_id}", status_code=204)
async def revoke_ledger_token(ledger_id: int, token_id: int, request: Request,
                              session: AsyncSession = Depends(get_session)) -> None:
    """A delete, not a flag: OBS stops showing it at the next poll."""
    g, _ = await _my_ledger(session, request, ledger_id)
    row = (await session.execute(
        select(OverlayToken).where(OverlayToken.id == token_id, OverlayToken.ledger_id == g.id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such overlay")
    await session.delete(row)
    await session.commit()


# ── the business on screen ──────────────────────────────────────────────────

class OnScreenIn(_In):
    business_id: int | None = None


@router.put("/ledgers/{ledger_id}/on-screen")
async def set_on_screen(ledger_id: int, body: OnScreenIn, request: Request,
                        session: AsyncSession = Depends(get_session)) -> dict:
    """
    The one-tap switch (README §6): every minted element of this ledger
    redraws at its next poll. Only an open business of this ledger; null
    clears it (the first open business is then on screen).
    """
    g, _ = await _my_ledger(session, request, ledger_id)
    if body.business_id is not None:
        b = await session.get(LedgerBusiness, body.business_id)
        if b is None or b.ledger_id != g.id:
            raise HTTPException(404, "no such business in this ledger")
        if b.opened_at is None:
            raise HTTPException(422, "only an open business can be on screen; a plan that was never opened stays off stream")
    g.on_screen_business_id = body.business_id
    g.updated_at = _now()
    await session.commit()
    return {"onScreenBusinessId": g.on_screen_business_id}


# ── the plan on stream ──────────────────────────────────────────────────────

class ChangeIn(_In):
    label: str = Field(default="", max_length=CHANGE_CHARS)
    delta: float | None = None


class LiveIn(_In):
    plan: Any = None
    name: str = Field(default="", max_length=400)
    # The planner's own diff of the tap, and its own reckoning of what it did
    # to the week. Absent when the plan is new on stream: no change line.
    change: ChangeIn | None = None


@router.put("/ledgers/{ledger_id}/live")
async def put_live(ledger_id: int, body: LiveIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    The planner's *Plan on stream* switch, on: the plan as it stands now,
    overwriting whatever was live. One plan per ledger. The plan is checked
    for shape and size, never recomputed: the overlay reckons it with the
    planner's engine.
    """
    g, _ = await _my_ledger(session, request, ledger_id)
    plan = _plan(body.plan)
    change = None
    if body.change is not None:
        delta = body.change.delta
        if delta is not None and not (abs(delta) <= DELTA_LIMIT):
            raise HTTPException(422, "a change's delta is a finite number of dollars")
        change = {"label": body.change.label.strip()[:CHANGE_CHARS], "delta": delta}
    g.live_plan = {"plan": plan, "name": body.name.strip()[:80]}
    g.live_change = change
    g.live_updated_at = _now()
    await session.commit()
    return {"live": True, "updatedAt": _iso(g.live_updated_at)}


@router.delete("/ledgers/{ledger_id}/live", status_code=204)
async def drop_live(ledger_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """The switch off: the plan is gone, not hidden, and the overlay draws its empty frame at the next poll."""
    g, _ = await _my_ledger(session, request, ledger_id)
    g.live_plan = None
    g.live_change = None
    g.live_updated_at = _now()
    await session.commit()
