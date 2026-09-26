# SPDX-License-Identifier: AGPL-3.0-only
"""
The Ledger: a Big Ambitions business planner and account book (docs/LEDGER.md,
Contract 3).

The reckoning runs in the browser, so these routes keep rows and check who is
asking. They store a plan as the person left it and never recompute it: a
plan is checked for shape and size, not for sense, because what it comes to is
the engine's business and the engine is not here.

⚠ **Anybody else's ledger is 404, never 403.** A 403 would say the id exists.

⚠ **A null line was not written.** Every week line arrives, is stored and
leaves as null when it was not given. Nothing here reads a null as 0, and
nothing sums a week: that is how an unknown wage becomes a profit.

⚠ **Free and ungated.** No tier, no allowance, no publishing agreement:
nothing in a ledger is public, and a planner that stops at a paywall is not
one. The data route reads no session at all — planning works signed out.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.routes import gamedata
from shruti.api.routes.practice import _reader, _refuse_if_suspended
from shruti.models.ledger import Ledger, LedgerBusiness, LedgerWeek

router = APIRouter(prefix="/api/ledger", tags=["ledger"])

DATA_FILE = "ledger-big-ambitions.json"
NOT_LOADED = "the game's data is not loaded yet"

PLAN_BYTES = 64 * 1024
CUSTOM_BYTES = 4 * 1024
NAME_CHARS = 80
NOTE_CHARS = 500
MAX_WEEK = 9999
MAX_ROWS = 200
MAX_COURSES = 64
MONEY_LIMIT = 1e13          # past a trillion dollars a figure is a typo, not a week
COUNT_LIMIT = 1_000_000_000

MONEY_LINES = ("money_in", "goods", "wages", "rent", "ads", "deliveries")
COUNT_LINES = ("units", "customers")
LINES = MONEY_LINES + COUNT_LINES


# ── the data pack ───────────────────────────────────────────────────────────
#
# One JSON file in the gamedata volume, put there by scripts/sync-gamedata.sh.
# Its absence is a working state: the Ledger says so and planning waits.

_pack_cache: dict[str, Any] = {"key": None, "body": None, "game": None}


def _pack() -> tuple[bytes, dict] | None:
    """The file's bytes and its `game` block, read again only when the file changes."""
    path = gamedata.GAMEDATA_DIR / DATA_FILE      # read at call time, so a test can point it elsewhere
    try:
        stat = path.stat()
        key = (str(path), stat.st_mtime_ns, stat.st_size)
        if _pack_cache["key"] != key:
            body = path.read_bytes()
            parsed = json.loads(body)
            if not isinstance(parsed, dict):
                return None
            _pack_cache.update(key=key, body=body, game=parsed.get("game") or {})
        return _pack_cache["body"], _pack_cache["game"]
    except (OSError, ValueError):
        return None


@router.get("/data")
def data() -> Response:
    """The game's facts, as the engine reads them. No session is read: planning needs no account."""
    found = _pack()
    if found is None:
        raise HTTPException(404, NOT_LOADED)
    return Response(content=found[0], media_type="application/json")


# ── checking what arrives ───────────────────────────────────────────────────

def _money(value: Any) -> float | None:
    """A finite number or null. ⚠ Not a bool, not a string: `true` is not a dollar."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("a line is a number, or null when it was not written")
    if not math.isfinite(value) or abs(value) > MONEY_LIMIT:
        raise ValueError("a line must be a finite number")
    return float(value)


def _count(value: Any) -> int | None:
    """A whole number of units or customers, or null."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("a count is a whole number, or null when it was not written")
    if not math.isfinite(value) or value != int(value) or not 0 <= value <= COUNT_LIMIT:
        raise ValueError("a count is a whole number, zero or more")
    return int(value)


Money = Annotated[float | None, BeforeValidator(_money)]
Count = Annotated[int | None, BeforeValidator(_count)]


def _name(value: str | None, what: str) -> str:
    name = (value or "").strip()
    if not name:
        raise HTTPException(422, f"a {what} needs a name")
    if len(name) > NAME_CHARS:
        raise HTTPException(422, f"a {what}'s name is {NAME_CHARS} characters at most")
    return name


def _json_size(value: Any, limit: int, what: str) -> None:
    try:
        size = len(json.dumps(value, allow_nan=False, separators=(",", ":")).encode())
    except ValueError:
        raise HTTPException(422, f"the {what} holds a number that is not finite")
    if size > limit:
        raise HTTPException(413, f"the {what} is {size // 1024} KB; {limit // 1024} KB is the most kept")


def _plan(value: Any, what: str = "plan") -> dict:
    """
    A plan's shape, loosely: an object, 64 KB at most, and the hours grid
    right if it is there. ⚠ Not recomputed and not checked against the game's
    data — a plan made against an older pack must still load.
    """
    if not isinstance(value, dict):
        raise HTTPException(422, f"a {what} is an object")
    _json_size(value, PLAN_BYTES, what)
    if "hours" in value and value["hours"] is not None:
        hours = value["hours"]
        ok = (isinstance(hours, list) and len(hours) == 7
              and all(isinstance(day, list) and len(day) == 24
                      and all(isinstance(h, int) and not isinstance(h, bool) and 0 <= h <= 9 for h in day)
                      for day in hours))
        if not ok:
            raise HTTPException(422, "a plan's hours are seven days of 24 hours, each 0 to 9 registers")
    return value


def _custom(value: Any) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise HTTPException(422, "a custom difficulty is an object of values")
    _json_size(value, CUSTOM_BYTES, "custom difficulty")
    return value


def _difficulty(value: str | None) -> str:
    d = (value or "").strip().lower()
    if not d or len(d) > 40 or not all(c.isalnum() or c == "-" for c in d):
        raise HTTPException(422, "a difficulty is its id from the game's data, like normal or custom")
    return d


def _courses(value: list | None) -> list[str]:
    courses = value or []
    if len(courses) > MAX_COURSES or not all(isinstance(c, str) and 0 < len(c) <= 80 for c in courses):
        raise HTTPException(422, "courses are the ids of the courses taken")
    return list(dict.fromkeys(courses))


class _In(BaseModel):
    """camelCase on the wire, like every other route; snake_case accepted too."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ── views ───────────────────────────────────────────────────────────────────

def _iso(when: datetime | None) -> str | None:
    return when.isoformat() if when else None


def _ledger_view(g: Ledger) -> dict:
    return {"id": g.id, "name": g.name, "game": g.game, "version": g.version,
            "difficulty": g.difficulty, "custom": g.custom, "inGameDay": g.in_game_day,
            "courses": g.courses or [], "position": g.position,
            "createdAt": _iso(g.created_at), "updatedAt": _iso(g.updated_at)}


def _week_view(w: LedgerWeek) -> dict:
    """⚠ Every line as stored: a null stays null on the way out."""
    return {"n": w.n, "moneyIn": w.money_in, "goods": w.goods, "wages": w.wages, "rent": w.rent,
            "ads": w.ads, "deliveries": w.deliveries, "units": w.units, "customers": w.customers,
            "note": w.note, "updatedAt": _iso(w.updated_at)}


def _business_view(b: LedgerBusiness, weeks: list[LedgerWeek]) -> dict:
    return {"id": b.id, "ledgerId": b.ledger_id, "name": b.name, "plan": b.plan or {},
            "keptPlan": b.kept_plan, "opened": b.opened_at is not None, "openedAt": _iso(b.opened_at),
            "position": b.position, "weeks": [_week_view(w) for w in sorted(weeks, key=lambda w: w.n)],
            "createdAt": _iso(b.created_at), "updatedAt": _iso(b.updated_at)}


async def _weeks_of(session: AsyncSession, business_ids: list[int]) -> dict[int, list[LedgerWeek]]:
    out: dict[int, list[LedgerWeek]] = {i: [] for i in business_ids}
    if business_ids:
        rows = (await session.execute(
            select(LedgerWeek).where(LedgerWeek.business_id.in_(business_ids)).order_by(LedgerWeek.n)
        )).scalars().all()
        for w in rows:
            out[w.business_id].append(w)
    return out


async def _full_view(session: AsyncSession, g: Ledger) -> dict:
    businesses = (await session.execute(
        select(LedgerBusiness).where(LedgerBusiness.ledger_id == g.id)
        .order_by(LedgerBusiness.position, LedgerBusiness.id)
    )).scalars().all()
    weeks = await _weeks_of(session, [b.id for b in businesses])
    return {**_ledger_view(g), "businesses": [_business_view(b, weeks[b.id]) for b in businesses]}


# ── whose it is ─────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _my_ledger(session: AsyncSession, request: Request, ledger_id: int) -> tuple[Ledger, object]:
    user = await _reader(request, session)
    g = await session.get(Ledger, ledger_id)
    if g is None or g.user_id != user.id:
        raise HTTPException(404, "no such ledger")
    return g, user


async def _my_business(session: AsyncSession, request: Request, business_id: int) -> tuple[LedgerBusiness, Ledger]:
    user = await _reader(request, session)
    b = await session.get(LedgerBusiness, business_id)
    g = await session.get(Ledger, b.ledger_id) if b is not None else None
    if b is None or g is None or g.user_id != user.id:
        raise HTTPException(404, "no such business")
    return b, g


# ── ledgers ─────────────────────────────────────────────────────────────────

class LedgerIn(_In):
    name: str = Field(default="", max_length=400)
    difficulty: str = "normal"
    custom: dict | None = None
    in_game_day: int | None = Field(default=None, ge=0, le=1_000_000)
    courses: list = Field(default_factory=list)
    version: str | None = Field(default=None, max_length=40)


class LedgerPatch(_In):
    """Absent fields are left as they are; `inGameDay` and `custom` may be set to null."""
    name: str | None = Field(default=None, max_length=400)
    difficulty: str | None = None
    custom: dict | None = None
    in_game_day: int | None = Field(default=None, ge=0, le=1_000_000)
    courses: list | None = None
    version: str | None = Field(default=None, max_length=40)
    position: int | None = Field(default=None, ge=0, le=9999)


@router.get("/ledgers")
async def my_ledgers(request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The reader's ledgers, each with how many businesses it holds — not their weeks."""
    user = await _reader(request, session)
    rows = (await session.execute(
        select(Ledger).where(Ledger.user_id == user.id).order_by(Ledger.position, Ledger.id)
    )).scalars().all()
    counts = dict((await session.execute(
        select(LedgerBusiness.ledger_id, func.count()).where(LedgerBusiness.ledger_id.in_([g.id for g in rows]))
        .group_by(LedgerBusiness.ledger_id)
    )).all()) if rows else {}
    return [{**_ledger_view(g), "businesses": int(counts.get(g.id, 0))} for g in rows]


@router.post("/ledgers", status_code=201)
async def start_ledger(body: LedgerIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Start a ledger. With no version given, it takes the loaded pack's, so the
    ledger remembers which patch its figures were read against.
    """
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    version = (body.version or "").strip()
    if not version:
        found = _pack()
        version = str((found[1] if found else {}).get("version") or "")
    last = (await session.execute(select(func.max(Ledger.position)).where(Ledger.user_id == user.id))).scalar()
    g = Ledger(user_id=user.id, name=_name(body.name, "ledger"), difficulty=_difficulty(body.difficulty),
               custom=_custom(body.custom), in_game_day=body.in_game_day, courses=_courses(body.courses),
               version=version[:40], position=(last + 1) if last is not None else 0)
    session.add(g)
    await session.commit()
    await session.refresh(g)
    return await _full_view(session, g)


@router.get("/ledgers/{ledger_id}")
async def one_ledger(ledger_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """One ledger, with its businesses and every week they ran."""
    g, _ = await _my_ledger(session, request, ledger_id)
    return await _full_view(session, g)


@router.put("/ledgers/{ledger_id}")
async def change_ledger(ledger_id: int, body: LedgerPatch, request: Request,
                        session: AsyncSession = Depends(get_session)) -> dict:
    g, _ = await _my_ledger(session, request, ledger_id)
    given = body.model_fields_set
    if body.name is not None:
        g.name = _name(body.name, "ledger")
    if body.difficulty is not None:
        g.difficulty = _difficulty(body.difficulty)
    if "custom" in given:
        g.custom = _custom(body.custom)
    if "in_game_day" in given:
        g.in_game_day = body.in_game_day
    if body.courses is not None:
        g.courses = _courses(body.courses)
    if body.version is not None:
        g.version = body.version.strip()
    if body.position is not None:
        g.position = body.position
    g.updated_at = _now()
    await session.commit()
    await session.refresh(g)
    return await _full_view(session, g)


@router.delete("/ledgers/{ledger_id}", status_code=204)
async def delete_ledger(ledger_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """The ledger, its businesses and their weeks — the last two by ON DELETE CASCADE."""
    g, _ = await _my_ledger(session, request, ledger_id)
    await session.delete(g)
    await session.commit()


# ── businesses ──────────────────────────────────────────────────────────────

class BusinessIn(_In):
    name: str = Field(default="", max_length=400)
    plan: Any = Field(default_factory=dict)


class BusinessPatch(_In):
    """Absent fields are left as they are. `keptPlan` may be set to null."""
    name: str | None = Field(default=None, max_length=400)
    plan: Any = None
    kept_plan: Any = None
    opened: bool | None = None
    position: int | None = Field(default=None, ge=0, le=9999)


@router.post("/ledgers/{ledger_id}/businesses", status_code=201)
async def keep_plan(ledger_id: int, body: BusinessIn, request: Request,
                    session: AsyncSession = Depends(get_session)) -> dict:
    """
    Keep a plan in a ledger. It is kept twice on purpose: `plan` is where it
    goes from here, `keptPlan` is what it was when kept.
    """
    g, user = await _my_ledger(session, request, ledger_id)
    await _refuse_if_suspended(session, user)
    plan = _plan(body.plan)
    last = (await session.execute(
        select(func.max(LedgerBusiness.position)).where(LedgerBusiness.ledger_id == g.id))).scalar()
    b = LedgerBusiness(ledger_id=g.id, name=_name(body.name, "business"), plan=plan, kept_plan=json.loads(json.dumps(plan)),
                       position=(last + 1) if last is not None else 0)
    session.add(b)
    g.updated_at = _now()
    await session.commit()
    await session.refresh(b)
    return _business_view(b, [])


@router.get("/businesses/{business_id}")
async def one_business(business_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    b, _ = await _my_business(session, request, business_id)
    return _business_view(b, (await _weeks_of(session, [b.id]))[b.id])


@router.put("/businesses/{business_id}")
async def change_business(business_id: int, body: BusinessPatch, request: Request,
                          session: AsyncSession = Depends(get_session)) -> dict:
    b, g = await _my_business(session, request, business_id)
    given = body.model_fields_set
    if body.name is not None:
        b.name = _name(body.name, "business")
    if "plan" in given:
        if body.plan is None:
            raise HTTPException(422, "a business always has a plan; send {} for an empty one")
        b.plan = _plan(body.plan)
    if "kept_plan" in given:
        b.kept_plan = None if body.kept_plan is None else _plan(body.kept_plan, "kept plan")
    if body.opened is not None:
        # Opening twice keeps the first date: the day it opened does not move.
        b.opened_at = (b.opened_at or _now()) if body.opened else None
    if body.position is not None:
        b.position = body.position
    b.updated_at = g.updated_at = _now()
    await session.commit()
    await session.refresh(b)
    return _business_view(b, (await _weeks_of(session, [b.id]))[b.id])


@router.delete("/businesses/{business_id}", status_code=204)
async def delete_business(business_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """The business and its weeks, the weeks by ON DELETE CASCADE."""
    b, g = await _my_business(session, request, business_id)
    await session.delete(b)
    g.updated_at = _now()
    await session.commit()


# ── weeks ───────────────────────────────────────────────────────────────────

class WeekLines(_In):
    """
    One week's lines. ⚠ Absent and null are the same thing — not written —
    and a week is written whole: a line left out of a rewrite is unwritten.
    """
    money_in: Money = None
    goods: Money = None
    wages: Money = None
    rent: Money = None
    ads: Money = None
    deliveries: Money = None
    units: Count = None
    customers: Count = None
    note: str | None = Field(default=None, max_length=NOTE_CHARS)


class EntryRow(WeekLines):
    business_id: int


class EntryGridIn(_In):
    rows: list[EntryRow] = Field(default_factory=list, max_length=MAX_ROWS)


WeekN = Annotated[int, Path(ge=1, le=MAX_WEEK)]


async def _write_week(session: AsyncSession, business_id: int, n: int, lines: WeekLines) -> LedgerWeek:
    """Write one week whole, over whatever was there. Lines not given are null."""
    w = (await session.execute(
        select(LedgerWeek).where(LedgerWeek.business_id == business_id, LedgerWeek.n == n)
    )).scalar_one_or_none()
    if w is None:
        w = LedgerWeek(business_id=business_id, n=n)
        session.add(w)
    for line in LINES:
        setattr(w, line, getattr(lines, line))
    w.note = (lines.note or "").strip()
    w.updated_at = _now()
    return w


@router.put("/businesses/{business_id}/weeks/{n}")
async def write_week(business_id: int, n: WeekN, body: WeekLines, request: Request,
                     session: AsyncSession = Depends(get_session)) -> dict:
    """Write one week. Money in is the one line a week cannot be without."""
    b, g = await _my_business(session, request, business_id)
    if body.money_in is None:
        raise HTTPException(422, "a week needs its money in; the other lines may wait")
    w = await _write_week(session, b.id, n, body)
    b.updated_at = g.updated_at = _now()
    await session.commit()
    await session.refresh(w)
    return _week_view(w)


@router.delete("/businesses/{business_id}/weeks/{n}", status_code=204)
async def remove_week(business_id: int, n: WeekN, request: Request,
                      session: AsyncSession = Depends(get_session)) -> None:
    b, g = await _my_business(session, request, business_id)
    w = (await session.execute(
        select(LedgerWeek).where(LedgerWeek.business_id == b.id, LedgerWeek.n == n)
    )).scalar_one_or_none()
    if w is None:
        raise HTTPException(404, "no such week")
    await session.delete(w)
    b.updated_at = g.updated_at = _now()
    await session.commit()


@router.post("/ledgers/{ledger_id}/weeks/{n}")
async def entry_grid(ledger_id: int, n: WeekN, body: EntryGridIn, request: Request,
                     session: AsyncSession = Depends(get_session)) -> dict:
    """
    One week for several businesses at once. A row with no money in is
    skipped, not refused: an empty row in the grid is a business that did not
    trade that week, or one not got to yet. The answer says which were
    written and which were skipped, so the page can say so too.

    ⚠ A row for a business outside this ledger refuses the whole grid, before
    anything is written — a half-written week is worse than none.
    """
    g, _ = await _my_ledger(session, request, ledger_id)
    mine = set((await session.execute(
        select(LedgerBusiness.id).where(LedgerBusiness.ledger_id == g.id))).scalars().all())
    strangers = [r.business_id for r in body.rows if r.business_id not in mine]
    if strangers:
        raise HTTPException(404, "no such business in this ledger")
    written, skipped = [], []
    for row in body.rows:
        if row.money_in is None:
            skipped.append(row.business_id)
            continue
        await _write_week(session, row.business_id, n, row)
        written.append(row.business_id)
    if written:
        stamp = _now()
        for b in (await session.execute(
                select(LedgerBusiness).where(LedgerBusiness.id.in_(written)))).scalars().all():
            b.updated_at = stamp
        g.updated_at = stamp
    await session.commit()
    await session.refresh(g)
    return {"n": n, "written": written, "skipped": skipped, "ledger": await _full_view(session, g)}

