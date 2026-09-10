# SPDX-License-Identifier: AGPL-3.0-only
"""
Offers: what the app has worth having.

Her monetisation path for a free app. A sponsor's deal, money off something in
the shop, a discount on a class — made in the admin, made REAL by Stripe where
it is hers, and shown in the app on its own.

⚠ **Three rules, and each is a way of promising something she cannot honour.**

1. An offer with an end date stops the moment it ends. One that keeps showing
   is a code she has to honour or refuse in public.
2. A members-only offer never reaches somebody who is not a member. Showing a
   code that will be refused at the till is worse than showing nothing.
3. A sponsor's code is theirs. Stripe is never asked about it, because a coupon
   invented for a code she does not own is a discount nobody will accept.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.db import get_session
from shruti.models import Discount, Offer, Sponsor
from shruti.models.accounts import Supporter, User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/offers", tags=["offers"])

KINDS = {"shop", "classes", "membership", "sponsor"}


def running(offer: Offer, *, at: datetime | None = None) -> bool:
    """
    Whether this offer is on right now.

    ⚠ Null `ends_at` means no end, not "ended at the epoch" — the same
    inversion that would take down the permanent standing tests.
    """
    if not offer.visible:
        return False
    now = at or datetime.now(timezone.utc)

    def aware(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    starts, ends = aware(offer.starts_at), aware(offer.ends_at)
    if starts is not None and starts > now:
        return False
    if ends is not None and ends <= now:
        return False
    return True


async def _is_member(request: Request, session: AsyncSession) -> bool:
    from shruti.api.routes.accounts import current_user

    user: User | None = await current_user(request, session)
    if user is None:
        return False
    row = (
        await session.execute(select(Supporter).where(Supporter.user_id == user.id))
    ).scalars().first()
    return row is not None and row.status in {"active", "trialing"}


async def _json(offer: Offer, session: AsyncSession) -> dict:
    code = offer.code
    if offer.discount_id is not None:
        discount = await session.get(Discount, offer.discount_id)
        # ⚠ Her own code comes from the discount row, which is what Stripe
        # actually holds. Copying it onto the offer would be a second place for
        # it to be wrong, and the wrong one is the one people would type.
        if discount is not None and discount.active:
            code = discount.code
        else:
            code = ""
    sponsor = (
        await session.get(Sponsor, offer.sponsor_id)
        if offer.sponsor_id is not None else None
    )
    return {
        "id": offer.id,
        "title": offer.title,
        "blurb": offer.blurb,
        "kind": offer.kind,
        "code": code,
        "url": offer.url,
        "from": sponsor.name if sponsor else "",
        "membersOnly": offer.members_only,
        "endsAt": offer.ends_at.isoformat() if offer.ends_at else None,
    }


@router.get("")
async def what_is_on(
    request: Request, session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    What this person can have right now.

    No account needed to see the open ones. A members-only offer is left out
    entirely rather than shown locked — a list of things you cannot have is a
    worse advert for a membership than a shorter list.
    """
    member = await _is_member(request, session)
    rows = (
        await session.execute(
            select(Offer).order_by(Offer.position, Offer.created_at.desc())
        )
    ).scalars().all()
    return [
        await _json(o, session)
        for o in rows
        if running(o) and (member or not o.members_only)
    ]


class OfferIn(BaseModel):
    title: str = Field(max_length=120)
    blurb: str = Field(default="", max_length=400)
    kind: str = "shop"
    discount_id: int | None = None
    sponsor_id: int | None = None
    code: str = Field(default="", max_length=60)
    url: str = Field(default="", max_length=400)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    members_only: bool = False
    visible: bool = True
    position: int = 0


@router.get("/admin", dependencies=[Depends(require_admin)])
async def all_of_them(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Every offer, running or not, for the admin screen."""
    rows = (
        await session.execute(
            select(Offer).order_by(Offer.position, Offer.created_at.desc())
        )
    ).scalars().all()
    out = []
    for o in rows:
        body = await _json(o, session)
        body["running"] = running(o)
        body["visible"] = o.visible
        body["discountId"] = o.discount_id
        body["sponsorId"] = o.sponsor_id
        out.append(body)
    return out


@router.post("/admin", status_code=201, dependencies=[Depends(require_admin)])
async def make(
    body: OfferIn, session: AsyncSession = Depends(get_session),
) -> dict:
    if body.kind not in KINDS:
        raise HTTPException(400, f"unknown kind; try one of {sorted(KINDS)}")
    # ⚠ A sponsor's deal carries their code and never a discount of ours.
    # Attaching one would put a Stripe coupon behind somebody else's offer.
    if body.kind == "sponsor" and body.discount_id is not None:
        raise HTTPException(
            422, "a sponsor's offer uses their code, not one of ours")
    if body.discount_id is not None:
        if await session.get(Discount, body.discount_id) is None:
            raise HTTPException(404, "no such discount")

    offer = Offer(**body.model_dump())
    session.add(offer)
    await session.commit()
    return await _json(offer, session)


@router.patch("/admin/{offer_id}", dependencies=[Depends(require_admin)])
async def change(
    offer_id: int, body: OfferIn, session: AsyncSession = Depends(get_session),
) -> dict:
    offer = await session.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(404, "no such offer")
    if body.kind not in KINDS:
        raise HTTPException(400, "unknown kind")
    for key, value in body.model_dump().items():
        setattr(offer, key, value)
    await session.commit()
    return await _json(offer, session)


@router.delete("/admin/{offer_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def remove(
    offer_id: int, session: AsyncSession = Depends(get_session),
) -> None:
    offer = await session.get(Offer, offer_id)
    if offer is not None:
        await session.delete(offer)
        await session.commit()
