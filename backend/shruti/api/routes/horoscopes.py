# SPDX-License-Identifier: AGPL-3.0-only
"""
Horoscopes: twelve a month, written by hand.

The `period` dimension exists now though only `monthly` is published, so daily,
seasonal and yearly are a switch rather than a rebuild. **A period that does
not exist renders as ABSENT** — never as an error and never as a disabled
control with a tooltip.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.db import get_session
from shruti.models.accounts import Horoscope

router = APIRouter(prefix="/api/horoscopes", tags=["horoscopes"])

SIGNS = (
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
)
PERIODS = ("monthly", "daily", "seasonal", "yearly")


def _current(period: str) -> str:
    now = datetime.now(timezone.utc)
    if period == "daily":
        return now.date().isoformat()
    if period == "yearly":
        return str(now.year)
    if period == "seasonal":
        return f"{now.year}-Q{(now.month - 1) // 3 + 1}"
    return f"{now.year}-{now.month:02d}"


@router.get("")
async def index(
    period: str = "monthly", covers: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if period not in PERIODS:
        raise HTTPException(400, f"unknown period; choose from {list(PERIODS)}")
    which = covers or _current(period)

    rows = (
        await session.execute(
            select(Horoscope).where(
                Horoscope.period == period,
                Horoscope.covers == which,
                Horoscope.published.is_(True),
            )
        )
    ).scalars().all()
    by_sign = {r.sign: r for r in rows}

    return {
        "period": period,
        "covers": which,
        # Which periods actually have something published — the switcher
        # renders only these, and the rest are absent rather than disabled.
        "availablePeriods": await _available(session),
        "readings": [
            {
                "sign": s,
                "published": s in by_sign,
                "bodyMd": by_sign[s].body_md if s in by_sign else "",
            }
            for s in SIGNS
        ],
    }


@router.get("/{sign}/{period}")
async def reading(
    sign: str, period: str, covers: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if sign not in SIGNS:
        raise HTTPException(404, "no such sign")
    if period not in PERIODS:
        raise HTTPException(404, "no such period")
    which = covers or _current(period)

    row = (
        await session.execute(
            select(Horoscope).where(
                Horoscope.sign == sign, Horoscope.period == period,
                Horoscope.covers == which, Horoscope.published.is_(True),
            )
        )
    ).scalar_one_or_none()

    return {
        "sign": sign, "period": period, "covers": which,
        "published": row is not None,
        "bodyMd": row.body_md if row else "",
        # Magickal writing signs with the motto.
        "byline": "Soror Eu. A.",
        "availablePeriods": await _available(session),
    }


async def _available(session: AsyncSession) -> list[str]:
    rows = (
        await session.execute(
            select(Horoscope.period).where(Horoscope.published.is_(True)).distinct()
        )
    ).scalars().all()
    return [p for p in PERIODS if p in set(rows)]
