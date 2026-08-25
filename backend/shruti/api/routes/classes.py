# SPDX-License-Identifier: AGPL-3.0-only
"""
Classes and workshops, as a reader sees them.

**The outline is public; the content is not.** Anybody can see what a course
contains — every module, every lesson, its type and its length — before paying
for it, because that list is the thing that sells the course. What they cannot
see without buying it is the video, the text, the file or the questions.

That split runs through every response here: a lesson always says what it is,
and only says what it holds when somebody may open it.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.access import may_open
from shruti.core.db import get_session
from shruti.models import (
    Course, Enrolment, Lesson, LessonProgress, Media, Module, QuizQuestion,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/classes", tags=["classes"])


def _course_card(c: Course, media: Media | None) -> dict:
    from shruti.core.storage import public_url

    return {
        "slug": c.slug,
        "title": c.title,
        "kind": c.kind,
        "tagline": c.tagline,
        "priceCents": c.price_cents,
        "currency": c.currency,
        "startsAt": c.starts_at.isoformat() if c.starts_at else None,
        "minutes": c.minutes,
        "seats": c.seats,
        "media": None if media is None else {
            "url": public_url(media.filename, media.storage_backend),
            "alt": media.alt_text,
        },
    }


@router.get("")
async def list_courses(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(
            select(Course, Media)
            .join(Media, Course.media_id == Media.id, isouter=True)
            .where(Course.visible.is_(True))
            .order_by(Course.position, Course.id)
        )
    ).all()
    return [_course_card(c, m) for c, m in rows]


@router.get("/{slug}")
async def read_course(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    A course, its outline, and how far this reader got.

    Returned to everybody. What changes with access is whether each lesson
    carries its content — never whether it is listed, because a hidden
    curriculum is a worse sales page and a worse promise.
    """
    from shruti.api.routes.accounts import current_user

    row = (
        await session.execute(
            select(Course, Media)
            .join(Media, Course.media_id == Media.id, isouter=True)
            .where(Course.slug == slug, Course.visible.is_(True))
        )
    ).first()
    if row is None:
        raise HTTPException(404, "no such course")
    course, media = row

    user = await current_user(request, session)
    allowed, reason = await may_open(user, course, session)

    modules = (
        await session.execute(
            select(Module).where(Module.course_id == course.id)
            .order_by(Module.position, Module.id)
        )
    ).scalars().all()
    lessons = (
        await session.execute(
            select(Lesson).where(Lesson.module_id.in_([m.id for m in modules] or [0]))
            .order_by(Lesson.position, Lesson.id)
        )
    ).scalars().all()

    done: set[int] = set()
    last_lesson: int | None = None
    if user is not None:
        done = {
            p.lesson_id
            for p in (
                await session.execute(
                    select(LessonProgress).where(
                        LessonProgress.user_id == user.id,
                        LessonProgress.lesson_id.in_([l.id for l in lessons] or [0]),
                        LessonProgress.completed_at.is_not(None),
                    )
                )
            ).scalars().all()
        }
        enrolment = (
            await session.execute(
                select(Enrolment).where(
                    Enrolment.user_id == user.id, Enrolment.course_id == course.id
                )
            )
        ).scalar_one_or_none()
        last_lesson = enrolment.last_lesson_id if enrolment else None

    by_module: dict[int, list[dict]] = {}
    for lesson in lessons:
        by_module.setdefault(lesson.module_id, []).append({
            "id": lesson.id,
            "title": lesson.title,
            "kind": lesson.kind,
            "minutes": round(lesson.duration_seconds / 60) if lesson.duration_seconds else None,
            "freePreview": lesson.free_preview,
            "done": lesson.id in done,
            # What they may actually open. A free preview is openable by
            # anybody, which is the point of one.
            "open": allowed or lesson.free_preview,
        })

    outline = [
        {
            "id": m.id,
            "title": m.title,
            "lessons": by_module.get(m.id, []),
            "done": sum(1 for l in by_module.get(m.id, []) if l["done"]),
            "count": len(by_module.get(m.id, [])),
        }
        for m in modules
    ]
    total = sum(m["count"] for m in outline)

    return {
        **_course_card(course, media),
        "bodyMd": course.body_md,
        "access": {"allowed": allowed, "reason": reason, "signedIn": user is not None},
        "modules": outline,
        "progress": {"done": len(done), "total": total,
                     "lastLessonId": last_lesson},
    }


@router.get("/{slug}/lessons/{lesson_id}")
async def read_lesson(
    slug: str, lesson_id: int, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    One lesson's actual content.

    **The only door.** Everything a paying reader gets — the playback token,
    the file, the questions — comes through here and through the access check
    above it, so there is one place to be right rather than one per lesson
    type.
    """
    from shruti.api.routes.accounts import current_user

    course = (
        await session.execute(select(Course).where(Course.slug == slug))
    ).scalar_one_or_none()
    lesson = await session.get(Lesson, lesson_id)
    if course is None or lesson is None:
        raise HTTPException(404, "no such lesson")

    module = await session.get(Module, lesson.module_id)
    if module is None or module.course_id != course.id:
        # The lesson exists and belongs to something else. Saying "no such
        # lesson" rather than "wrong course" keeps the id from being a way to
        # enumerate what else is here.
        raise HTTPException(404, "no such lesson")

    user = await current_user(request, session)
    allowed, reason = await may_open(user, course, session)
    if not (allowed or lesson.free_preview):
        raise HTTPException(
            403,
            "this lesson is part of a class you do not have yet"
            if user else "sign in to open this",
        )

    body: dict = {
        "id": lesson.id,
        "title": lesson.title,
        "kind": lesson.kind,
        "bodyMd": lesson.body_md,
        "minutes": round(lesson.duration_seconds / 60) if lesson.duration_seconds else None,
        "freePreview": lesson.free_preview,
        "grantedBy": reason,
    }

    if lesson.kind == "video" and lesson.video_id:
        from shruti.core.video import playback

        body["video"] = playback(lesson.video_provider, lesson.video_id)

    if lesson.kind in {"pdf", "audio"} and lesson.file_id:
        # Handed over by the same guarded route a bought file uses, so a
        # course file is no more reachable than a purchased one.
        body["file"] = {"url": f"/api/classes/{slug}/lessons/{lesson.id}/file"}

    if lesson.kind == "quiz":
        questions = (
            await session.execute(
                select(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)
                .order_by(QuizQuestion.position, QuizQuestion.id)
            )
        ).scalars().all()
        # Answers come with the questions on purpose: these are self-checks,
        # nothing is scored, and holding the answer back would mean a round
        # trip to be told something nobody is marking.
        body["questions"] = [
            {
                "id": q.id,
                "prompt": q.prompt,
                "choices": [c for c in q.choices.splitlines() if c.strip()],
                "answerIndex": q.answer_index,
                "explanation": q.explanation,
            }
            for q in questions
        ]

    return body


class ProgressIn(BaseModel):
    seconds: int | None = None
    done: bool | None = None


@router.post("/{slug}/lessons/{lesson_id}/progress")
async def mark_progress(
    slug: str, lesson_id: int, body: ProgressIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Remember where they are.

    **Recorded for anybody signed in who may open the lesson**, and never
    removed afterwards. Somebody whose membership lapses keeps every tick, so
    coming back is coming back rather than starting again.
    """
    from datetime import datetime, timezone

    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "not signed in")

    course = (
        await session.execute(select(Course).where(Course.slug == slug))
    ).scalar_one_or_none()
    lesson = await session.get(Lesson, lesson_id)
    if course is None or lesson is None:
        raise HTTPException(404, "no such lesson")

    allowed, _reason = await may_open(user, course, session)
    if not (allowed or lesson.free_preview):
        raise HTTPException(403, "not yours to mark")

    row = (
        await session.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id == lesson.id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        row = LessonProgress(user_id=user.id, lesson_id=lesson.id)
        session.add(row)

    if body.seconds is not None:
        # Only ever forwards. A rewatch that starts from the beginning must not
        # lose the furthest point somebody reached.
        row.seconds_watched = max(row.seconds_watched, body.seconds)
    if body.done is True and row.completed_at is None:
        row.completed_at = datetime.now(timezone.utc)
    if body.done is False:
        row.completed_at = None

    enrolment = (
        await session.execute(
            select(Enrolment).where(
                Enrolment.user_id == user.id, Enrolment.course_id == course.id
            )
        )
    ).scalar_one_or_none()
    if enrolment is None:
        enrolment = Enrolment(user_id=user.id, course_id=course.id)
        session.add(enrolment)
    enrolment.last_lesson_id = lesson.id

    await session.commit()
    return {"ok": True, "done": row.completed_at is not None,
            "seconds": row.seconds_watched}
