# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio's community: practice pieces (room `carnatic-practice`, subject
`exercise:<id>`) and listening analyses (room `carnatic-analysis`, subject
`recording:<id>`), on the site's practice model (LISTENING.md §4d option 2).
Contract: docs/carnatic/API.md §15.

The same votes, comments, reports, strikes and blocks as the horoscope
practice room, so a suspension or a block holds everywhere, and the same
rules: one vote per person; three distinct reporters hide a thing until
Sophia reviews it, and reporters are never shown; blocks work both ways and
nobody is told; a suspension pauses posting, never reading. Nobody gets a
grade: the rubric is shown only as totals. A deleted account's pieces and
analyses stay, anonymised as "somebody" (Sophia's rule; the practice model
already keeps submitted works that way).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.routes.accounts import current_user, require_user
from shruti.api.routes.practice import (
    REPORT_REASONS, REPORTS_TO_HIDE, _blocked_by, _count_reports, _hidden_from, _name, _refuse_if_suspended,
)
from shruti.core import carnatic_checks as checks
from shruti.core.db import get_session
from shruti.models.accounts import User
from shruti.models.carnatic_course import CarnaticExercise, CarnaticRecording, PracticePart, PracticeRubric
from shruti.models.practice import PracticeBlock, PracticeComment, PracticeReport, PracticeVote, PracticeWork

router = APIRouter(prefix="/api/carnatic/community", tags=["carnatic-community"])

ROOMS = {"carnatic-practice", "carnatic-analysis"}
# LISTENING.md §4c: the practice room's reasons, with "not-a-reading" replaced.
REASONS = [r if r != "not-a-reading" else "not-about-this-exercise" for r in REPORT_REASONS]
# LISTENING.md §4b: every analysis gets these three.
ANALYSIS_RUBRIC = [
    {"id": "accurate", "ask": "Do the timestamps point at what the notes say?", "scale": ["no", "mostly", "yes"]},
    {"id": "helped", "ask": "Did it help you hear something you'd missed?", "scale": ["no", "a little", "yes"]},
    {"id": "add", "ask": "One thing you'd add", "answer": "free"},
]
NOTE_CATEGORIES = ["phrase", "resting note", "gamaka", "section", "tala", "laya", "other"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt):
    return None if dt is None else (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).isoformat()


async def _exercise(session: AsyncSession, work: PracticeWork) -> dict | None:
    if work.subject.startswith("exercise:"):
        row = await session.get(CarnaticExercise, work.subject[9:])
        return row.data if row else None
    return None


async def _rubric_questions(session: AsyncSession, work: PracticeWork) -> list[dict]:
    ex = await _exercise(session, work) or {}
    own = [q for q in (ex.get("rubric") or []) if isinstance(q, dict)]
    if work.room == "carnatic-analysis" and not own:
        return ANALYSIS_RUBRIC
    # Format 2 quotes the scale words; a YAML 1.1 reader could still hand us booleans.
    return [{**q, "scale": [("yes" if w is True else "no" if w is False else w) for w in q["scale"]]} if q.get("scale") else q
            for q in own]


def _sentences(text: str) -> list[str]:
    import re
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text or "") if x.strip()]


def _part_label(key: str, parts: dict[str, PracticePart]) -> str:
    if "@" in key:
        # A reply to one sentence of a part: "text@2" is the text's third sentence.
        base, _, n = key.partition("@")
        sent = _sentences(parts[base].body_md if base in parts else "")
        i = int(n) if n.isdigit() else -1
        if 0 <= i < len(sent):
            return f"on “{sent[i][:40]}{'…' if len(sent[i]) > 40 else ''}”"
        key = base
    p = parts.get(key)
    if key.startswith("note:") and p is not None:
        t = (p.data or {}).get("t")
        return f"the {t} note" if t else "one note"
    if key == "sargam":
        return "the notation"
    if key.startswith("quote:") and p is not None:
        return f"on “{p.body_md[:40]}”"
    return {"text": "the text", "summary": "the summary", "link": "the recording"}.get(key, key)


def _private_feedback(work: PracticeWork, parts: list[PracticePart], rec: CarnaticRecording | None,
                      ex: dict | None) -> dict | None:
    """Only for the author (LISTENING.md §4b; EXERCISES.md §3)."""
    out: dict = {}
    if rec is not None and rec.sections:
        marks = [p for p in parts if p.key.startswith("note:") and (p.data or {}).get("category") == "section"]
        times = [checks.seconds(str((p.data or {}).get("t", ""))) for p in marks]
        times = [t for t in times if t is not None]
        found = 0
        for s in rec.sections:
            ref = checks.seconds(str(s.get("t", "")))
            if ref is None:
                continue
            soft = any(w in str(s.get("label", "")).lower() for w in ("alapana", "tanam", "stage"))
            if any(abs(t - ref) <= (10 if soft else 6) for t in times):
                found += 1
        out["sectionsFound"], out["sectionsMarked"] = found, len(rec.sections)
    guess = next((p for p in parts if p.key == "guess"), None)
    if guess is not None and rec is not None and rec.raga:
        from shruti.api.routes.carnatic_course import _raga_matches
        out["guessRight"] = _raga_matches(str((guess.data or {}).get("raga", "")), rec.raga)
    pc = (ex or {}).get("private_check") or {}
    if pc.get("against") == "transcription":
        out["compare"] = "Shruti hasn't made a reference transcription for this one yet."
    return out or None


async def work_json(session: AsyncSession, work: PracticeWork, viewer: User | None, *, full: bool) -> dict:
    parts = (await session.execute(select(PracticePart).where(PracticePart.work_id == work.id)
                                   .order_by(PracticePart.id))).scalars().all()
    author = await session.get(User, work.user_id) if work.user_id else None
    votes = (await session.execute(select(func.count()).select_from(PracticeVote)
                                   .where(PracticeVote.work_id == work.id))).scalar_one()
    comments = (await session.execute(select(func.count()).select_from(PracticeComment).where(
        PracticeComment.work_id == work.id, PracticeComment.hidden.is_(False)))).scalar_one()
    mine = viewer is not None and work.user_id is not None and viewer.id == work.user_id
    out = {"id": work.id, "room": work.room, "subject": work.subject, "title": work.title,
           "author": _name(author), "authorId": work.user_id, "mine": mine,
           "submittedAt": _iso(work.submitted_at), "updatedAt": _iso(work.updated_at),
           "votes": votes, "comments": comments, "discussed": votes + 2 * comments,
           "hidden": work.hidden, "hiddenBy": work.hidden_by if (work.hidden and mine) else "",
           "excerpt": next((p.body_md[:220] for p in parts if p.key in ("text", "summary")), "")}
    if not full:
        return out
    out["parts"] = [{"key": p.key, "body": p.body_md, "data": p.data} for p in parts]
    out["voted"] = bool(viewer and (await session.execute(select(PracticeVote.id).where(
        PracticeVote.work_id == work.id, PracticeVote.user_id == viewer.id))).first())
    questions = await _rubric_questions(session, work)
    answers = (await session.execute(select(PracticeRubric).where(PracticeRubric.work_id == work.id))).scalars().all()
    totals: dict[str, dict[str, int]] = {}
    free: dict[str, int] = {}
    for q in questions:
        if q.get("scale"):
            totals[q["id"]] = {step: 0 for step in q["scale"]}
    for a in answers:
        for qid, value in (a.answers or {}).items():
            if qid in totals and value in totals[qid]:
                totals[qid][value] += 1
            elif value:
                free[qid] = free.get(qid, 0) + 1
    mine_answers = next((a.answers for a in answers if viewer and a.user_id == viewer.id), None)
    out["rubric"] = {"questions": questions, "totals": totals, "freeAnswers": free, "mine": mine_answers,
                     "answered": len(answers)}
    rec = None
    ex = await _exercise(session, work)
    rid = work.subject[10:] if work.subject.startswith("recording:") else \
        next((str(r.get("id")) for r in ((ex or {}).get("recordings") or []) if isinstance(r, dict)), None)
    if rid:
        rec = await session.get(CarnaticRecording, rid)
    out["private"] = _private_feedback(work, parts, rec, ex) if mine else None
    return out


async def _visible_work(session: AsyncSession, work_id: int, viewer: User | None) -> PracticeWork:
    work = await session.get(PracticeWork, work_id)
    mine = work is not None and viewer is not None and work.user_id == viewer.id
    if work is None or work.room not in ROOMS or (work.submitted_at is None and not mine):
        raise HTTPException(404, "No such piece.")
    if work.hidden and not mine:
        raise HTTPException(404, {"code": "NOT_AVAILABLE", "detail": "This piece isn't available."})
    if viewer is not None and work.user_id in await _hidden_from(session, viewer):
        raise HTTPException(404, {"code": "NOT_AVAILABLE", "detail": "This piece isn't available."})
    return work


# ── reading ─────────────────────────────────────────────────────────────────

@router.get("/works")
async def works(room: str, subject: str | None = None, sort: str = "new", before: int | None = None,
                mine: bool = False, viewer: User | None = Depends(current_user),
                session: AsyncSession = Depends(get_session)) -> dict:
    if room not in ROOMS:
        raise HTTPException(404, "No such room.")
    q = select(PracticeWork).where(PracticeWork.room == room)
    if mine:
        if viewer is None:
            raise HTTPException(401, "not signed in")
        q = q.where(PracticeWork.user_id == viewer.id)
    else:
        q = q.where(PracticeWork.submitted_at.is_not(None), PracticeWork.hidden.is_(False))
        hidden = await _hidden_from(session, viewer)
        if hidden:
            q = q.where(PracticeWork.user_id.not_in(hidden) | PracticeWork.user_id.is_(None))
    if subject:
        q = q.where(PracticeWork.subject == subject)
    if before and sort == "new":
        q = q.where(PracticeWork.id < before)
    rows = (await session.execute(q.order_by(PracticeWork.id.desc()).limit(300))).scalars().all()
    items = [await work_json(session, w, viewer, full=False) for w in rows]
    if sort == "discussed":
        items.sort(key=lambda w: (-w["discussed"], -w["id"]))
    page = items[:30]
    return {"items": page, "next": page[-1]["id"] if len(items) > 30 and sort == "new" else None}


@router.get("/works/{work_id}")
async def work(work_id: int, viewer: User | None = Depends(current_user),
               session: AsyncSession = Depends(get_session)) -> dict:
    w = await _visible_work(session, work_id, viewer)
    return await work_json(session, w, viewer, full=True)


# ── writing ─────────────────────────────────────────────────────────────────

class PartIn(BaseModel):
    key: str = Field(pattern=r"^(sargam|text|link|summary|guess|comparison|note:\d{1,3}|clip)$")
    body: str = Field(default="", max_length=12000)
    data: dict = Field(default_factory=dict)


class WorkIn(BaseModel):
    room: str
    subject: str = Field(max_length=120)
    title: str = Field(default="", max_length=160)
    parts: list[PartIn] = Field(default_factory=list, max_length=80)


class WorkEdit(BaseModel):
    title: str = Field(default="", max_length=160)
    parts: list[PartIn] = Field(default_factory=list, max_length=80)


async def _check_subject(session: AsyncSession, room: str, subject: str) -> None:
    if room == "carnatic-practice":
        ex = await session.get(CarnaticExercise, subject.removeprefix("exercise:"))
        if not subject.startswith("exercise:") or ex is None or ex.kind != "practice":
            raise HTTPException(422, "That isn't a practice piece.")
    elif room == "carnatic-analysis":
        if subject.startswith("exercise:"):
            # A lesson's listening analysis (kind: listening), about its `recordings`.
            ex = await session.get(CarnaticExercise, subject.removeprefix("exercise:"))
            if ex is None or ex.kind != "listening":
                raise HTTPException(422, "That isn't a listening analysis.")
            return
        rec = await session.get(CarnaticRecording, subject.removeprefix("recording:"))
        if not subject.startswith("recording:") or rec is None or rec.status not in ("approved", "retired"):
            raise HTTPException(422, "That recording isn't in the Listening room.")
    else:
        raise HTTPException(404, "No such room.")


async def _set_parts(session: AsyncSession, work: PracticeWork, parts: list[PartIn]) -> None:
    await session.execute(delete(PracticePart).where(PracticePart.work_id == work.id))
    for p in parts:
        data = dict(p.data)
        if p.key.startswith("note:") and data.get("category") not in NOTE_CATEGORIES:
            data["category"] = "other"
        if p.key == "link" and p.body:
            from shruti.core import carnatic as rules
            if rules.player_of(p.body) is None:
                raise HTTPException(422, "Link a YouTube, SoundCloud, Vimeo or Bandcamp recording.")
        session.add(PracticePart(work_id=work.id, key=p.key, body_md=p.body.strip(), data=data))


async def _mine(session: AsyncSession, work_id: int, user: User) -> PracticeWork:
    w = await session.get(PracticeWork, work_id)
    if w is None or w.room not in ROOMS or w.user_id != user.id:
        raise HTTPException(404, "No such piece.")
    return w


@router.post("/works", status_code=201)
async def create(body: WorkIn, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    await _refuse_if_suspended(session, user)
    await _check_subject(session, body.room, body.subject)
    w = PracticeWork(user_id=user.id, room=body.room, subject=body.subject, title=body.title.strip(),
                     period="", covers="")
    session.add(w)
    await session.flush()
    await _set_parts(session, w, body.parts)
    await session.commit()
    return await work_json(session, w, user, full=True)


@router.put("/works/{work_id}")
async def edit(work_id: int, body: WorkEdit, user: User = Depends(require_user),
               session: AsyncSession = Depends(get_session)) -> dict:
    await _refuse_if_suspended(session, user)
    w = await _mine(session, work_id, user)
    if w.submitted_at is not None:
        raise HTTPException(409, "A submitted piece can't be changed; withdraw it and write a new one.")
    w.title, w.updated_at = body.title.strip(), _now()
    await _set_parts(session, w, body.parts)
    await session.commit()
    return await work_json(session, w, user, full=True)


def hints_for(ex: dict | None, parts: list[PracticePart]) -> list[str]:
    """Prechecks and the word range, as friendly notes. They never block."""
    if not ex:
        return []
    out: list[str] = []
    sub = ex.get("submission") or {}
    text = next((p.body_md for p in parts if p.key == "text"), "")
    words = (sub.get("text") or {}).get("words")
    if isinstance(words, list) and len(words) == 2 and text:
        n = len(re.findall(r"\S+", text))
        if n < words[0]:
            out.append(f"The text is {n} words; this piece asks for {words[0]} to {words[1]}.")
        elif n > words[1]:
            out.append(f"The text is {n} words; this piece asks for {words[0]} to {words[1]}.")
    sargam = next((p for p in parts if p.key == "sargam"), None)
    spec = sub.get("sargam") or {}
    if sargam is not None and sargam.body_md:
        for pre in ex.get("prechecks") or []:
            out.extend(checks.precheck(pre, sargam.body_md, {**spec, **(sargam.data or {})}))
    for part in ("sargam", "text"):
        if (sub.get(part) or {}).get("required") and not next((p.body_md for p in parts if p.key == part), ""):
            out.append(f"This piece asks for {'notation' if part == 'sargam' else 'some text'}.")
    return out


@router.post("/works/{work_id}/submit")
async def submit(work_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    from shruti.core.publishing import require_publish_agreement
    await _refuse_if_suspended(session, user)
    w = await _mine(session, work_id, user)
    try:
        await require_publish_agreement(session, user)
    except HTTPException as e:
        if e.status_code == 428:
            return JSONResponse(status_code=428, content={"code": "PUBLISH_AGREEMENT_NEEDED", "detail": e.detail})
        raise
    parts = (await session.execute(select(PracticePart).where(PracticePart.work_id == w.id))).scalars().all()
    if not parts:
        raise HTTPException(422, "There's nothing in this piece yet.")
    hints = hints_for(await _exercise(session, w), parts)
    if w.submitted_at is None:
        w.submitted_at = _now()
    await session.commit()
    return {**(await work_json(session, w, user, full=True)), "hints": hints}


@router.post("/works/{work_id}/hints")
async def hints(work_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    w = await _mine(session, work_id, user)
    parts = (await session.execute(select(PracticePart).where(PracticePart.work_id == w.id))).scalars().all()
    return {"hints": hints_for(await _exercise(session, w), parts)}


@router.post("/works/{work_id}/withdraw")
async def withdraw(work_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    w = await _mine(session, work_id, user)
    w.hidden, w.hidden_by = True, "author"
    await session.commit()
    return {"ok": True}


@router.delete("/works/{work_id}", status_code=204)
async def remove_draft(work_id: int, user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)) -> Response:
    w = await _mine(session, work_id, user)
    if w.submitted_at is not None:
        raise HTTPException(409, "A submitted piece can be withdrawn, not deleted.")
    await session.delete(w)
    await session.commit()
    return Response(status_code=204)


# ── feedback ────────────────────────────────────────────────────────────────

@router.put("/works/{work_id}/vote")
async def vote(work_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    w = await _visible_work(session, work_id, user)
    if w.user_id == user.id:
        raise HTTPException(422, "That's your own piece.")
    if (await session.execute(select(PracticeVote.id).where(PracticeVote.work_id == w.id,
                                                            PracticeVote.user_id == user.id))).first() is None:
        session.add(PracticeVote(work_id=w.id, user_id=user.id))
        await session.commit()
    return {"voted": True}


@router.delete("/works/{work_id}/vote")
async def unvote(work_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    await session.execute(delete(PracticeVote).where(PracticeVote.work_id == work_id, PracticeVote.user_id == user.id))
    await session.commit()
    return {"voted": False}


class RubricIn(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


@router.put("/works/{work_id}/rubric")
async def rubric(work_id: int, body: RubricIn, user: User = Depends(require_user),
                 session: AsyncSession = Depends(get_session)) -> dict:
    await _refuse_if_suspended(session, user)
    w = await _visible_work(session, work_id, user)
    if w.user_id == user.id:
        raise HTTPException(422, "That's your own piece.")
    if w.user_id and await _blocked_by(session, author_id=w.user_id, speaker_id=user.id):
        raise HTTPException(403, "You can't answer this piece.")
    questions = {q["id"]: q for q in await _rubric_questions(session, w)}
    clean = {}
    for qid, value in body.answers.items():
        q = questions.get(qid)
        if q is None:
            continue
        if q.get("scale"):
            if value in q["scale"]:
                clean[qid] = value
        else:
            clean[qid] = value.strip()[:500]
    row = (await session.execute(select(PracticeRubric).where(PracticeRubric.work_id == w.id,
                                                              PracticeRubric.user_id == user.id))).scalar_one_or_none()
    if row is None:
        row = PracticeRubric(work_id=w.id, user_id=user.id, answers=clean)
        session.add(row)
    else:
        row.answers, row.updated_at = clean, _now()
    await session.commit()
    return (await work_json(session, w, user, full=True))["rubric"]


@router.get("/works/{work_id}/comments")
async def comments(work_id: int, viewer: User | None = Depends(current_user),
                   session: AsyncSession = Depends(get_session)) -> dict:
    w = await _visible_work(session, work_id, viewer)
    hidden = await _hidden_from(session, viewer)
    parts = {p.key: p for p in (await session.execute(select(PracticePart).where(
        PracticePart.work_id == w.id))).scalars().all()}
    rows = (await session.execute(select(PracticeComment).where(
        PracticeComment.work_id == w.id).order_by(PracticeComment.id))).scalars().all()
    out = []
    for c in rows:
        mine = viewer is not None and c.user_id == viewer.id
        if (c.hidden and not mine) or (c.user_id in hidden):
            continue
        author = await session.get(User, c.user_id) if c.user_id else None
        out.append({"id": c.id, "author": _name(author), "authorId": c.user_id, "mine": mine,
                    "part": c.sign or None, "partLabel": _part_label(c.sign, parts) if c.sign else None,
                    "body": c.body_md, "hidden": c.hidden and mine, "createdAt": _iso(c.created_at)})
    return {"items": out}


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    part: str | None = Field(default=None, max_length=40)


@router.post("/works/{work_id}/comments", status_code=201)
async def comment(work_id: int, body: CommentIn, user: User = Depends(require_user),
                  session: AsyncSession = Depends(get_session)) -> dict:
    await _refuse_if_suspended(session, user)
    w = await _visible_work(session, work_id, user)
    if w.submitted_at is None:
        raise HTTPException(409, "This piece isn't public yet.")
    if w.user_id and w.user_id != user.id and await _blocked_by(session, author_id=w.user_id, speaker_id=user.id):
        raise HTTPException(403, "You can't reply to this piece.")
    part = body.part or ""
    base, _, n = part.partition("@")
    if part and ((n and not n.isdigit()) or (await session.execute(select(PracticePart.id).where(
            PracticePart.work_id == w.id, PracticePart.key == base))).first() is None):
        raise HTTPException(422, "That part isn't in this piece.")
    c = PracticeComment(work_id=w.id, user_id=user.id, sign=part, body_md=body.body.strip())
    session.add(c)
    await session.commit()
    return {"id": c.id, "author": _name(user), "authorId": user.id, "mine": True, "part": part or None,
            "body": c.body_md, "createdAt": _iso(c.created_at)}


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user: User = Depends(require_user),
                         session: AsyncSession = Depends(get_session)) -> Response:
    c = await session.get(PracticeComment, comment_id)
    w = await session.get(PracticeWork, c.work_id) if c else None
    if c is None or w is None or w.room not in ROOMS or c.user_id != user.id:
        raise HTTPException(404, "No such comment.")
    await session.delete(c)
    await session.commit()
    return Response(status_code=204)


# ── reports and blocks ──────────────────────────────────────────────────────

class ReportIn(BaseModel):
    reason: str = Field(default="other", max_length=40)
    detail: str = Field(default="", max_length=1000)


async def _report(session: AsyncSession, user: User, body: ReportIn, *, work: PracticeWork | None = None,
                  comment: PracticeComment | None = None) -> dict:
    where = {"work_id": work.id} if work is not None else {"comment_id": comment.id}
    target = work if work is not None else comment
    already = (await session.execute(select(PracticeReport.id).filter_by(user_id=user.id, **where))).first()
    if already is None:
        reason = body.reason if body.reason in REASONS else "other"
        session.add(PracticeReport(user_id=user.id, reason=reason, detail=body.detail.strip(), **where))
        await session.flush()
        # Only open reports count: a thing she has reviewed and put back comes
        # down again only on three new reports.
        total = (await session.execute(select(func.count(func.distinct(PracticeReport.user_id))).select_from(
            PracticeReport).filter_by(**where).where(PracticeReport.reviewed_at.is_(None)))).scalar_one()
        if total >= REPORTS_TO_HIDE and not target.hidden:
            target.hidden, target.hidden_by = True, "reports"
        await session.commit()
    return {"reported": True}


@router.post("/works/{work_id}/report")
async def report_work(work_id: int, body: ReportIn, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)) -> dict:
    w = await _visible_work(session, work_id, user)
    return await _report(session, user, body, work=w)


@router.post("/comments/{comment_id}/report")
async def report_comment(comment_id: int, body: ReportIn, user: User = Depends(require_user),
                         session: AsyncSession = Depends(get_session)) -> dict:
    c = await session.get(PracticeComment, comment_id)
    w = await session.get(PracticeWork, c.work_id) if c else None
    if c is None or c.hidden or w is None or w.room not in ROOMS:
        raise HTTPException(404, "No such comment.")
    return await _report(session, user, body, comment=c)


@router.get("/reasons")
async def reasons() -> dict:
    return {"items": REASONS}


@router.get("/blocks")
async def blocks(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(PracticeBlock).where(PracticeBlock.user_id == user.id))).scalars().all()
    out = []
    for b in rows:
        u = await session.get(User, b.blocked_id)
        out.append({"userId": b.blocked_id, "name": _name(u)})
    return {"items": out}


class BlockIn(BaseModel):
    userId: int


@router.post("/blocks", status_code=201)
async def block(body: BlockIn, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    if body.userId == user.id:
        raise HTTPException(422, "That's you.")
    if await session.get(User, body.userId) is None:
        raise HTTPException(404, "No such person.")
    if not await _blocked_by(session, author_id=user.id, speaker_id=body.userId):
        session.add(PracticeBlock(user_id=user.id, blocked_id=body.userId))
        await session.commit()
    return {"blocked": True}


@router.delete("/blocks/{user_id}", status_code=204)
async def unblock(user_id: int, user: User = Depends(require_user),
                  session: AsyncSession = Depends(get_session)) -> Response:
    await session.execute(delete(PracticeBlock).where(PracticeBlock.user_id == user.id,
                                                      PracticeBlock.blocked_id == user_id))
    await session.commit()
    return Response(status_code=204)


# ── feedback on one's own pieces (SELF_TEST.md §5 item 5) ──────────────────

@router.get("/feedback")
async def my_feedback(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    """Replies, rubric answers and votes on the viewer's own pieces and analyses, newest first."""
    mine = (await session.execute(select(PracticeWork).where(
        PracticeWork.user_id == user.id, PracticeWork.room.in_(ROOMS), PracticeWork.submitted_at.is_not(None)))).scalars().all()
    if not mine:
        return {"items": []}
    ids = {w.id: w for w in mine}
    hidden = await _hidden_from(session, user)
    out: list[dict] = []
    for c in (await session.execute(select(PracticeComment).where(
            PracticeComment.work_id.in_(ids), PracticeComment.user_id != user.id, PracticeComment.hidden.is_(False))
            .order_by(PracticeComment.id.desc()).limit(20))).scalars().all():
        if c.user_id in hidden:
            continue
        author = await session.get(User, c.user_id) if c.user_id else None
        out.append({"kind": "reply", "work": c.work_id, "workTitle": ids[c.work_id].title, "who": _name(author),
                    "text": c.body_md[:120], "at": _iso(c.created_at)})
    for w in mine:
        answers = (await session.execute(select(PracticeRubric).where(PracticeRubric.work_id == w.id))).scalars().all()
        if answers:
            latest = max((a.updated_at or a.created_at for a in answers), default=None)
            out.append({"kind": "rubric", "work": w.id, "workTitle": w.title, "count": len(answers), "at": _iso(latest)})
        votes = (await session.execute(select(PracticeVote).where(PracticeVote.work_id == w.id)
                                       .order_by(PracticeVote.id.desc()))).scalars().all()
        if votes:
            out.append({"kind": "votes", "work": w.id, "workTitle": w.title, "count": len(votes),
                        "at": _iso(votes[0].created_at)})
    out.sort(key=lambda x: x.get("at") or "", reverse=True)
    return {"items": out[:12]}
