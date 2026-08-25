# SPDX-License-Identifier: AGPL-3.0-only
"""
Keeping a chart, and handing one to a friend.

**Two tokens per chart.** `owner_token` is how a person gets back to their own
chart. `share_token` is what they give away. They are different strings on
purpose: with one token, sharing would mean handing over your only way in, and
unsharing would be impossible. With two, a share can be revoked without the
owner losing anything.

**Neither token carries birth data**, so the date, time and place stay out of
the URL, out of a browser history, and out of a screenshot of the address bar.
The shared view does not print them either.

What that does **not** do — and the share dialogue says so in as many words —
is hide the birth data from someone who can read a chart. The ascendant gives
the birth time to within a few minutes and the planets give the date. The
figure IS the birth data, drawn. Hiding it from the URL stops the casual case
completely and the informed case not at all, and it would be dishonest to
imply otherwise.

**This holds special-category data.** Birth data used for an astrological
reading arguably reveals philosophical belief, so the lawful basis is explicit
consent — as with `Nativity`. An account holder has that on record against
their account. Somebody without an account has nothing to hang it on, so the
consent is stored on the chart row, verbatim and versioned. And because it
cannot be renewed by asking somebody we have no address for, an ownerless
chart expires; opening it puts the clock back.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.routes.accounts import current_user
from shruti.core.consents import CONSENT_VERSION, NATIVITY
from shruti.core.db import get_session
from shruti.models.accounts import SavedChart, User

router = APIRouter(prefix="/api/charts", tags=["charts"])

# Long enough that guessing is not a strategy: 32 bytes of urlsafe randomness.
# These are bearer tokens for special-category data, so they are sized like
# passwords rather than like slugs.
TOKEN_BYTES = 32

# How long a chart nobody owns is kept, pushed forward every time it is opened.
# Not a tidy-up policy — the consent behind it cannot be renewed by asking, so
# it must not be relied on indefinitely.
ORPHAN_DAYS = 365

TRADITIONS = ("hellenistic", "vedic")
FIGURES = ("wheel", "north", "south")
HOUSE_SYSTEMS = ("whole_sign", "placidus", "equal", "porphyry",
                 "regiomontanus", "campanus")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


class Keep(BaseModel):
    """What it takes to keep a chart."""

    label: str = Field(default="", max_length=80)
    tradition: str = "hellenistic"
    house_system: str = "whole_sign"
    figure: str = "wheel"

    birth_date: str = Field(max_length=10)
    birth_time: Optional[str] = Field(default=None, max_length=5)
    time_unknown: bool = False
    place_name: str = Field(default="", max_length=160)
    lat: float = 0.0
    lon: float = 0.0

    # Required for somebody without an account, ignored for somebody with one
    # — their account already carries the consent, and asking twice for the
    # same permission teaches people to click past it.
    consent: bool = False


def _owner_view(chart: SavedChart) -> dict:
    """Everything, because it is theirs."""
    return {
        "label": chart.label,
        "tradition": chart.tradition,
        "houseSystem": chart.house_system,
        "figure": chart.figure,
        "birthDate": chart.birth_date,
        "birthTime": chart.birth_time,
        "timeUnknown": chart.time_unknown,
        "placeName": chart.place_name,
        "lat": chart.lat,
        "lon": chart.lon,
        "mine": chart.user_id is not None,
        "shared": chart.share_token is not None,
        "shareToken": chart.share_token,
        "sharedAt": chart.shared_at.isoformat() if chart.shared_at else None,
        "expiresAt": chart.expires_at.isoformat() if chart.expires_at else None,
        "createdAt": chart.created_at.isoformat() if chart.created_at else None,
    }


def _shared_view(chart: SavedChart) -> dict:
    """
    The figure, and nothing that spells out the moment.

    No birth date, no time, no place, no coordinates — not because they cannot
    be inferred from the chart by somebody who reads charts, but because
    printing them hands the same thing to everybody else too.

    What is passed on is what it takes to DRAW the chart, which necessarily
    includes the instant. That is the honest shape of the compromise: the
    drawing carries it, the page does not spell it out, and the person sharing
    was told as much before they made the link.
    """
    return {
        "label": chart.label,
        "tradition": chart.tradition,
        "houseSystem": chart.house_system,
        "figure": chart.figure,
        "timeUnknown": chart.time_unknown,
        # Needed to cast the chart at all. Not shown as text by the page.
        "birthDate": chart.birth_date,
        "birthTime": chart.birth_time,
        "lat": chart.lat,
        "lon": chart.lon,
    }


async def _by_owner(token: str, session: AsyncSession) -> SavedChart:
    chart = (
        await session.execute(select(SavedChart).where(SavedChart.owner_token == token))
    ).scalar_one_or_none()
    if chart is None:
        raise HTTPException(404, "no such chart")
    if chart.expires_at and chart.expires_at < _now():
        raise HTTPException(410, "this chart has expired")
    return chart


@router.post("", status_code=201)
async def keep(
    body: Keep,
    request: Request,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep this chart, whether or not there is an account.

    Works signed out. That is the point: a person who has just cast their chart
    should be able to keep it without being made to sign up first, and be
    *offered* an account because keeping it is nicer with one — not because the
    door is shut without one.
    """
    if body.tradition not in TRADITIONS:
        raise HTTPException(400, "unknown tradition")
    if body.figure not in FIGURES:
        raise HTTPException(400, "unknown figure")
    if body.house_system not in HOUSE_SYSTEMS:
        raise HTTPException(400, "unknown house system")
    if not body.birth_date:
        raise HTTPException(400, "a chart needs a date")

    chart = SavedChart(
        owner_token=_token(),
        user_id=user.id if user else None,
        label=body.label.strip(),
        tradition=body.tradition,
        house_system=body.house_system,
        figure=body.figure,
        birth_date=body.birth_date,
        birth_time=None if body.time_unknown else (body.birth_time or None),
        time_unknown=body.time_unknown,
        place_name=body.place_name.strip(),
        lat=body.lat,
        lon=body.lon,
        last_seen_at=_now(),
    )

    if user is None:
        # No account to hang a consent record on, so it is evidenced here,
        # verbatim, under the version they were shown.
        if not body.consent:
            raise HTTPException(
                400,
                "keeping a chart means storing birth data, which needs consent",
            )
        chart.consent_version = CONSENT_VERSION
        chart.consent_wording = NATIVITY.wording
        chart.consent_source = "chart-keep"
        chart.consent_at = _now()
        chart.expires_at = _now() + timedelta(days=ORPHAN_DAYS)

    session.add(chart)
    await session.commit()
    await session.refresh(chart)
    return {"ownerToken": chart.owner_token, "chart": _owner_view(chart)}


@router.get("/mine", dependencies=[])
async def mine(
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Every chart on this account, newest first."""
    if user is None:
        raise HTTPException(401, "not signed in")
    rows = (
        await session.execute(
            select(SavedChart)
            .where(SavedChart.user_id == user.id)
            .order_by(SavedChart.id.desc())
        )
    ).scalars().all()
    return [{**_owner_view(c), "ownerToken": c.owner_token} for c in rows]


@router.get("/o/{token}")
async def open_mine(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Open a chart by its owner token, and push the expiry back."""
    chart = await _by_owner(token, session)
    chart.last_seen_at = _now()
    if chart.user_id is None:
        chart.expires_at = _now() + timedelta(days=ORPHAN_DAYS)
    await session.commit()
    return _owner_view(chart)


@router.post("/o/{token}/share")
async def start_sharing(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Mint a link to hand out. Idempotent: asking twice returns the same link.

    Re-minting on every request would quietly break links already sent, which
    is the opposite of what pressing "share" again means.
    """
    chart = await _by_owner(token, session)
    if chart.share_token is None:
        chart.share_token = _token()
        chart.shared_at = _now()
        await session.commit()
    return {"shareToken": chart.share_token}


@router.delete("/o/{token}/share", status_code=204)
async def stop_sharing(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Take the link back.

    The link stops working. It does not un-send the link, and it does not
    un-see what has been seen — but it is the difference between a share that
    is permanent by accident and one that is a decision.
    """
    chart = await _by_owner(token, session)
    chart.share_token = None
    chart.shared_at = None
    await session.commit()
    return Response(status_code=204)


@router.post("/o/{token}/claim")
async def claim(
    token: str,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Attach a chart kept without an account to the account just made.

    This is what stops "sign up to keep your chart" from being a lie: the chart
    they already have follows them in, rather than being cast again. Claiming
    also clears the expiry, because there is now somebody to ask.
    """
    if user is None:
        raise HTTPException(401, "not signed in")
    chart = await _by_owner(token, session)
    if chart.user_id is not None and chart.user_id != user.id:
        # Somebody else's, and holding the token does not change that.
        raise HTTPException(409, "that chart already belongs to an account")
    chart.user_id = user.id
    chart.expires_at = None
    await session.commit()
    return _owner_view(chart)


@router.delete("/o/{token}", status_code=204)
async def forget(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Delete it, now, without asking anybody.

    Here because this table holds special-category data for people who may
    never have made an account, and a right to erasure that requires writing
    an email is not much of a right.
    """
    chart = await _by_owner(token, session)
    await session.delete(chart)
    await session.commit()
    return Response(status_code=204)


@router.get("/s/{token}")
async def open_shared(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """What a friend sees. See `_shared_view` for what is left out, and why."""
    chart = (
        await session.execute(select(SavedChart).where(SavedChart.share_token == token))
    ).scalar_one_or_none()
    if chart is None:
        raise HTTPException(404, "no such chart")
    if chart.expires_at and chart.expires_at < _now():
        raise HTTPException(410, "this chart has expired")
    return _shared_view(chart)
