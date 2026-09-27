# SPDX-License-Identifier: AGPL-3.0-only
"""
The Swara Studio admin: Sophia's own area for the school, isolated from the
rest of the site admin (DESIGN_REQUEST_v2 §7). Operator only.

Lessons: the course tree; the editor (front matter as a form, body as text,
the checks in words, editor notes, the meaning-change prompt, revisions and
restore); "a newer file version exists" when the course repository changed
under an edited lesson. Exercises and the glossary, editable. Recordings:
the candidate queue with approve / reject with a reason / hold, annotation
(clips, sections, beat map) and the balance view. Raga flags for the synth.
Moderation for the community rooms (Listen posts, comments and sheets keep
their v1 endpoints under /api/carnatic/admin).
"""
from __future__ import annotations

import re

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core import carnatic_course as course
from shruti.core import carnatic_drills as drills
from shruti.core.db import get_session
from shruti.models.accounts import User
from shruti.models.carnatic_course import (
    CarnaticExercise, CarnaticGlossary, CarnaticLesson, CarnaticLessonRevision, CarnaticRagaFlag,
    CarnaticRecording, CarnaticUnit, PracticePart,
)
from shruti.models.practice import PracticeComment, PracticeReport, PracticeStrike, PracticeVote, PracticeWork

router = APIRouter(prefix="/api/carnatic/studio", tags=["carnatic-studio"], dependencies=[Depends(require_admin)])

ROOMS = ("carnatic-practice", "carnatic-analysis")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt):
    return None if dt is None else (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


async def _exercise_ids(session: AsyncSession) -> set[str]:
    return set((await _exercise_kinds(session)).keys()) | {k["id"] for k in drills.TALA_KEEPING}


async def _exercise_kinds(session: AsyncSession) -> dict[str, str]:
    return {r[0]: r[1] for r in (await session.execute(select(CarnaticExercise.id, CarnaticExercise.kind))).all()}


DRILL_IDS = {l["id"] for l in drills.LEVELS}


# ── lessons ─────────────────────────────────────────────────────────────────

@router.get("/tree")
async def tree(session: AsyncSession = Depends(get_session)) -> dict:
    units = (await session.execute(select(CarnaticUnit).order_by(CarnaticUnit.n))).scalars().all()
    rows = (await session.execute(select(CarnaticLesson))).scalars().all()
    by = defaultdict(dict)
    for r in rows:
        by[r.id][r.lang] = r
    out = []
    counts = Counter()
    for u in units:
        lessons = []
        for s in u.lessons or []:
            langs = by.get(s["id"], {})
            en = langs.get("en")
            status = en.status if en else "planned"
            counts[status] += 1
            translations = {}
            for lang in ("ta", "te", "kn"):
                t = langs.get(lang)
                if t is None:
                    translations[lang] = "none"
                else:
                    src = int((t.front.get("translation") or {}).get("source_revision", 0) or 0)
                    translations[lang] = "out of date" if en and src < en.revision else t.status
            lessons.append({
                "id": s["id"], "title": (en.front.get("title") if en else s.get("title")), "status": status,
                "slug": en.slug if en else s.get("slug"), "revision": en.revision if en else None,
                "edited": bool(en and en.admin_edited), "newerFile": bool(en and en.file_hash),
                "notes": len(course.editor_notes(en.body)) if en else 0, "translations": translations,
                "minutes": (en.front.get("minutes") if en else s.get("minutes")),
            })
        out.append({"n": u.n, "title": u.title, "level": u.level, "lessons": lessons})
    return {"units": out, "counts": dict(counts)}


def _lesson_admin(row: CarnaticLesson, check: dict) -> dict:
    return {"id": row.id, "lang": row.lang, "slug": row.slug, "status": row.status, "revision": row.revision,
            "front": row.front, "body": row.body, "edited": row.admin_edited, "editedAt": _iso(row.edited_at),
            "editedBy": row.edited_by, "updatedAt": _iso(row.updated_at),
            "newerFile": ({"front": row.file_front, "body": row.file_body, "seenAt": _iso(row.file_seen_at)}
                          if row.file_hash else None),
            "check": check}


async def _lesson(session: AsyncSession, lesson_id: str, lang: str) -> CarnaticLesson:
    row = await session.get(CarnaticLesson, (lesson_id, lang))
    if row is None:
        raise HTTPException(404, "No such lesson.")
    return row


@router.get("/lessons/{lesson_id}")
async def lesson(lesson_id: str, lang: str = "en", session: AsyncSession = Depends(get_session)) -> dict:
    row = await _lesson(session, lesson_id, lang)
    check = course.check_lesson(row.front, row.body, await _exercise_ids(session), DRILL_IDS, await _exercise_kinds(session))
    return _lesson_admin(row, check)


@router.post("/lessons/{lesson_id}/create", status_code=201)
async def create_lesson(lesson_id: str, by: str = Depends(require_admin), session: AsyncSession = Depends(get_session)) -> dict:
    """A draft for a lesson the syllabus plans but no file has written yet (format 2 front matter, empty body)."""
    if await session.get(CarnaticLesson, (lesson_id, "en")) is not None:
        raise HTTPException(409, "That lesson already exists.")
    units = (await session.execute(select(CarnaticUnit))).scalars().all()
    entry = next(((u, s) for u in units for s in (u.lessons or []) if s.get("id") == lesson_id), None)
    if entry is None:
        raise HTTPException(404, "The syllabus has no such lesson.")
    u, s = entry
    goals = [g.strip() for g in re.split(r";\s*", str(s.get("goals") or "")) if g.strip()]
    front = {"format": 2, "id": lesson_id, "slug": s.get("slug") or lesson_id.lower().replace(".", "-"), "lang": "en",
             "revision": 1, "status": "draft", "unit": u.n, "order": int(lesson_id[-2:]), "title": s.get("title", ""),
             "summary": "", "level": s.get("level") if s.get("level") in ("beginner", "intermediate", "advanced") else "beginner",
             "minutes": s.get("minutes") or 15, "goals": goals, "prerequisites": s.get("after") or [],
             "tools": [], "ragas": [], "talas": [], "recordings": [], "sources": [], "exercises": [], "author": "", "editor": by}
    row = CarnaticLesson(id=lesson_id, lang="en", front=front, body="", base_hash="", admin_edited=True,
                         edited_at=_now(), edited_by=by, **course.lesson_fields(front))
    session.add(row)
    session.add(CarnaticLessonRevision(lesson_id=lesson_id, lang="en", revision=1, front=front, body="", source="admin",
                                       by=by, note="started in the Studio", created_at=_now()))
    await session.commit()
    return {"id": lesson_id}


class LessonDraft(BaseModel):
    front: dict
    body: str = Field(max_length=400_000)


@router.post("/lessons/{lesson_id}/check")
async def check(lesson_id: str, body: LessonDraft, lang: str = "en",
                session: AsyncSession = Depends(get_session)) -> dict:
    row = await _lesson(session, lesson_id, lang)
    result = course.check_lesson(body.front, body.body, await _exercise_ids(session), DRILL_IDS, await _exercise_kinds(session))
    result["meaningChange"] = course.is_meaning_change(row.body, body.body)
    return result


class LessonSave(LessonDraft):
    status: str = Field(pattern="^(draft|review|published)$")
    meaningChange: bool | None = None
    note: str = Field(default="", max_length=300)


@router.put("/lessons/{lesson_id}")
async def save(lesson_id: str, body: LessonSave, lang: str = "en", by: str = Depends(require_admin),
               session: AsyncSession = Depends(get_session)):
    """
    Saving a draft is never blocked. Publishing is blocked only by a missing
    required field, an unknown exercise id or an open editor note. A change of
    more than a typo asks once whether it changes the meaning; yes raises the
    revision, which marks translations out of date.
    """
    row = await _lesson(session, lesson_id, lang)
    result = course.check_lesson(body.front, body.body, await _exercise_ids(session), DRILL_IDS, await _exercise_kinds(session))
    if body.status == "published" and not result["publishable"]:
        return JSONResponse(status_code=422, content={"code": "NOT_PUBLISHABLE", "check": result,
                                                      "detail": "Saved nothing: fix these before publishing."})
    changed = course.is_meaning_change(row.body, body.body)
    if changed and body.meaningChange is None:
        return JSONResponse(status_code=409, content={
            "code": "MEANING_PROMPT",
            "detail": "Is this a change of meaning? Translations will be marked out of date."})
    front = dict(body.front)
    revision = row.revision + (1 if changed and body.meaningChange else 0)
    front["revision"], front["status"] = revision, body.status
    was_published = row.status == "published"
    row.front, row.body, row.status, row.revision = front, body.body, body.status, revision
    for k, v in course.lesson_fields(front).items():
        setattr(row, k, v)
    row.admin_edited, row.edited_at, row.edited_by, row.updated_at = True, _now(), by, _now()
    if body.status == "published" and not was_published:
        row.published_at = _now()
    session.add(CarnaticLessonRevision(lesson_id=row.id, lang=row.lang, revision=revision, front=front,
                                       body=body.body, source="admin", by=by, note=body.note,
                                       meaning_change=bool(changed and body.meaningChange), created_at=_now()))
    await session.commit()
    return _lesson_admin(row, result)


@router.get("/lessons/{lesson_id}/revisions")
async def revisions(lesson_id: str, lang: str = "en", session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticLessonRevision).where(
        CarnaticLessonRevision.lesson_id == lesson_id, CarnaticLessonRevision.lang == lang)
        .order_by(CarnaticLessonRevision.id.desc()))).scalars().all()
    out = []
    for i, r in enumerate(rows):
        prev = rows[i + 1] if i + 1 < len(rows) else None
        out.append({"id": r.id, "revision": r.revision, "source": r.source, "by": r.by, "note": r.note,
                    "meaningChange": r.meaning_change, "at": _iso(r.created_at),
                    "changed": _summary(prev.body if prev else "", r.body, prev.front if prev else {}, r.front)})
    return {"items": out}


def _summary(old_body: str, new_body: str, old_front: dict, new_front: dict) -> str:
    fields = [k for k in set(old_front) | set(new_front) if old_front.get(k) != new_front.get(k)
              and k not in ("revision",)]
    import difflib
    lines = [l for l in difflib.unified_diff(old_body.splitlines(), new_body.splitlines(), lineterm="", n=0)
             if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    bits = []
    if lines:
        bits.append(f"{len(lines)} lines of text")
    if fields:
        bits.append("fields: " + ", ".join(sorted(fields)[:6]))
    return "; ".join(bits) or "no change"


@router.post("/lessons/{lesson_id}/restore/{rev_id}")
async def restore(lesson_id: str, rev_id: int, lang: str = "en", by: str = Depends(require_admin),
                  session: AsyncSession = Depends(get_session)) -> dict:
    row = await _lesson(session, lesson_id, lang)
    rev = await session.get(CarnaticLessonRevision, rev_id)
    if rev is None or rev.lesson_id != lesson_id or rev.lang != lang:
        raise HTTPException(404, "No such revision.")
    row.front, row.body = dict(rev.front), rev.body
    row.front["status"] = row.status
    row.front["revision"] = row.revision
    row.admin_edited, row.edited_at, row.edited_by, row.updated_at = True, _now(), by, _now()
    session.add(CarnaticLessonRevision(lesson_id=row.id, lang=lang, revision=row.revision, front=row.front,
                                       body=row.body, source="restore", by=by,
                                       note=f"restored revision of {_iso(rev.created_at)}", created_at=_now()))
    await session.commit()
    return _lesson_admin(row, course.check_lesson(row.front, row.body, await _exercise_ids(session), DRILL_IDS, await _exercise_kinds(session)))


@router.post("/lessons/{lesson_id}/take-file")
async def take_file(lesson_id: str, lang: str = "en", by: str = Depends(require_admin),
                    session: AsyncSession = Depends(get_session)) -> dict:
    """Replace the admin copy with the newer file version, and follow the files again."""
    row = await _lesson(session, lesson_id, lang)
    if not row.file_hash:
        raise HTTPException(409, "There's no newer file version.")
    row.front, row.body, row.base_hash = row.file_front, row.file_body, row.file_hash
    for k, v in course.lesson_fields(row.front).items():
        setattr(row, k, v)
    row.file_hash, row.file_front, row.file_body, row.admin_edited = "", None, None, False
    row.updated_at = _now()
    session.add(CarnaticLessonRevision(lesson_id=row.id, lang=lang, revision=row.revision, front=row.front,
                                       body=row.body, source="import", by=by, note="took the file version",
                                       created_at=_now()))
    await session.commit()
    return _lesson_admin(row, course.check_lesson(row.front, row.body, await _exercise_ids(session), DRILL_IDS, await _exercise_kinds(session)))


# ── exercises and glossary ──────────────────────────────────────────────────

@router.get("/exercises")
async def exercises(unit: int | None = None, session: AsyncSession = Depends(get_session)) -> dict:
    q = select(CarnaticExercise)
    if unit is not None:
        q = q.where(CarnaticExercise.unit == unit)
    rows = (await session.execute(q.order_by(CarnaticExercise.id))).scalars().all()
    return {"items": [{"id": r.id, "unit": r.unit, "lesson": r.lesson, "kind": r.kind, "data": r.data,
                       "edited": r.admin_edited, "newerFile": bool(r.file_hash)} for r in rows]}


class ExerciseSave(BaseModel):
    data: dict


@router.put("/exercises/{ex_id}")
async def save_exercise(ex_id: str, body: ExerciseSave, session: AsyncSession = Depends(get_session)) -> dict:
    row = await session.get(CarnaticExercise, ex_id)
    if row is None:
        raise HTTPException(404, "No such exercise.")
    data = dict(body.data)
    data["id"] = ex_id
    row.data, row.kind, row.lesson = data, data.get("kind", row.kind), data.get("lesson", row.lesson)
    row.admin_edited, row.edited_at, row.updated_at = True, _now(), _now()
    await session.commit()
    return {"id": row.id, "data": row.data, "edited": True}


@router.post("/exercises/{ex_id}/take-file")
async def exercise_take_file(ex_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = await session.get(CarnaticExercise, ex_id)
    if row is None or not row.file_hash:
        raise HTTPException(409, "There's no newer file version.")
    row.data, row.base_hash, row.file_hash, row.file_data, row.admin_edited = row.file_data, row.file_hash, "", None, False
    row.updated_at = _now()
    await session.commit()
    return {"id": row.id, "data": row.data, "edited": False}


class TermIn(BaseModel):
    term: str = Field(min_length=1, max_length=80)
    definition: str = Field(min_length=1, max_length=800)
    lesson: str = Field(default="", max_length=20)
    forms: list[str] | None = Field(default=None, max_length=24)
    aliases: list[str] = Field(default_factory=list, max_length=24)   # the old name for forms
    iso: str = Field(default="", max_length=120)
    source: str = Field(default="", max_length=80)


@router.get("/glossary")
async def glossary(session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticGlossary).order_by(CarnaticGlossary.term))).scalars().all()
    return {"items": [{"slug": g.slug, "term": g.term, "definition": g.definition, "lesson": g.lesson,
                       "forms": g.aliases, "iso": g.iso, "source": g.source, "edited": g.admin_edited,
                       "newerFile": bool(g.file_hash), "fileData": g.file_data if g.file_hash else None} for g in rows]}


@router.put("/glossary/{slug}")
async def save_term(slug: str, body: TermIn, session: AsyncSession = Depends(get_session)) -> dict:
    import re
    if not re.fullmatch(r"[a-z0-9-]{1,80}", slug):
        raise HTTPException(422, "A slug is lower-case letters, digits and hyphens.")
    row = await session.get(CarnaticGlossary, slug)
    if row is None:
        row = CarnaticGlossary(slug=slug)
        session.add(row)
    forms = body.forms if body.forms is not None else body.aliases
    row.term, row.definition, row.lesson = body.term.strip(), body.definition.strip(), body.lesson
    row.aliases, row.iso, row.source = [f.strip() for f in forms if f.strip()], body.iso.strip(), body.source.strip()
    row.admin_edited, row.updated_at = True, _now()
    await session.commit()
    return {"slug": slug, "term": row.term, "definition": row.definition, "lesson": row.lesson, "forms": row.aliases,
            "iso": row.iso, "source": row.source}


@router.delete("/glossary/{slug}", status_code=204)
async def delete_term(slug: str, session: AsyncSession = Depends(get_session)):
    from fastapi import Response
    row = await session.get(CarnaticGlossary, slug)
    if row is not None:
        await session.delete(row)
        await session.commit()
    return Response(status_code=204)


# ── recordings ──────────────────────────────────────────────────────────────

def _rec(r: CarnaticRecording, suggester: str | None = None) -> dict:
    return {"id": r.id, "status": r.status, "provider": r.provider, "url": r.url, "title": r.title,
            "channel": r.channel, "uploaderKind": r.uploader_kind, "artists": r.artists, "instrument": r.instrument,
            "composition": r.composition, "composer": r.composer, "form": r.form, "raga": r.raga, "tala": r.tala,
            "pageSays": r.page_says, "listenFor": r.listen_for, "flags": r.flags, "duration": r.duration,
            "clips": r.clips, "sections": r.sections, "beatMap": r.beat_map, "marks": r.marks or {}, "reason": r.reason,
            "decidedAt": _iso(r.decided_at), "approvedAt": _iso(r.approved_at),
            "suggestion": ({**(r.suggestion or {}), "by": suggester} if r.suggestion is not None else None),
            "research": (r.raw or {}).get("file", "")}


@router.get("/recordings")
async def recordings(status: str | None = None, raga: str | None = None, form: str | None = None,
                     q: str | None = None, session: AsyncSession = Depends(get_session)) -> dict:
    query = select(CarnaticRecording)
    if status:
        query = query.where(CarnaticRecording.status == status)
    if raga:
        query = query.where(CarnaticRecording.raga == raga)
    if form:
        query = query.where(CarnaticRecording.form == form)
    rows = (await session.execute(query.order_by(CarnaticRecording.suggested_by.is_(None),
                                                 CarnaticRecording.id))).scalars().all()
    if q:
        ql = q.lower()
        rows = [r for r in rows if ql in f"{r.id} {r.title} {r.channel} {r.composition}".lower()]
    counts = dict((await session.execute(select(CarnaticRecording.status, func.count())
                                         .group_by(CarnaticRecording.status))).all())
    out = []
    for r in rows:
        name = None
        if r.suggested_by:
            u = await session.get(User, r.suggested_by)
            name = (u.display_name or "").strip() or "somebody" if u else "somebody"
        out.append(_rec(r, name))
    return {"items": out, "counts": counts}


@router.get("/recordings/{rid}")
async def one_recording(rid: str, session: AsyncSession = Depends(get_session)) -> dict:
    r = await session.get(CarnaticRecording, rid)
    if r is None:
        raise HTTPException(404, "No such recording.")
    name = None
    if r.suggested_by:
        u = await session.get(User, r.suggested_by)
        name = ((u.display_name or "").strip() or "somebody") if u else "somebody"
    return _rec(r, name)


class Decision(BaseModel):
    action: str = Field(pattern="^(approve|reject|hold|retire|candidate)$")
    reason: str = Field(default="", max_length=300)


@router.post("/recordings/{rid}/decide")
async def decide(rid: str, body: Decision, session: AsyncSession = Depends(get_session)) -> dict:
    r = await session.get(CarnaticRecording, rid)
    if r is None:
        raise HTTPException(404, "No such recording.")
    if body.action == "reject" and not body.reason.strip():
        raise HTTPException(422, "Say why, in a line: the person who suggested it sees the reason.")
    r.status = {"approve": "approved", "reject": "rejected", "hold": "held", "retire": "retired",
                "candidate": "candidate"}[body.action]
    r.reason = body.reason.strip()
    r.decided_at = _now()
    if body.action == "approve":
        r.approved_at = r.approved_at or _now()
    r.updated_at = _now()
    await session.commit()
    return _rec(r)


class Annotations(BaseModel):
    clips: list[dict] | None = None
    sections: list[dict] | None = None
    beatMap: dict | None = None
    clearBeatMap: bool = False
    marks: dict | None = None
    listenFor: str | None = None
    raga: str | None = None
    tala: str | None = None
    form: str | None = None
    instrument: str | None = None
    composition: str | None = None
    composer: str | None = None
    artists: list[str] | None = None


def _clean_marks(m: dict) -> dict:
    """Her marks for the ear trainer, trimmed to the shapes the drills read."""
    def secs(x) -> float | None:
        try:
            return round(float(x), 3)
        except (TypeError, ValueError):
            return None
    out: dict = {}
    out["transcriptions"] = [{"start": str(t.get("start", "")), "end": str(t.get("end", "")), "sargam": str(t.get("sargam", ""))[:400]}
                             for t in (m.get("transcriptions") or []) if isinstance(t, dict) and t.get("sargam")][:50]
    out["gamakas"] = [{"t": str(g.get("t", "")), "gamakas": [str(x) for x in (g.get("gamakas") or [])][:6]}
                      for g in (m.get("gamakas") or []) if isinstance(g, dict) and g.get("gamakas")][:50]
    out["korvais"] = [{"start": str(k.get("start", "")), "landing": secs(k.get("landing"))}
                      for k in (m.get("korvais") or []) if isinstance(k, dict) and secs(k.get("landing")) is not None][:50]
    return out


@router.put("/recordings/{rid}")
async def annotate(rid: str, body: Annotations, session: AsyncSession = Depends(get_session)) -> dict:
    r = await session.get(CarnaticRecording, rid)
    if r is None:
        raise HTTPException(404, "No such recording.")
    if body.clips is not None:
        r.clips = [{"id": str(c.get("id") or chr(97 + i)), "start": str(c.get("start", "")),
                    "end": str(c.get("end", "")), "label": str(c.get("label", ""))[:120]}
                   for i, c in enumerate(body.clips)]
    if body.sections is not None:
        r.sections = [{"t": str(s.get("t", "")), "label": str(s.get("label", ""))[:80]} for s in body.sections]
    if body.beatMap is not None:
        samam = [round(float(x), 3) for x in body.beatMap.get("samam", []) if isinstance(x, (int, float))]
        counts = [round(float(x), 3) for x in body.beatMap.get("counts", []) if isinstance(x, (int, float))]
        r.beat_map = {"clip": body.beatMap.get("clip"), "tala": body.beatMap.get("tala", r.tala), "samam": samam,
                      "counts": counts}
    if body.clearBeatMap:
        r.beat_map = None
    if body.marks is not None:
        r.marks = _clean_marks(body.marks)
    for field, attr in (("listenFor", "listen_for"), ("raga", "raga"), ("tala", "tala"), ("form", "form"),
                        ("instrument", "instrument"), ("composition", "composition"), ("composer", "composer"),
                        ("artists", "artists")):
        value = getattr(body, field)
        if value is not None:
            setattr(r, attr, value)
    r.admin_edited, r.updated_at = True, _now()
    await session.commit()
    return _rec(r)


@router.get("/balance")
async def balance(session: AsyncSession = Depends(get_session)) -> dict:
    """Approved recordings per raga, by instrument and by artist (LISTENING.md §2)."""
    rows = (await session.execute(select(CarnaticRecording).where(CarnaticRecording.status == "approved"))).scalars().all()
    by: dict[str, dict] = {}
    for r in rows:
        key = r.raga or f"form:{r.form}"
        b = by.setdefault(key, {"total": 0, "instruments": Counter(), "artists": Counter()})
        b["total"] += 1
        b["instruments"][r.instrument or "not stated"] += 1
        for a in (r.artists or [])[:1]:
            b["artists"][a.split("(")[0].strip()] += 1
    return {"items": [{"key": k, "total": v["total"], "instruments": dict(v["instruments"]),
                       "artists": dict(v["artists"])} for k, v in sorted(by.items())]}


@router.get("/raga-flags")
async def raga_flags(session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticRagaFlag).order_by(CarnaticRagaFlag.raga))).scalars().all()
    return {"items": [{"raga": f.raga, "synthOk": f.synth_ok, "note": f.note} for f in rows]}


class FlagIn(BaseModel):
    synthOk: bool
    note: str = Field(default="", max_length=200)


@router.put("/raga-flags/{raga}")
async def set_flag(raga: str, body: FlagIn, session: AsyncSession = Depends(get_session)) -> dict:
    row = await session.get(CarnaticRagaFlag, raga)
    if row is None:
        row = CarnaticRagaFlag(raga=raga)
        session.add(row)
    row.synth_ok, row.note, row.updated_at = body.synthOk, body.note, _now()
    await session.commit()
    return {"raga": raga, "synthOk": row.synth_ok}


# ── moderation of the community rooms ───────────────────────────────────────

@router.get("/moderation")
async def moderation(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Reported and hidden pieces, analyses and their comments. Waiting for her
    (hidden by three reports) first; reporters never shown, only reasons.
    """
    works = (await session.execute(select(PracticeWork).where(PracticeWork.room.in_(ROOMS),
                                                              PracticeWork.submitted_at.is_not(None)))).scalars().all()
    ids = [w.id for w in works]
    reports = (await session.execute(select(PracticeReport).where(
        (PracticeReport.work_id.in_(ids or [-1])) |
        (PracticeReport.comment_id.in_(select(PracticeComment.id).where(PracticeComment.work_id.in_(ids or [-1]))))
    ))).scalars().all()
    by_work, by_comment = defaultdict(list), defaultdict(list)
    for r in reports:
        (by_work[r.work_id] if r.work_id else by_comment[r.comment_id]).append(r)
    out = []
    for w in works:
        rs = by_work.get(w.id, [])
        if not rs and not w.hidden:
            continue
        author = await session.get(User, w.user_id) if w.user_id else None
        part = (await session.execute(select(PracticePart).where(PracticePart.work_id == w.id,
                                                                 PracticePart.key.in_(("text", "summary"))))).scalars().first()
        out.append({"kind": "work", "id": w.id, "room": w.room, "subject": w.subject, "title": w.title,
                    "author": (author.display_name or "somebody") if author else "somebody", "authorId": w.user_id,
                    "excerpt": part.body_md[:300] if part else "", "hidden": w.hidden, "hiddenBy": w.hidden_by,
                    "reports": len({r.user_id for r in rs if r.reviewed_at is None}),
                    "reasons": dict(Counter(r.reason for r in rs if r.reviewed_at is None)),
                    "details": [r.detail for r in rs if r.detail and r.reviewed_at is None][:5]})
    comments = (await session.execute(select(PracticeComment).where(PracticeComment.work_id.in_(ids or [-1]))))\
        .scalars().all()
    for c in comments:
        rs = by_comment.get(c.id, [])
        if not rs and not c.hidden:
            continue
        author = await session.get(User, c.user_id) if c.user_id else None
        out.append({"kind": "comment", "id": c.id, "workId": c.work_id, "excerpt": c.body_md[:300],
                    "author": (author.display_name or "somebody") if author else "somebody", "authorId": c.user_id,
                    "hidden": c.hidden, "hiddenBy": c.hidden_by,
                    "reports": len({r.user_id for r in rs if r.reviewed_at is None}),
                    "reasons": dict(Counter(r.reason for r in rs if r.reviewed_at is None)),
                    "details": [r.detail for r in rs if r.detail and r.reviewed_at is None][:5]})
    out.sort(key=lambda e: (e["hiddenBy"] != "reports", -e["reports"]))
    week = _now() - timedelta(days=7)
    discussed = []
    for w in works:
        if w.hidden or w.submitted_at is None or w.submitted_at < week:
            continue
        v = (await session.execute(select(func.count()).select_from(PracticeVote).where(PracticeVote.work_id == w.id))).scalar_one()
        c = sum(1 for x in comments if x.work_id == w.id and not x.hidden)
        discussed.append({"id": w.id, "room": w.room, "subject": w.subject, "title": w.title, "votes": v,
                          "comments": c, "score": v + 2 * c})
    discussed.sort(key=lambda d: -d["score"])
    strikes = (await session.execute(select(PracticeStrike).where(PracticeStrike.lifted_at.is_(None)))).scalars().all()
    return {"items": out, "awaiting": sum(1 for e in out if e["hiddenBy"] == "reports"),
            "mostDiscussed": discussed[:10],
            "strikes": [{"id": s.id, "userId": s.user_id, "until": _iso(s.until), "reason": s.reason} for s in strikes]}


class Verdict(BaseModel):
    outcome: str = Field(pattern="^(restore|remove|hide)$")
    suspendDays: int | None = Field(default=None, ge=0, le=3650)
    reason: str = Field(default="", max_length=500)


@router.post("/moderation/{kind}/{item_id}")
async def verdict(kind: str, item_id: int, body: Verdict, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Restore puts it straight back and closes its reports; remove takes it down
    for good (kept for the record, shown to nobody); either can suspend the
    author from posting (the practice room's strike: 0 days is indefinite).
    """
    if kind == "work":
        thing = await session.get(PracticeWork, item_id)
        column = PracticeReport.work_id
        if thing is not None and thing.room not in ROOMS:
            thing = None
    elif kind == "comment":
        thing = await session.get(PracticeComment, item_id)
        column = PracticeReport.comment_id
    else:
        raise HTTPException(404, "No such thing.")
    if thing is None:
        raise HTTPException(404, "No such thing.")
    if body.outcome == "restore":
        thing.hidden, thing.hidden_by = False, ""
    else:
        thing.hidden, thing.hidden_by = True, "her"
    now = _now()
    for r in (await session.execute(select(PracticeReport).where(column == item_id,
                                                                 PracticeReport.reviewed_at.is_(None)))).scalars():
        r.reviewed_at, r.outcome = now, "dismissed" if body.outcome == "restore" else "upheld"
    suspended = None
    if body.suspendDays is not None and thing.user_id:
        until = None if body.suspendDays == 0 else now + timedelta(days=body.suspendDays)
        session.add(PracticeStrike(user_id=thing.user_id, until=until,
                                   reason=body.reason or "Reported writing in Swara Studio."))
        suspended = "indefinite" if until is None else until.isoformat()
    await session.commit()
    return {"ok": True, "hidden": thing.hidden, "suspendedUntil": suspended}
