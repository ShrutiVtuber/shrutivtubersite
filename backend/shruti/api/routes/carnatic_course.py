# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio v2: the course (read and offline), a learner's progress,
attempts, bests and review cards, and the Listening room's recordings,
guesses and suggestions. The contract is docs/carnatic/API.md §10-§14.

Reading never needs an account. Everything a learner keeps is theirs alone
and is never shown to anyone else. No streaks, no pass marks, no red: the
only scale anywhere is new · getting there · comfortable.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.routes.accounts import current_user, require_user
from shruti.core import carnatic as rules
from shruti.core import carnatic_course as course
from shruti.core import carnatic_drills as drills
from shruti.core.db import get_session
from shruti.models.accounts import User
from shruti.models.carnatic_course import (
    CarnaticAttempt, CarnaticBest, CarnaticCard, CarnaticExercise, CarnaticGlossary, CarnaticGuess,
    CarnaticLesson, CarnaticLessonState, CarnaticRagaFlag, CarnaticRecording, CarnaticUnit,
)

router = APIRouter(prefix="/api/carnatic", tags=["carnatic-course"])

LEVEL_LABEL = {"foundations": "Foundations", "intermediate": "Intermediate", "advanced": "Advanced",
               "any time": "Any time"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, f"not a time: {value}")
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def is_operator(request: Request, session: AsyncSession) -> bool:
    """The operator previewing drafts on the website. Never raises."""
    from shruti.api.deps import require_admin
    try:
        await require_admin(request, session)
        return True
    except HTTPException:
        return False


# ── the course ──────────────────────────────────────────────────────────────

async def _published(session: AsyncSession, preview: bool, lang: str = "en") -> list[CarnaticLesson]:
    q = select(CarnaticLesson).where(CarnaticLesson.lang == lang)
    if not preview:
        q = q.where(CarnaticLesson.status == "published")
    return list((await session.execute(q.order_by(CarnaticLesson.unit, CarnaticLesson.order))).scalars().all())


async def _approved_ids(session: AsyncSession) -> set[str]:
    rows = (await session.execute(select(CarnaticRecording.id).where(CarnaticRecording.status == "approved"))).all()
    return {r[0] for r in rows}


def lesson_json(row: CarnaticLesson, approved: set[str], *, with_body: bool = True) -> dict:
    f = row.front or {}
    order = course.footnote_order(row.body)
    sources = [s for s in (f.get("sources") or []) if isinstance(s, dict)]
    numbered = {k: i + 1 for i, k in enumerate(order)}
    extra = len(order)
    out_sources = []
    for s in sources:
        n = numbered.get(s.get("key"))
        if n is None:
            extra += 1
            n = extra
        out_sources.append({"key": s.get("key"), "n": n, "cite": s.get("cite", ""), "url": s.get("url"),
                            "research": s.get("research"), "confidence": s.get("confidence", "high")})
    out_sources.sort(key=lambda s: s["n"])
    out = {
        "id": row.id, "slug": row.slug, "lang": row.lang, "revision": row.revision, "status": row.status,
        "unit": row.unit, "order": row.order,
        "title": f.get("title", ""), "summary": f.get("summary", ""), "level": f.get("level", ""),
        "minutes": f.get("minutes", 0), "goals": f.get("goals") or [], "prerequisites": f.get("prerequisites") or [],
        "tools": f.get("tools") or [], "ragas": f.get("ragas") or [], "talas": f.get("talas") or [],
        "recordings": [{"id": r.get("id"), "why": r.get("why", ""), "available": r.get("id") in approved}
                       for r in (f.get("recordings") or []) if isinstance(r, dict)],
        "sources": out_sources, "exercises": f.get("exercises") or [],
        "updatedAt": _iso(row.updated_at), "translation": None,
    }
    if with_body:
        out["body"] = course.strip_notes(row.body)
        out["words"] = course.words(row.body)
    return out


async def units_json(session: AsyncSession, preview: bool) -> list[dict]:
    units = (await session.execute(select(CarnaticUnit).order_by(CarnaticUnit.n))).scalars().all()
    lessons = {l.id: l for l in await _published(session, preview)}
    ex_rows = (await session.execute(select(CarnaticExercise.id, CarnaticExercise.lesson, CarnaticExercise.kind,
                                            CarnaticExercise.data))).all()
    kinds: dict[str, set[str]] = {}
    checkpoints: dict[int, str] = {}
    for eid, lesson, kind, data in ex_rows:
        kinds.setdefault(lesson, set()).add(kind)
        if kind == "checkpoint":
            unit = int(eid[4:6]) if eid.startswith("CP.U") else 0
            if unit:
                checkpoints[unit] = eid
    approved = await _approved_ids(session)
    out = []
    for u in units:
        items = []
        recs: list[dict] = []
        quizzes = False
        for s in u.lessons or []:
            row = lessons.get(s["id"])
            f = row.front if row else {}
            tools = set(f.get("tools") or s.get("tools") or [])
            k = kinds.get(s["id"], set())
            quizzes = quizzes or "quiz" in k
            front_recs = f.get("recordings") or []
            for r in front_recs:
                rid = r.get("id") if isinstance(r, dict) else r
                if rid and all(x["id"] != rid for x in recs):
                    recs.append({"id": rid, "why": (r.get("why") if isinstance(r, dict) else "") or "",
                                 "lesson": s["id"], "available": rid in approved})
            items.append({
                "id": s["id"], "slug": (row.slug if row else s.get("slug")), "order": int(s["id"][-2:]),
                "title": f.get("title") or s.get("title"), "minutes": f.get("minutes") or s.get("minutes") or 0,
                "level": f.get("level") or s.get("level") or "", "available": row is not None,
                "status": row.status if row else "planned",
                "hasListening": "listening" in k or bool(front_recs) or bool(tools & {"recording", "listen"}),
                "hasPractice": "practice" in k,
                "after": s.get("after") or [],
            })
        out.append({"n": u.n, "title": u.title, "level": u.level, "levelLabel": LEVEL_LABEL.get(u.level, u.level),
                    "intro": u.intro, "lessons": items, "recordings": recs,
                    # A unit without its own CP.Unn set gets one assembled from its lesson quizzes.
                    "checkpoint": checkpoints.get(u.n) or (f"CP.U{u.n:02d}" if quizzes else None)})
    return out


async def _exercises(session: AsyncSession, preview: bool, *, unit: int | None = None,
                     lesson: str | None = None) -> list[dict]:
    q = select(CarnaticExercise)
    if unit is not None:
        q = q.where(CarnaticExercise.unit == unit)
    if lesson is not None:
        q = q.where(CarnaticExercise.lesson == lesson)
    rows = (await session.execute(q.order_by(CarnaticExercise.id))).scalars().all()
    if not preview:
        published = {l.id for l in await _published(session, False)}
        published_units = {int(i[1:3]) for i in published}
        rows = [r for r in rows if r.lesson in published or (r.kind == "checkpoint" and r.unit in published_units)]
    return [_ready({**r.data, "id": r.id, "unit": r.unit}) for r in rows]


def _waiting(item) -> bool:
    """An item whose answer waits for Sophia's annotation (`answer: null`, FORMAT.md §4a)."""
    return isinstance(item, dict) and "answer" in item and item["answer"] is None and not item.get("answer_from")


def _ready(ex: dict) -> dict:
    """Items waiting for an annotation are hidden until they have one."""
    for key in ("items", "auto"):
        if isinstance(ex.get(key), list):
            kept = [i for i in ex[key] if not _waiting(i)]
            if len(kept) != len(ex[key]):
                ex = {**ex, key: kept, "waiting": ex.get("waiting", 0) + len(ex[key]) - len(kept)}
    return ex


async def _flags(session: AsyncSession) -> dict[str, bool]:
    rows = (await session.execute(select(CarnaticRagaFlag))).scalars().all()
    return {r.raga: r.synth_ok for r in rows}


async def _glossary(session: AsyncSession) -> list[dict]:
    rows = (await session.execute(select(CarnaticGlossary).order_by(CarnaticGlossary.term))).scalars().all()
    return [{"term": g.term, "slug": g.slug, "definition": g.definition, "lesson": g.lesson,
             "forms": g.aliases or [], "aliases": g.aliases or [], "iso": g.iso, "source": g.source} for g in rows]


_version_cache: dict[str, tuple[float, dict]] = {}


async def _version(session: AsyncSession) -> dict:
    hit = _version_cache.get("v")
    if hit and time.monotonic() - hit[0] < 20:
        return hit[1]
    v = await course.course_version(session)
    _version_cache["v"] = (time.monotonic(), v)
    return v


def _etagged(request: Request, body: dict, etag: str, cache: str = "no-cache"):
    tag = f'"{etag}"'
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers={"ETag": tag, "Cache-Control": cache})
    return JSONResponse(body, headers={"ETag": tag, "Cache-Control": cache})


@router.get("/course/version")
async def course_version(request: Request, session: AsyncSession = Depends(get_session)):
    v = await _version(session)
    return _etagged(request, v, v["digest"])


@router.get("/course/units")
async def course_units(request: Request, preview: bool = False, session: AsyncSession = Depends(get_session)):
    preview = preview and await is_operator(request, session)
    return {"items": await units_json(session, preview)}


@router.get("/course/lessons")
async def course_lessons(raga: str | None = None, tala: str | None = None, recording: str | None = None,
                         session: AsyncSession = Depends(get_session)) -> dict:
    """Published lessons that discuss a raga or tala, or recommend a recording (a raga page's Lessons tab)."""
    out = []
    for l in await _published(session, False):
        if l.lang != "en":
            continue
        f = l.front or {}
        recs = [(r.get("id") if isinstance(r, dict) else r) for r in (f.get("recordings") or [])]
        if (raga and raga in (f.get("ragas") or [])) or (tala and tala in (f.get("talas") or [])) or (recording and recording in recs):
            out.append({"id": l.id, "slug": l.slug, "title": f.get("title", ""), "unit": l.unit, "order": l.order,
                        "minutes": f.get("minutes", 0)})
    return {"items": sorted(out, key=lambda x: (x["unit"], x["order"]))}


@router.get("/course/lessons/{key}")
async def course_lesson(key: str, request: Request, lang: str = "en", preview: bool = False,
                        session: AsyncSession = Depends(get_session)) -> dict:
    """By id (U01.L01) or slug. A translation is returned only when published; otherwise the English."""
    preview = preview and await is_operator(request, session)
    q = select(CarnaticLesson).where((CarnaticLesson.id == key) | (CarnaticLesson.slug == key))
    rows = (await session.execute(q)).scalars().all()
    visible = [r for r in rows if preview or r.status == "published"]
    en = next((r for r in visible if r.lang == "en"), None)
    tr = next((r for r in visible if r.lang == lang and lang != "en"), None)
    row = tr or en
    if row is None:
        raise HTTPException(404, "No such lesson.")
    out = lesson_json(row, await _approved_ids(session))
    if lang != "en":
        out["translation"] = ({"lang": lang, "status": tr.status, "outOfDate": bool(
            en and int((tr.front.get("translation") or {}).get("source_revision", 0) or 0) < en.revision)}
            if tr else {"lang": lang, "status": "none", "outOfDate": False})
    return out


@router.get("/course/exercises")
async def course_exercises(request: Request, unit: int | None = None, lesson: str | None = None,
                           preview: bool = False, session: AsyncSession = Depends(get_session)) -> dict:
    preview = preview and await is_operator(request, session)
    return {"items": await _exercises(session, preview, unit=unit, lesson=lesson)}


@router.get("/course/exercises/{ex_id}")
async def course_exercise(ex_id: str, request: Request, preview: bool = False,
                          session: AsyncSession = Depends(get_session)) -> dict:
    preview = preview and await is_operator(request, session)
    row = await session.get(CarnaticExercise, ex_id)
    if row is not None:
        items = await _exercises(session, preview, lesson=row.lesson) if row.lesson else []
        hit = next((x for x in items if x["id"] == ex_id), None)
        if hit is None and (preview or row.kind == "checkpoint" or ex_id.startswith("K.")):
            hit = {**row.data, "id": row.id, "unit": row.unit}
        if hit is not None:
            return hit
    k = next((k for k in await _tala_keeping(session) if k["id"] == ex_id), None)
    if k is not None:
        return k
    raise HTTPException(404, "No such exercise.")


@router.get("/course/glossary")
async def course_glossary(session: AsyncSession = Depends(get_session)) -> dict:
    return {"items": await _glossary(session)}


async def _tala_keeping(session: AsyncSession) -> list[dict]:
    """K.01-K.16: from exercises/selftest.yaml once imported (format 2), else the built-in table."""
    rows = (await session.execute(select(CarnaticExercise).where(CarnaticExercise.id.like("K.%"))
                                  .order_by(CarnaticExercise.id))).scalars().all()
    if not rows:
        return drills.TALA_KEEPING
    out = []
    for r in rows:
        d = {**r.data, "id": r.id}
        d.setdefault("unlockedBy", d.get("lesson", ""))
        out.append(d)
    return out


async def _drills(session: AsyncSession) -> dict:
    return {**drills.definitions(await _flags(session)), "talaKeeping": await _tala_keeping(session)}


@router.get("/course/drills")
async def course_drills(session: AsyncSession = Depends(get_session)) -> dict:
    return await _drills(session)


@router.get("/course/bundle")
async def course_bundle(request: Request, session: AsyncSession = Depends(get_session)):
    """Everything published, for reading offline (API.md §10b)."""
    v = await _version(session)
    tag = f'"{v["digest"]}"'
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers={"ETag": tag})
    approved = await _approved_ids(session)
    lessons = [lesson_json(l, approved) for l in await _published(session, False)]
    body = {"format": 2, "digest": v["digest"], "updatedAt": v["updatedAt"],
            "units": await units_json(session, False), "lessons": lessons,
            "exercises": await _exercises(session, False), "glossary": await _glossary(session),
            "drills": await _drills(session), "tala_keeping": await _tala_keeping(session)}
    return JSONResponse(body, headers={"ETag": tag, "Cache-Control": "no-cache"})


# ── lesson progress ─────────────────────────────────────────────────────────

class LessonStateIn(BaseModel):
    openedAt: str | None = None
    completedAt: str | None = None
    uncomplete: bool = False
    position: dict | None = None
    updatedAt: str | None = None


def _state_json(r: CarnaticLessonState) -> dict:
    return {"openedAt": _iso(r.opened_at), "completedAt": _iso(r.completed_at), "position": r.position,
            "updatedAt": _iso(r.updated_at)}


@router.get("/me/lessons")
async def my_lessons(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticLessonState).where(CarnaticLessonState.user_id == user.id))).scalars().all()
    return {"items": {r.lesson_id: _state_json(r) for r in rows}}


@router.put("/me/lessons/{lesson_id}")
async def put_my_lesson(lesson_id: str, body: LessonStateIn, request: Request, user: User = Depends(require_user),
                        session: AsyncSession = Depends(get_session)) -> dict:
    """Merge: opened keeps the earliest; completion and place follow the latest change."""
    if len(lesson_id) > 20:
        raise HTTPException(422, "No such lesson.")
    raw = await request.json()
    row = (await session.execute(select(CarnaticLessonState).where(
        CarnaticLessonState.user_id == user.id, CarnaticLessonState.lesson_id == lesson_id))).scalar_one_or_none()
    if row is None:
        row = CarnaticLessonState(user_id=user.id, lesson_id=lesson_id)
        session.add(row)
    stamp = _parse_dt(body.updatedAt) or _now()
    opened = _parse_dt(body.openedAt)
    if opened and (row.opened_at is None or opened < row.opened_at):
        row.opened_at = opened
    newer = row.updated_at is None or stamp >= row.updated_at
    if newer:
        if "completedAt" in raw:
            row.completed_at = _parse_dt(body.completedAt)
        if body.uncomplete:
            row.completed_at = None
        if body.position is not None:
            row.position = body.position
        row.updated_at = stamp
    if row.opened_at is None:
        row.opened_at = stamp
    await session.commit()
    await session.refresh(row)
    return _state_json(row)


# ── attempts, bests, cards ──────────────────────────────────────────────────

def word_for(right: int, of: int) -> str:
    """SELF_TEST.md §4: under 50 % new, 50-79 getting there, 80 and over comfortable."""
    share = right / of if of else 0
    return "comfortable" if share >= 0.8 else "getting there" if share >= 0.5 else "new"


class AttemptIn(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    itemId: str = Field(min_length=1, max_length=40)
    kind: str = Field(pattern="^(quiz|checkpoint|tap|drill|review|guess)$")
    startedAt: str
    seconds: int = Field(default=0, ge=0, le=86400)
    result: dict = Field(default_factory=dict)


class AttemptsIn(BaseModel):
    attempts: list[AttemptIn] = Field(max_length=200)


def _candidates(a: AttemptIn) -> list[tuple[str, dict]]:
    """(skill, best) pairs an attempt could set."""
    r = a.result or {}
    if a.kind == "checkpoint":
        out = [(skill, {"right": int(v.get("right", 0)), "of": int(v.get("of", 0))})
               for skill, v in (r.get("skills") or {}).items() if isinstance(v, dict) and v.get("of")]
        if r.get("of"):
            out.append(("", {"right": int(r.get("right", 0)), "of": int(r["of"])}))
        return [(s, {**b, "word": word_for(b["right"], b["of"])}) for s, b in out]
    if a.kind in ("quiz", "review") and r.get("of"):
        return [("", {"right": int(r.get("right", 0)), "of": int(r["of"]),
                      "word": word_for(int(r.get("right", 0)), int(r["of"]))})]
    if a.kind == "tap" and r.get("of"):
        good = int(r.get("perfect", 0)) + int(r.get("onTime", 0))
        return [("", {"tempo": int(r.get("tempo", 0)), "good": good, "of": int(r["of"]),
                      "perfect": int(r.get("perfect", 0))})]
    return []


def _better(kind: str, new: dict, old: dict | None) -> bool:
    if old is None:
        return True
    if kind == "tap":
        ns, os = new["good"] / max(new["of"], 1), old.get("good", 0) / max(old.get("of", 1), 1)
        if new["tempo"] != old.get("tempo", 0):
            return new["tempo"] > old.get("tempo", 0) and ns >= 0.8
        return ns > os
    return new["right"] / max(new["of"], 1) > old.get("right", 0) / max(old.get("of", 1), 1)


def _best_json(b: CarnaticBest) -> dict:
    return {"itemId": b.item_id, "skill": b.skill, "best": b.best, "previous": b.previous,
            "achievedAt": _iso(b.achieved_at)}


@router.post("/me/attempts")
async def post_attempts(body: AttemptsIn, user: User = Depends(require_user),
                        session: AsyncSession = Depends(get_session)) -> dict:
    stored, improved = 0, []
    for a in body.attempts:
        exists = (await session.execute(select(CarnaticAttempt.id).where(
            CarnaticAttempt.user_id == user.id, CarnaticAttempt.client_id == a.id))).first()
        if exists:
            continue
        started = _parse_dt(a.startedAt) or _now()
        session.add(CarnaticAttempt(user_id=user.id, client_id=a.id, item_id=a.itemId, kind=a.kind,
                                    started_at=started, seconds=a.seconds, result=a.result))
        stored += 1
        for skill, best in _candidates(a):
            row = (await session.execute(select(CarnaticBest).where(
                CarnaticBest.user_id == user.id, CarnaticBest.item_id == a.itemId,
                CarnaticBest.skill == skill))).scalar_one_or_none()
            if row is None:
                row = CarnaticBest(user_id=user.id, item_id=a.itemId, skill=skill, best=best, achieved_at=started)
                session.add(row)
                improved.append(row)
            elif _better(a.kind, best, row.best):
                row.previous, row.best, row.achieved_at = row.best, best, started
                improved.append(row)
    await session.commit()
    return {"stored": stored, "bests": [_best_json(b) for b in improved]}


@router.get("/me/attempts")
async def get_attempts(item: str | None = None, kind: str | None = None, limit: int = Query(50, le=500),
                       user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    q = select(CarnaticAttempt).where(CarnaticAttempt.user_id == user.id)
    if item:
        q = q.where(CarnaticAttempt.item_id == item)
    if kind:
        q = q.where(CarnaticAttempt.kind == kind)
    rows = (await session.execute(q.order_by(CarnaticAttempt.started_at.desc()).limit(limit))).scalars().all()
    return {"items": [{"id": r.client_id, "itemId": r.item_id, "kind": r.kind, "startedAt": _iso(r.started_at),
                       "seconds": r.seconds, "result": r.result} for r in rows]}


@router.get("/me/bests")
async def get_bests(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticBest).where(CarnaticBest.user_id == user.id)
                                  .order_by(CarnaticBest.achieved_at.desc()))).scalars().all()
    return {"items": [_best_json(b) for b in rows]}


# EAR_TRAINING.md §6: boxes 0-6 are this session, 1, 3, 7, 16, 35, 75 days.
BOX_DAYS = [0, 1, 3, 7, 16, 35, 75]


def next_due(box: int, seen: datetime) -> datetime:
    return seen + timedelta(days=BOX_DAYS[max(0, min(6, box))])


class CardIn(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    box: int = Field(ge=0, le=6)
    lastSeen: str | None = None
    nextDue: str | None = None
    recent: list[bool] = Field(default_factory=list, max_length=5)


class CardsIn(BaseModel):
    cards: list[CardIn] = Field(max_length=500)


def _card_json(c: CarnaticCard) -> dict:
    return {"key": c.key, "box": c.box, "lastSeen": _iso(c.last_seen), "nextDue": _iso(c.next_due),
            "recent": c.recent or []}


async def _due_count(session: AsyncSession, uid: int) -> int:
    return (await session.execute(select(func.count()).select_from(CarnaticCard).where(
        CarnaticCard.user_id == uid, CarnaticCard.next_due <= _now()))).scalar_one()


@router.get("/me/cards")
async def get_cards(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticCard).where(CarnaticCard.user_id == user.id))).scalars().all()
    return {"items": [_card_json(c) for c in rows], "due": await _due_count(session, user.id)}


@router.put("/me/cards")
async def put_cards(body: CardsIn, user: User = Depends(require_user),
                    session: AsyncSession = Depends(get_session)) -> dict:
    """Per card, the most recent review wins (a device's cards merging with the account's)."""
    out = []
    for c in body.cards:
        seen = _parse_dt(c.lastSeen)
        row = (await session.execute(select(CarnaticCard).where(
            CarnaticCard.user_id == user.id, CarnaticCard.key == c.key))).scalar_one_or_none()
        if row is None:
            row = CarnaticCard(user_id=user.id, key=c.key)
            session.add(row)
        elif row.last_seen is not None and seen is not None and seen <= row.last_seen:
            out.append(row)
            continue
        row.box, row.last_seen, row.recent = c.box, seen, c.recent[-5:]
        row.next_due = _parse_dt(c.nextDue) or (next_due(c.box, seen) if seen else _now())
        out.append(row)
    await session.commit()
    return {"items": [_card_json(c) for c in out], "due": await _due_count(session, user.id)}


# ── the Listening room: recordings, guesses, suggestions ────────────────────

def recording_json(r: CarnaticRecording, *, reveal: bool = True, analyses: int | None = 0,
                   guess_mode: bool = False, guessed: bool = True) -> dict:
    # A guess-mode recording's analyses (and their count) stay hidden until the viewer has guessed it.
    locked = guess_mode and not guessed
    guess = {"guessMode": guess_mode, "analysesLocked": locked}
    if r.status == "retired":
        return {"id": r.id, "status": "retired", "form": r.form, "raga": r.raga if reveal else None,
                "analyses": None if locked else analyses, **guess}
    out = {"id": r.id, "status": r.status, "provider": r.provider, "url": r.url, "title": r.title,
           "channel": r.channel, "artists": r.artists, "instrument": r.instrument, "composition": r.composition,
           "composer": r.composer, "form": r.form, "raga": r.raga, "tala": r.tala, "listenFor": r.listen_for,
           "clips": r.clips or [], "sections": r.sections or [], "beatMap": r.beat_map,
           "annotations": r.marks or {}, "analyses": None if locked else analyses, **guess}
    if not reveal:
        for k in ("title", "channel", "artists", "composition", "composer", "raga", "listenFor", "sections"):
            out[k] = None
    return out


async def _analysis_counts(session: AsyncSession) -> dict[str, int]:
    from shruti.models.practice import PracticeWork
    rows = (await session.execute(select(PracticeWork.subject, func.count()).where(
        PracticeWork.room == "carnatic-analysis", PracticeWork.submitted_at.is_not(None),
        PracticeWork.hidden.is_(False)).group_by(PracticeWork.subject))).all()
    return {s.removeprefix("recording:"): n for s, n in rows}


@router.get("/listening/recordings")
async def listening_recordings(raga: str | None = None, form: str | None = None, viewer: User | None = Depends(current_user),
                               session: AsyncSession = Depends(get_session)) -> dict:
    q = select(CarnaticRecording).where(CarnaticRecording.status.in_(("approved", "retired")))
    if raga:
        q = q.where(CarnaticRecording.raga == raga)
    if form:
        q = q.where(CarnaticRecording.form == form)
    rows = (await session.execute(q.order_by(CarnaticRecording.id))).scalars().all()
    counts = await _analysis_counts(session)
    gm, done = await guess_mode_ids(session), await guessed_ids(session, getattr(viewer, "id", None))
    return {"items": [recording_json(r, analyses=counts.get(r.id, 0), guess_mode=r.id in gm, guessed=r.id in done) for r in rows]}


@router.get("/listening/recordings/{rid}")
async def listening_recording(rid: str, viewer: User | None = Depends(current_user),
                              session: AsyncSession = Depends(get_session)) -> dict:
    r = await session.get(CarnaticRecording, rid)
    if r is None or r.status not in ("approved", "retired"):
        raise HTTPException(404, "No such recording.")
    counts = await _analysis_counts(session)
    return recording_json(r, analyses=counts.get(r.id, 0), guess_mode=r.id in await guess_mode_ids(session),
                          guessed=await has_guessed(session, getattr(viewer, "id", None), r.id))


class GuessIn(BaseModel):
    recording: str = Field(max_length=80)
    guess: str = Field(min_length=1, max_length=80)
    confidence: str = Field(default="", pattern="^(|hunch|fairly|sure)$")
    phrases: str = Field(default="", max_length=1000)


def _raga_name(raga_id: str) -> str:
    data = rules.data("ragas.json") or {}
    for r in data.get("janyas", []) + data.get("performed", []):
        if r["id"] == raga_id:
            return r["name"]
    for m in data.get("melakartas", []):
        if m.get("id") == raga_id:
            return m["name"]
    return raga_id.replace("-", " ").title()


def raga_key(text: str) -> str:
    """FORMAT.md §4c: the raga-name normaliser (Sankarabharanam = Dheerasankarabharanam, Thodi = Todi)."""
    import re
    t = text.lower().strip()
    t = re.sub(r"[\s\-_']", "", t)
    t = re.sub(r"^(dheera|dhira)", "", t)
    for a, b in (("th", "t"), ("sh", "s"), ("dh", "d"), ("bh", "b"), ("kh", "k"), ("gh", "g"), ("ch", "c"),
                 ("w", "v"), ("ow", "au"), ("ou", "au")):
        t = t.replace(a, b)
    t = re.sub(r"([aeiou])\1+", r"\1", t)
    t = re.sub(r"m$", "", t)      # a final -m or -am dropped: Mohanam, Mohana and Mohan are one raga
    t = re.sub(r"a$", "", t)
    return t


def _raga_matches(guess: str, raga_id: str) -> bool:
    data = rules.data("ragas.json") or {}
    names = {raga_id, raga_id.replace("-", " "), _raga_name(raga_id)}
    for r in data.get("janyas", []) + data.get("performed", []):
        if r["id"] == raga_id:
            names |= set(r.get("aliases") or [])
    target = {raga_key(n) for n in names}
    return raga_key(guess) in target or raga_key(guess) == raga_key(raga_id)


@router.post("/listening/guesses")
async def guess(body: GuessIn, viewer: User | None = Depends(current_user),
                session: AsyncSession = Depends(get_session)) -> dict:
    r = await session.get(CarnaticRecording, body.recording)
    if r is None or r.status != "approved" or not r.raga:
        raise HTTPException(404, "No such recording.")
    right = _raga_matches(body.guess, r.raga)
    if viewer is not None:
        session.add(CarnaticGuess(user_id=viewer.id, recording_id=r.id, guess=body.guess, confidence=body.confidence,
                                  phrases=body.phrases, right=right, created_at=_now()))
        await session.commit()
    lessons = (await session.execute(select(CarnaticLesson.id, CarnaticLesson.front).where(
        CarnaticLesson.status == "published"))).all()
    linked = [lid for lid, f in lessons if r.raga in ((f or {}).get("ragas") or [])]
    # A close miss: the guess is the other raga of a confusable set with this one (EAR_TRAINING.md §4).
    guessed = next((x for c in drills.CONFUSABLE for x in c["ragas"] if _raga_matches(body.guess, x)), None)
    pair = None if right or guessed is None else next(
        (c for c in drills.CONFUSABLE if r.raga in c["ragas"] and guessed in c["ragas"]), None)
    return {"right": right, "close": pair is not None, "pair": pair and {"set": pair["set"], "differ": pair["differ"],
            "guessName": _raga_name(guessed)}, "raga": r.raga, "ragaName": _raga_name(r.raga), "composition": r.composition,
            "composer": r.composer, "artists": r.artists, "listenFor": r.listen_for, "lessons": linked,
            "recording": recording_json(r)}


@router.get("/me/guesses")
async def my_guesses(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticGuess).where(CarnaticGuess.user_id == user.id)
                                  .order_by(CarnaticGuess.id.desc()))).scalars().all()
    return {"items": [{"recording": g.recording_id, "guess": g.guess, "confidence": g.confidence, "right": g.right,
                       "at": _iso(g.created_at)} for g in rows]}


_guess_cache: dict[str, tuple[float, set[str]]] = {}


async def guess_mode_ids(session: AsyncSession) -> set[str]:
    """
    Recordings in guess mode (LISTENING.md §5): flagged in the Studio, named by a
    `guess: true` exercise, or embedded with {{recording … guess=true}} in a lesson.
    Their analyses are hidden from anyone who hasn't committed a guess.
    """
    hit = _guess_cache.get("ids")
    if hit and time.monotonic() - hit[0] < 20:
        return hit[1]
    import re
    ids = {r[0] for r in (await session.execute(select(CarnaticRecording.id).where(CarnaticRecording.guess_mode.is_(True)))).all()}
    for (data,) in (await session.execute(select(CarnaticExercise.data))).all():
        if (data or {}).get("guess"):
            ids |= {str(r.get("id")) for r in (data.get("recordings") or []) if isinstance(r, dict) and r.get("id")}
    for (body,) in (await session.execute(select(CarnaticLesson.body).where(CarnaticLesson.lang == "en"))).all():
        for m in re.finditer(r"\{\{\s*recording\b([^}]*)\}\}", body or ""):
            if re.search(r"\bguess=\"?true", m.group(1)):
                rid = re.search(r"\bid=\"?([a-z0-9-]+)", m.group(1))
                if rid:
                    ids.add(rid.group(1))
    _guess_cache["ids"] = (time.monotonic(), ids)
    return ids


async def guessed_ids(session: AsyncSession, uid: int | None) -> set[str]:
    if uid is None:
        return set()
    return {r[0] for r in (await session.execute(select(CarnaticGuess.recording_id).where(CarnaticGuess.user_id == uid))).all()}


async def locked_recordings(session: AsyncSession, viewer) -> set[str]:
    """The guess-mode recordings this viewer hasn't guessed: their analyses stay hidden."""
    return await guess_mode_ids(session) - await guessed_ids(session, getattr(viewer, "id", None))


async def has_guessed(session: AsyncSession, uid: int | None, rid: str) -> bool:
    if uid is None:
        return False
    return (await session.execute(select(CarnaticGuess.id).where(
        CarnaticGuess.user_id == uid, CarnaticGuess.recording_id == rid))).first() is not None


class SuggestionIn(BaseModel):
    url: str = Field(min_length=8, max_length=500)
    raga: str = Field(default="", max_length=60)
    form: str = Field(default="", max_length=40)
    composition: str = Field(default="", max_length=200)
    why: str = Field(min_length=1, max_length=300)


PENDING_LIMIT = 5


async def oembed(url: str, provider: str) -> dict:
    """The provider's own title and channel for a link, or {} when it can't be read."""
    import httpx
    endpoints = {"youtube": "https://www.youtube.com/oembed", "vimeo": "https://vimeo.com/api/oembed.json",
                 "soundcloud": "https://soundcloud.com/oembed"}
    ep = endpoints.get(provider)
    if ep is None:
        return {}
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            r = await client.get(ep, params={"url": url, "format": "json"})
            if r.status_code == 200:
                d = r.json()
                return {"title": d.get("title", ""), "channel": d.get("author_name", "")}
    except (httpx.HTTPError, ValueError):
        pass
    return {}


@router.post("/listening/suggestions", status_code=201)
async def suggest(body: SuggestionIn, user: User = Depends(require_user),
                  session: AsyncSession = Depends(get_session)):
    from shruti.api.routes.practice import _refuse_if_suspended
    await _refuse_if_suspended(session, user)
    provider = rules.player_of(body.url)
    if provider is None:
        raise HTTPException(422, "Suggest a YouTube, SoundCloud, Vimeo or Bandcamp link.")
    pending = (await session.execute(select(func.count()).select_from(CarnaticRecording).where(
        CarnaticRecording.suggested_by == user.id, CarnaticRecording.status == "candidate"))).scalar_one()
    if pending >= PENDING_LIMIT:
        return JSONResponse(status_code=429, content={
            "code": "TOO_MANY_PENDING",
            "detail": "You have five suggestions waiting already. Shruti will get to them."})
    found = await oembed(body.url, provider)
    n = (await session.execute(select(func.count()).select_from(CarnaticRecording).where(
        CarnaticRecording.id.like("m-%")))).scalar_one()
    row = CarnaticRecording(id=f"m-{n + 1:04d}", status="candidate", provider=provider, url=body.url.strip(),
                            title=found.get("title", ""), channel=found.get("channel", ""), raga=body.raga,
                            form=body.form, composition=body.composition, uploader_kind="",
                            flags=[] if found else ["title and channel could not be read"],
                            suggested_by=user.id, suggestion={"why": body.why, "at": _iso(_now())})
    session.add(row)
    await session.commit()
    return {"id": row.id, "title": row.title, "channel": row.channel, "status": "pending"}


@router.get("/me/suggestions")
async def my_suggestions(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticRecording).where(CarnaticRecording.suggested_by == user.id)
                                  .order_by(CarnaticRecording.created_at.desc()))).scalars().all()
    status = {"candidate": "pending", "approved": "approved", "rejected": "rejected", "held": "held",
              "retired": "approved"}
    return {"items": [{"id": r.id, "url": r.url, "title": r.title, "channel": r.channel, "raga": r.raga,
                       "status": status.get(r.status, r.status), "reason": r.reason} for r in rows]}


@router.get("/me/community")
async def my_community(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    from shruti.api.routes.practice import _suspended
    s = await _suspended(session, user.id)
    return {"suspended": None if s is None else {"until": _iso(s.until), "reason": s.reason}}
