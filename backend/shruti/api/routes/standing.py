# SPDX-License-Identifier: AGPL-3.0-only
"""
Standing compatibility tests.

Two things, and the second is the business one:

- **"Are you compatible with Shruti?"** — hers, permanent, no account needed to
  take it. A share hook.
- **Another VTuber's**, against their own chart, for a run their tier decides:
  five days, ten days, or permanent.

⚠ **The expiry is the part that goes wrong quietly.** An expired test that keeps
answering is a feature given away; one that 404s with no explanation is a VTuber
who thinks the site is broken. So every read checks, and an expired one still
answers — with when it ran and what would keep it up.
"""
from __future__ import annotations

import logging
import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.db import get_session
from shruti.core.standing import expires_at, has_run_out, what_would_keep_it
from shruti.models.accounts import SavedChart, StandingTest, Supporter, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/standing", tags=["standing"])

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")
# Addresses that would collide with a page, or claim to be her.
RESERVED = {"shruti", "admin", "api", "new", "me", "account", "about"}


async def _tier_of(user: User | None, session: AsyncSession) -> str:
    """What this person pays, right now. Empty for nobody and for a lapsed one."""
    if user is None:
        return ""
    row = (
        await session.execute(select(Supporter).where(Supporter.user_id == user.id))
    ).scalars().first()
    if row is None or row.status not in {"active", "trialing"}:
        return ""
    return row.tier or ""


def _public(test: StandingTest, chart: SavedChart | None) -> dict:
    ended = has_run_out(test.expires_at)
    return {
        "slug": test.slug,
        "host": test.host_name,
        "blurb": test.blurb,
        # ⚠ Never the birth data. A standing test is a public address; the
        # chart behind it belongs to its host and only the ASPECTS come out.
        "hasChart": chart is not None,
        "expiresAt": test.expires_at.isoformat() if test.expires_at else None,
        "permanent": test.expires_at is None,
        "running": not ended and not test.hidden and chart is not None,
        "ranOut": ended,
        # Never a dead end. Empty where there is nothing to sell.
        "wouldKeepIt": what_would_keep_it(test.tier_at_setup) if ended else "",
    }


@router.get("")
async def running(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Every test still answering. Hers first, then newest."""
    rows = (
        await session.execute(
            select(StandingTest)
            .where(StandingTest.hidden.is_(False))
            .order_by(StandingTest.user_id.is_(None).desc(),
                      StandingTest.created_at.desc())
        )
    ).scalars().all()
    out = []
    for test in rows:
        if has_run_out(test.expires_at):
            continue
        chart = await session.get(SavedChart, test.chart_id)
        if chart is None:
            continue
        out.append(_public(test, chart))
    return out


class SetUpIn(BaseModel):
    # The chart to test against: an owner token they already hold.
    chart: str
    slug: str = Field(default="", max_length=40)
    host_name: str = Field(default="", max_length=60)
    blurb: str = Field(default="", max_length=280)


@router.post("", status_code=201)
async def set_up(
    body: SetUpIn, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Put one up against a chart you hold.

    The run comes from the tier at this moment and is then FIXED — see the note
    on the model. Cancelling later does not shorten a run already bought, and
    upgrading does not lengthen it; that is what taking it down and putting it
    back up is for.
    """
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    if user is None:
        raise HTTPException(401, "sign in to put up a test")

    chart = (
        await session.execute(
            select(SavedChart).where(SavedChart.owner_token == body.chart)
        )
    ).scalars().first()
    if chart is None:
        raise HTTPException(404, "that chart could not be found")
    # ⚠ Theirs, not merely one they have a link to. A standing test names a
    # host, and naming somebody else's chart as your own is the obvious abuse.
    if chart.user_id != user.id:
        raise HTTPException(403, "that chart is not on your account")

    slug = (body.slug or "").strip().lower() or secrets.token_hex(4)
    if not SLUG.match(slug) or slug in RESERVED:
        raise HTTPException(
            422, "an address is 3–40 characters of lowercase letters, numbers "
                 "and hyphens, and cannot be one of the site's own")
    taken = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if taken is not None:
        raise HTTPException(409, "that address is taken")

    tier = await _tier_of(user, session)
    test = StandingTest(
        slug=slug,
        chart_id=chart.id,
        user_id=user.id,
        host_name=(body.host_name.strip() or user.display_name.strip()
                   or "somebody"),
        blurb=body.blurb.strip(),
        tier_at_setup=tier,
        expires_at=expires_at(tier),
    )
    session.add(test)
    await session.commit()
    return _public(test, chart)


@router.delete("/{slug}", status_code=204)
async def take_down(
    slug: str, request: Request, session: AsyncSession = Depends(get_session),
) -> None:
    """Its host taking it down. She uses the admin route."""
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    test = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if test is None or user is None or test.user_id != user.id:
        raise HTTPException(404, "there is no test of yours at that address")
    test.hidden = True
    await session.commit()


@router.post("/{slug}/renew")
async def renew(
    slug: str, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Start the run again at whatever they pay now.

    The path back from "expired" that the plan asks for. Somebody who joined the
    higher tier after their five days ran out presses this and it becomes
    permanent, rather than having to work out that deleting and re-adding is
    what the site wanted.
    """
    from shruti.api.routes.accounts import current_user

    user = await current_user(request, session)
    test = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if test is None or user is None or test.user_id != user.id:
        raise HTTPException(404, "there is no test of yours at that address")

    tier = await _tier_of(user, session)
    test.tier_at_setup = tier
    test.expires_at = expires_at(tier)
    test.hidden = False
    await session.commit()
    chart = await session.get(SavedChart, test.chart_id)
    return _public(test, chart)


@router.post("/{slug}/hide", dependencies=[Depends(require_admin)])
async def hide(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    """Hers, for anything that should not be at a public address."""
    test = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if test is None:
        raise HTTPException(404, "no such test")
    test.hidden = not test.hidden
    await session.commit()
    return {"ok": True, "hidden": test.hidden}


# ── hers ────────────────────────────────────────────────────────────────────

class HersIn(BaseModel):
    chart: str
    slug: str = Field(default="shruti", max_length=40)
    host_name: str = Field(default="Shruti", max_length=60)
    blurb: str = Field(default="", max_length=280)


@router.post("/admin", status_code=201, dependencies=[Depends(require_admin)])
async def put_up_hers(
    body: HersIn, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Her own test, which never runs out.

    ⚠ A separate route rather than a branch inside `set_up`. She signs in as the
    OPERATOR, not as a reader, so the tier lookup there would find nothing and
    give her five days — the same five days it gives a stranger, on the one test
    that has no owner watching it stop.
    """
    chart = (
        await session.execute(
            select(SavedChart).where(SavedChart.owner_token == body.chart)
        )
    ).scalars().first()
    if chart is None:
        raise HTTPException(404, "that chart could not be found")

    slug = (body.slug or "shruti").strip().lower()
    existing = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if existing is not None:
        # Point it at the chart she has just named rather than refusing: this
        # is the route she uses to correct it.
        existing.chart_id = chart.id
        existing.host_name = body.host_name.strip() or existing.host_name
        existing.blurb = body.blurb.strip() or existing.blurb
        existing.expires_at = None
        existing.hidden = False
        await session.commit()
        return _public(existing, chart)

    test = StandingTest(
        slug=slug, chart_id=chart.id, user_id=None,
        host_name=body.host_name.strip() or "Shruti",
        blurb=body.blurb.strip(),
        tier_at_setup="",
        expires_at=None,          # hers is permanent
    )
    session.add(test)
    await session.commit()
    return _public(test, chart)


# ⚠ LAST, and it must stay last. `/{slug}` matches "admin" and every other
# single-segment path declared after it, and this codebase has been bitten by
# exactly that three times in the admin router.
@router.get("/{slug}")
async def one(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    """
    What is at this address.

    ⚠ An expired test is answered, not 404'd. The page it feeds says when it
    ran and what would put it back, because a VTuber who shared a link and now
    sees nothing concludes the site is broken and says so publicly.
    """
    test = (
        await session.execute(select(StandingTest).where(StandingTest.slug == slug))
    ).scalars().first()
    if test is None:
        raise HTTPException(404, "there is no test at that address")
    chart = await session.get(SavedChart, test.chart_id)
    return _public(test, chart)
