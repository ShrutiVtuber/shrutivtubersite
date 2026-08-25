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

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
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


# ── building one ────────────────────────────────────────────────────────────
#
# Declared after the reader's routes but before nothing — this router has no
# catch-alls, so `/admin/...` cannot be swallowed by `/{slug}`: they differ in
# their first segment, and `admin` is a literal.

class CourseIn(BaseModel):
    slug: str
    title: str
    kind: str = "class"
    tagline: str = ""
    body_md: str = ""
    media_id: int | None = None
    price_cents: int = 0
    currency: str = "eur"
    tax_code: str = "txcd_10000000"
    starts_at: str | None = None
    minutes: int | None = None
    seats: int | None = None
    visible: bool = False
    position: int = 0


def _admin_course(c: Course, tiers: list[str], counts: tuple[int, int]) -> dict:
    modules, lessons = counts
    return {
        "id": c.id, "slug": c.slug, "title": c.title, "kind": c.kind,
        "tagline": c.tagline, "body_md": c.body_md, "media_id": c.media_id,
        "price_cents": c.price_cents, "currency": c.currency,
        "tax_code": c.tax_code,
        "starts_at": c.starts_at.isoformat() if c.starts_at else None,
        "minutes": c.minutes, "seats": c.seats, "room_name": c.room_name,
        "visible": c.visible, "position": c.position,
        "includedWith": tiers,
        "modules": modules, "lessons": lessons,
        "stripePriceId": c.stripe_price_id,
        # Free courses need no Stripe price; paid ones cannot be bought
        # without one, and saying so beats a buy button that 503s.
        "sellable": c.price_cents == 0 or bool(c.stripe_price_id),
    }


@router.get("/admin/courses", dependencies=[Depends(require_admin)])
async def admin_courses(session: AsyncSession = Depends(get_session)) -> list[dict]:
    from shruti.models import CourseTier

    rows = (
        await session.execute(select(Course).order_by(Course.position, Course.id))
    ).scalars().all()
    tiers: dict[int, list[str]] = {}
    for link in (await session.execute(select(CourseTier))).scalars().all():
        tiers.setdefault(link.course_id, []).append(link.tier_key)

    modules = (await session.execute(select(Module))).scalars().all()
    by_course: dict[int, list[int]] = {}
    for m in modules:
        by_course.setdefault(m.course_id, []).append(m.id)
    lessons = (await session.execute(select(Lesson))).scalars().all()
    per_module: dict[int, int] = {}
    for l in lessons:
        per_module[l.module_id] = per_module.get(l.module_id, 0) + 1

    return [
        _admin_course(
            c, sorted(tiers.get(c.id, [])),
            (len(by_course.get(c.id, [])),
             sum(per_module.get(mid, 0) for mid in by_course.get(c.id, []))),
        )
        for c in rows
    ]


async def _sync_course(row: Course, session: AsyncSession) -> dict:
    """
    Keep a paid course in step with Stripe. A free one needs nothing there.
    """
    from shruti.core import shop as stripe_shop
    from shruti.models import CourseTier

    tiers = sorted(
        link.tier_key
        for link in (
            await session.execute(
                select(CourseTier).where(CourseTier.course_id == row.id)
            )
        ).scalars().all()
    )
    counts = (0, 0)

    if row.price_cents <= 0:
        return _admin_course(row, tiers, counts)

    try:
        product_id, price_id = stripe_shop.sync(row)
    except Exception as exc:                           # noqa: BLE001
        log.warning("course %s could not be synced: %s", row.slug, type(exc).__name__)
        return _admin_course(row, tiers, counts) | {
            "stripeError": f"{type(exc).__name__}: {exc}"
        }
    row.stripe_product_id, row.stripe_price_id = product_id, price_id
    await session.commit()
    await session.refresh(row)
    return _admin_course(row, tiers, counts)


@router.post("/admin/courses", status_code=201, dependencies=[Depends(require_admin)])
async def create_course(
    body: CourseIn, session: AsyncSession = Depends(get_session)
) -> dict:
    from datetime import datetime

    if body.kind not in {"class", "workshop"}:
        raise HTTPException(422, "a course is a class or a workshop")

    starts = None
    if body.starts_at:
        try:
            starts = datetime.fromisoformat(body.starts_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(422, "that start time is not one I can read")

    row = Course(**body.model_dump(exclude={"starts_at"}), starts_at=starts)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return await _sync_course(row, session)


@router.patch("/admin/courses/{course_id}", dependencies=[Depends(require_admin)])
async def update_course(
    course_id: int, body: dict, session: AsyncSession = Depends(get_session)
) -> dict:
    from datetime import datetime

    row = await session.get(Course, course_id)
    if row is None:
        raise HTTPException(404, "no such course")

    for key, value in body.items():
        if key in {"id", "created_at", "stripe_product_id", "stripe_price_id"}:
            continue
        if key == "starts_at":
            if value:
                try:
                    value = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                except ValueError:
                    raise HTTPException(422, "that start time is not one I can read")
            else:
                value = None
        if hasattr(row, key):
            setattr(row, key, value)
    await session.commit()
    await session.refresh(row)
    return await _sync_course(row, session)


@router.delete("/admin/courses/{course_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_course(course_id: int, session: AsyncSession = Depends(get_session)):
    """
    Remove a course nobody holds.

    **Refused once anybody has it.** Their entitlement points here, and so does
    every tick of their progress — deleting it would take away something
    somebody paid for and lose the record that they ever had it. Hide it
    instead: nobody new can find it, everybody who has it keeps it.
    """
    from shruti.models import Entitlement

    row = await session.get(Course, course_id)
    if row is None:
        raise HTTPException(404, "no such course")

    held = (
        await session.execute(
            select(Entitlement).where(Entitlement.course_id == course_id)
        )
    ).scalars().first()
    if held is not None:
        raise HTTPException(
            409,
            "somebody has this, so it cannot be deleted \u2014 their access and "
            "everything they have worked through points at it. Untick "
            "\u201cpublished\u201d instead: nobody new can find it and everybody "
            "who has it keeps it.",
        )

    for module in (
        await session.execute(select(Module).where(Module.course_id == course_id))
    ).scalars().all():
        for lesson in (
            await session.execute(select(Lesson).where(Lesson.module_id == module.id))
        ).scalars().all():
            await session.execute(
                QuizQuestion.__table__.delete().where(
                    QuizQuestion.lesson_id == lesson.id
                )
            )
            await session.delete(lesson)
        await session.delete(module)
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


class TiersIn(BaseModel):
    """Which memberships include this. Sent whole, not one at a time."""

    tier_keys: list[str]


@router.put("/admin/courses/{course_id}/tiers", dependencies=[Depends(require_admin)])
async def set_course_tiers(
    course_id: int, body: TiersIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Say which memberships include this course.

    **Changing it does not reach into anybody's access here.** Entitlements are
    brought in line when a subscription is next looked at, which keeps one
    place responsible for granting and revoking rather than two that can
    disagree.
    """
    from shruti.models import CourseTier

    course = await session.get(Course, course_id)
    if course is None:
        raise HTTPException(404, "no such course")

    await session.execute(
        CourseTier.__table__.delete().where(CourseTier.course_id == course_id)
    )
    for key in {k.strip() for k in body.tier_keys if k.strip()}:
        session.add(CourseTier(course_id=course_id, tier_key=key))
    await session.commit()
    return {"ok": True, "includedWith": sorted(set(body.tier_keys))}


# ── modules and lessons ─────────────────────────────────────────────────────

class ModuleIn(BaseModel):
    title: str
    position: int = 0


@router.get("/admin/courses/{course_id}/outline", dependencies=[Depends(require_admin)])
async def admin_outline(
    course_id: int, session: AsyncSession = Depends(get_session)
) -> list[dict]:
    modules = (
        await session.execute(
            select(Module).where(Module.course_id == course_id)
            .order_by(Module.position, Module.id)
        )
    ).scalars().all()
    lessons = (
        await session.execute(
            select(Lesson).where(Lesson.module_id.in_([m.id for m in modules] or [0]))
            .order_by(Lesson.position, Lesson.id)
        )
    ).scalars().all()

    counts = {
        q.lesson_id: 0 for q in (
            await session.execute(select(QuizQuestion))
        ).scalars().all()
    }
    for q in (await session.execute(select(QuizQuestion))).scalars().all():
        counts[q.lesson_id] = counts.get(q.lesson_id, 0) + 1

    by_module: dict[int, list[dict]] = {}
    for l in lessons:
        by_module.setdefault(l.module_id, []).append({
            "id": l.id, "title": l.title, "kind": l.kind, "position": l.position,
            "body_md": l.body_md,
            "video_provider": l.video_provider, "video_id": l.video_id,
            "duration_seconds": l.duration_seconds,
            "file_id": l.file_id, "free_preview": l.free_preview,
            "questions": counts.get(l.id, 0),
            # A video lesson with no video is the commonest half-finished
            # state, and the one that looks fine in a list.
            "incomplete": l.kind == "video" and not l.video_id,
        })

    return [
        {"id": m.id, "title": m.title, "position": m.position,
         "lessons": by_module.get(m.id, [])}
        for m in modules
    ]


@router.post("/admin/courses/{course_id}/modules", status_code=201,
             dependencies=[Depends(require_admin)])
async def create_module(
    course_id: int, body: ModuleIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if await session.get(Course, course_id) is None:
        raise HTTPException(404, "no such course")
    existing = (
        await session.execute(select(Module).where(Module.course_id == course_id))
    ).scalars().all()
    row = Module(course_id=course_id, title=body.title,
                 position=body.position or (max((m.position for m in existing), default=0) + 10))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "title": row.title, "position": row.position}


@router.patch("/admin/modules/{module_id}", dependencies=[Depends(require_admin)])
async def update_module(
    module_id: int, body: dict, session: AsyncSession = Depends(get_session)
) -> dict:
    row = await session.get(Module, module_id)
    if row is None:
        raise HTTPException(404, "no such module")
    for key, value in body.items():
        if key in {"id", "course_id", "created_at"}:
            continue
        if hasattr(row, key):
            setattr(row, key, value)
    await session.commit()
    return {"ok": True}


@router.delete("/admin/modules/{module_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_module(module_id: int, session: AsyncSession = Depends(get_session)):
    """Removes its lessons with it — an orphan lesson belongs nowhere."""
    row = await session.get(Module, module_id)
    if row is None:
        raise HTTPException(404, "no such module")
    for lesson in (
        await session.execute(select(Lesson).where(Lesson.module_id == module_id))
    ).scalars().all():
        await session.execute(
            QuizQuestion.__table__.delete().where(QuizQuestion.lesson_id == lesson.id)
        )
        await session.delete(lesson)
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


class LessonIn(BaseModel):
    title: str
    kind: str = "video"
    position: int = 0
    body_md: str = ""
    video_provider: str = ""
    video_id: str = ""
    duration_seconds: int | None = None
    file_id: int | None = None
    free_preview: bool = False


LESSON_KINDS = {"video", "text", "audio", "pdf", "quiz"}


@router.post("/admin/modules/{module_id}/lessons", status_code=201,
             dependencies=[Depends(require_admin)])
async def create_lesson(
    module_id: int, body: LessonIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if body.kind not in LESSON_KINDS:
        raise HTTPException(422, f"a lesson is one of {sorted(LESSON_KINDS)}")
    if await session.get(Module, module_id) is None:
        raise HTTPException(404, "no such module")
    existing = (
        await session.execute(select(Lesson).where(Lesson.module_id == module_id))
    ).scalars().all()
    row = Lesson(
        module_id=module_id,
        **body.model_dump(exclude={"position"}),
        position=body.position or (max((l.position for l in existing), default=0) + 10),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "title": row.title, "kind": row.kind}


@router.patch("/admin/lessons/{lesson_id}", dependencies=[Depends(require_admin)])
async def update_lesson(
    lesson_id: int, body: dict, session: AsyncSession = Depends(get_session)
) -> dict:
    row = await session.get(Lesson, lesson_id)
    if row is None:
        raise HTTPException(404, "no such lesson")
    if body.get("kind") and body["kind"] not in LESSON_KINDS:
        raise HTTPException(422, f"a lesson is one of {sorted(LESSON_KINDS)}")
    for key, value in body.items():
        if key in {"id", "module_id", "created_at"}:
            continue
        if hasattr(row, key):
            setattr(row, key, value)
    await session.commit()
    return {"ok": True}


@router.delete("/admin/lessons/{lesson_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_lesson(lesson_id: int, session: AsyncSession = Depends(get_session)):
    """
    Remove a lesson, and the ticks against it.

    Progress is kept everywhere else in this system on purpose; here it cannot
    be, because a tick against a lesson that no longer exists is not a record
    of anything. The video at the provider is untouched — deleting a lesson
    should not delete a master.
    """
    row = await session.get(Lesson, lesson_id)
    if row is None:
        raise HTTPException(404, "no such lesson")
    await session.execute(
        QuizQuestion.__table__.delete().where(QuizQuestion.lesson_id == lesson_id)
    )
    await session.execute(
        LessonProgress.__table__.delete().where(LessonProgress.lesson_id == lesson_id)
    )
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


class QuestionIn(BaseModel):
    prompt: str
    choices: str = ""
    answer_index: int = 0
    explanation: str = ""
    position: int = 0


@router.get("/admin/lessons/{lesson_id}/questions", dependencies=[Depends(require_admin)])
async def admin_questions(
    lesson_id: int, session: AsyncSession = Depends(get_session)
) -> list[dict]:
    rows = (
        await session.execute(
            select(QuizQuestion).where(QuizQuestion.lesson_id == lesson_id)
            .order_by(QuizQuestion.position, QuizQuestion.id)
        )
    ).scalars().all()
    return [
        {"id": q.id, "prompt": q.prompt, "choices": q.choices,
         "answer_index": q.answer_index, "explanation": q.explanation,
         "position": q.position}
        for q in rows
    ]


@router.post("/admin/lessons/{lesson_id}/questions", status_code=201,
             dependencies=[Depends(require_admin)])
async def create_question(
    lesson_id: int, body: QuestionIn, session: AsyncSession = Depends(get_session)
) -> dict:
    lesson = await session.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(404, "no such lesson")
    choices = [c for c in body.choices.splitlines() if c.strip()]
    if len(choices) < 2:
        raise HTTPException(422, "a question needs at least two answers to choose between")
    if not 0 <= body.answer_index < len(choices):
        raise HTTPException(422, "the right answer is not one of the choices")

    existing = (
        await session.execute(
            select(QuizQuestion).where(QuizQuestion.lesson_id == lesson_id)
        )
    ).scalars().all()
    row = QuizQuestion(
        lesson_id=lesson_id,
        **body.model_dump(exclude={"position"}),
        position=body.position or (max((q.position for q in existing), default=0) + 10),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id}


@router.delete("/admin/questions/{question_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_question(
    question_id: int, session: AsyncSession = Depends(get_session)
):
    row = await session.get(QuizQuestion, question_id)
    if row is None:
        raise HTTPException(404, "no such question")
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


# ── buying one ──────────────────────────────────────────────────────────────

class EnrolIn(BaseModel):
    slug: str


@router.post("/enrol")
async def enrol(
    body: EnrolIn, request: Request, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Take a class: pay for it, or claim a free place.

    Signing in first is required and not negotiable — a class is something
    somebody comes back to for years, and there is nowhere to put an
    entitlement without an account to hang it on.

    A free course with seats is an RSVP rather than a purchase: no money moves,
    a ticket is issued, and the seat count goes down so she knows how many are
    coming.
    """
    from shruti.api.routes.accounts import current_user
    from shruti.core.access import grant, may_open

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in first — a class needs somewhere to live")

    course = (
        await session.execute(
            select(Course).where(Course.slug == body.slug, Course.visible.is_(True))
        )
    ).scalar_one_or_none()
    if course is None:
        raise HTTPException(404, "no such course")

    already, reason = await may_open(user, course, session)
    if already:
        return {"ok": True, "alreadyYours": True, "reason": reason}

    taken = await _seats_taken(course.id, session)
    if course.seats is not None and taken >= course.seats:
        raise HTTPException(409, "there are no places left")

    # Free, but counted: an RSVP.
    if course.price_cents <= 0:
        await grant(user.id, course.id,
                    "ticket" if course.kind == "workshop" else "gift", session)
        return {"ok": True, "granted": True, "paid": False}

    if not course.stripe_price_id:
        raise HTTPException(503, "this is not finished being set up")

    from shruti.api.routes.billing import _site_url
    from shruti.core import shop as stripe_shop

    site = _site_url(request)
    stripe = stripe_shop._client()
    args = {
        "mode": "payment",
        "line_items": [{"price": course.stripe_price_id, "quantity": 1}],
        "success_url": f"{site}/classes/{course.slug}?welcome=1",
        "cancel_url": f"{site}/classes/{course.slug}",
        "automatic_tax": {"enabled": True},
        "allow_promotion_codes": True,
        # The webhook needs to know who this is for. The reference survives the
        # redirect and is not something the browser can rewrite on the way back.
        "client_reference_id": str(user.id),
        "metadata": {"course_slug": course.slug, "kind": course.kind},
    }
    if user.email:
        args["customer_email"] = user.email

    return {"ok": True, "url": stripe.checkout.Session.create(**args)["url"]}


async def _seats_taken(course_id: int, session: AsyncSession) -> int:
    """
    How many places are gone.

    Counts entitlements rather than orders, because a place given away and a
    place sold both fill a room.
    """
    from shruti.models import Entitlement

    rows = (
        await session.execute(
            select(Entitlement).where(
                Entitlement.course_id == course_id,
                Entitlement.revoked_at.is_(None),
            )
        )
    ).scalars().all()
    return len(rows)


async def record_enrolment(event_object: dict, session: AsyncSession):
    """
    Grant a course from a completed checkout.

    Called by the webhook and idempotent through `grant`, because Stripe
    retries by design and somebody must not end up with two of anything — nor,
    worse, with nothing because the second attempt raised.
    """
    from shruti.core.access import grant

    slug = (event_object.get("metadata") or {}).get("course_slug") or ""
    reference = event_object.get("client_reference_id")
    if not slug or not reference or not str(reference).isdigit():
        return None

    course = (
        await session.execute(select(Course).where(Course.slug == slug))
    ).scalar_one_or_none()
    if course is None:
        return None

    return await grant(
        int(reference), course.id,
        "ticket" if course.kind == "workshop" else "purchase",
        session,
    )


# ── what a reader sees ──────────────────────────────────────────────────────
#
# Declared AFTER the admin routes, and that is not stylistic. `/{slug}` sits in
# the same position as `admin`, so a parameter here eats the literal there —
# `/api/classes/admin/lessons/5` would be read as the lesson 5 of a course
# called "admin". Today only the accident that one is GET and the other PATCH
# keeps them apart; declaring these last means it does not depend on that.

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


@router.get("/{slug}/lessons/{lesson_id}/file")
async def lesson_file(
    slug: str, lesson_id: int, request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    The PDF or the audio a lesson hands over.

    Guarded by the same check as the lesson itself, and served from the same
    store a bought product file uses — a course file is no more reachable than
    a purchased one, and neither is reachable by guessing a name.
    """
    from shruti.api.routes.accounts import current_user
    from shruti.models import ProductFile

    course = (
        await session.execute(select(Course).where(Course.slug == slug))
    ).scalar_one_or_none()
    lesson = await session.get(Lesson, lesson_id)
    if course is None or lesson is None:
        raise HTTPException(404, "no such lesson")

    module = await session.get(Module, lesson.module_id)
    if module is None or module.course_id != course.id:
        raise HTTPException(404, "no such lesson")

    user = await current_user(request, session)
    allowed, _reason = await may_open(user, course, session)
    if not (allowed or lesson.free_preview):
        raise HTTPException(
            403,
            "this is part of a class you do not have yet"
            if user else "sign in to open this",
        )

    if not lesson.file_id:
        raise HTTPException(404, "there is no file on this lesson")
    row = await session.get(ProductFile, lesson.file_id)
    if row is None:
        raise HTTPException(410, "the file is missing; please write and it will be sorted out")

    from shruti.core.storage import fetch

    found = await fetch(row.stored_name)
    if found is None:
        raise HTTPException(410, "the file is missing; please write and it will be sorted out")

    data, content_type = found
    return Response(
        content=data,
        media_type=content_type or row.mime_type or "application/octet-stream",
        headers={
            # The name she uploaded, not the hash it is stored under.
            "Content-Disposition": f'attachment; filename="{row.original_name}"',
            # One person's course material. Nothing in between should keep it.
            "Cache-Control": "private, no-store",
        },
    )


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
