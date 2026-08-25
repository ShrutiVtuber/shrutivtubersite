# SPDX-License-Identifier: AGPL-3.0-only
"""
Who may open a course, and why.

The rule she asked for, stated once so nothing has to reimplement it:

  - Bought outright: theirs, for good.
  - Included with a membership: theirs while the membership lasts.
  - **Losing the membership takes the materials and leaves the progress.**

That last one is why permission and progress are separate tables. Nothing here
touches progress; it only ever answers "may they".
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models import Course, CourseTier, Entitlement


async def tier_keys_for(email: str, session: AsyncSession) -> set[str]:
    """
    The memberships this person is actually paying for right now.

    Read from the supporter record rather than from any entitlement, because
    the subscription is the truth and an entitlement is only its shadow.
    """
    from shruti.models import Supporter

    if not email:
        return set()
    rows = (
        await session.execute(select(Supporter).where(Supporter.email == email.lower()))
    ).scalars().all()
    return {r.tier for r in rows if r.tier}


async def may_open(user, course: Course, session: AsyncSession) -> tuple[bool, str]:
    """
    Whether this person may open this course, and how they came by it.

    Returns (allowed, reason) where reason is one of `purchase`, `ticket`,
    `gift`, `tier:<key>`, `free`, or "" — said out loud so a page can tell
    somebody *why* they have access, and so losing it later is explicable
    rather than mysterious.
    """
    if course.price_cents == 0 and not course.seats:
        # Given away. Nothing to check.
        return True, "free"

    if user is None:
        return False, ""

    granted = (
        await session.execute(
            select(Entitlement).where(
                Entitlement.user_id == user.id,
                Entitlement.course_id == course.id,
                Entitlement.revoked_at.is_(None),
            )
        )
    ).scalars().all()

    # Bought outright, given, or attended: permanent, and checked first so a
    # lapsed membership never hides a purchase somebody actually made.
    for row in granted:
        if row.source in {"purchase", "ticket", "gift"}:
            return True, row.source

    # Included with a membership: only while that membership is live. The
    # entitlement row is not proof on its own — a cancellation that has not
    # been swept up yet would otherwise keep the door open.
    if any(row.source == "tier" for row in granted):
        live = await tier_keys_for(getattr(user, "email", ""), session)
        for row in granted:
            if row.source == "tier" and row.tier_key in live:
                return True, f"tier:{row.tier_key}"

    return False, ""


async def sync_tier_entitlements(user, session: AsyncSession) -> dict:
    """
    Bring somebody's membership-granted access in line with what they pay for.

    Run when a subscription starts, changes or ends. Grants what their current
    memberships include and revokes what they no longer do — **and touches no
    progress whatsoever**, which is the point.

    Revoking stamps a date rather than deleting the row, so "why can I not open
    this any more" has an answer with a date on it.
    """
    email = (getattr(user, "email", "") or "").lower()
    live = await tier_keys_for(email, session)

    included: dict[int, str] = {}
    if live:
        rows = (
            await session.execute(
                select(CourseTier).where(CourseTier.tier_key.in_(live))
            )
        ).scalars().all()
        for row in rows:
            included[row.course_id] = row.tier_key

    existing = (
        await session.execute(
            select(Entitlement).where(
                Entitlement.user_id == user.id, Entitlement.source == "tier"
            )
        )
    ).scalars().all()
    by_course = {row.course_id: row for row in existing}

    granted = revoked = 0
    now = datetime.now(timezone.utc)

    for course_id, tier_key in included.items():
        row = by_course.get(course_id)
        if row is None:
            session.add(Entitlement(user_id=user.id, course_id=course_id,
                                    source="tier", tier_key=tier_key))
            granted += 1
        elif row.revoked_at is not None:
            # They came back. Their progress was never touched, so they land
            # where they left off.
            row.revoked_at = None
            row.tier_key = tier_key
            granted += 1

    for course_id, row in by_course.items():
        if course_id not in included and row.revoked_at is None:
            row.revoked_at = now
            revoked += 1

    await session.commit()
    return {"granted": granted, "revoked": revoked}


async def grant(user_id: int, course_id: int, source: str, session: AsyncSession,
                tier_key: str = "") -> Entitlement:
    """
    Give somebody a course. Idempotent — buying twice is one entitlement.

    A repeated Stripe webhook is the ordinary case rather than the exceptional
    one, so this has to be safe to call again.
    """
    row = (
        await session.execute(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.course_id == course_id,
                Entitlement.source == source,
            )
        )
    ).scalar_one_or_none()

    if row is None:
        row = Entitlement(user_id=user_id, course_id=course_id, source=source,
                          tier_key=tier_key)
        session.add(row)
    else:
        row.revoked_at = None
    await session.commit()
    await session.refresh(row)
    return row
