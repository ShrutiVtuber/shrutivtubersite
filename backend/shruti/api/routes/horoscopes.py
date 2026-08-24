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


# ── authoring ───────────────────────────────────────────────────────────────
#
# Writing twelve of anything monthly is a chore, and a bad editor is how a
# monthly feature becomes a quarterly one. So drafts save one sign at a time
# without leaving the screen, and publishing is all twelve at once.

from fastapi import Depends  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from shruti.api.deps import require_admin  # noqa: E402


class DraftIn(BaseModel):
    sign: str
    period: str = "monthly"
    covers: str
    body_md: str = Field(default="", max_length=8000)


@router.put("/draft", dependencies=[Depends(require_admin)])
async def save_draft(
    body: DraftIn, session: AsyncSession = Depends(get_session)
) -> dict:
    if body.sign not in SIGNS:
        raise HTTPException(400, "no such sign")
    if body.period not in PERIODS:
        raise HTTPException(400, "no such period")

    row = (
        await session.execute(
            select(Horoscope).where(
                Horoscope.sign == body.sign, Horoscope.period == body.period,
                Horoscope.covers == body.covers,
            )
        )
    ).scalar_one_or_none()

    if row is None:
        row = Horoscope(
            sign=body.sign, period=body.period, covers=body.covers,
            body_md=body.body_md,
        )
        session.add(row)
    else:
        row.body_md = body.body_md
    await session.commit()
    return {"ok": True, "sign": body.sign, "written": bool(body.body_md.strip())}


@router.get("/drafts", dependencies=[Depends(require_admin)])
async def drafts(
    period: str = "monthly", covers: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    which = covers or _current(period)
    rows = (
        await session.execute(
            select(Horoscope).where(
                Horoscope.period == period, Horoscope.covers == which
            )
        )
    ).scalars().all()
    by_sign = {r.sign: r for r in rows}
    written = sum(1 for s in SIGNS if by_sign.get(s) and by_sign[s].body_md.strip())
    return {
        "period": period, "covers": which,
        "written": written, "total": len(SIGNS),
        "published": all(by_sign.get(s) and by_sign[s].published for s in SIGNS),
        "drafts": [
            {
                "sign": s,
                "bodyMd": by_sign[s].body_md if s in by_sign else "",
                "published": bool(by_sign.get(s) and by_sign[s].published),
            }
            for s in SIGNS
        ],
    }


class PublishIn(BaseModel):
    period: str = "monthly"
    covers: str


@router.post("/publish", dependencies=[Depends(require_admin)])
async def publish(
    body: PublishIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    All twelve or none.

    **An empty reading is worse than a late one**, so publishing is blocked
    until every sign has something — and the refusal names how many are
    missing rather than just saying no.
    """
    rows = (
        await session.execute(
            select(Horoscope).where(
                Horoscope.period == body.period, Horoscope.covers == body.covers
            )
        )
    ).scalars().all()
    by_sign = {r.sign: r for r in rows}

    missing = [s for s in SIGNS if not (by_sign.get(s) and by_sign[s].body_md.strip())]
    if missing:
        raise HTTPException(
            422,
            f"{len(missing)} of {len(SIGNS)} still unwritten: {', '.join(missing)}",
        )

    now = datetime.now(timezone.utc)
    for s in SIGNS:
        row = by_sign[s]
        row.published = True
        row.published_at = row.published_at or now
    await session.commit()
    return {"ok": True, "published": len(SIGNS), "covers": body.covers}


@router.get("/archive")
async def archive(
    sign: str | None = None, period: str = "monthly",
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Every published period, newest first — optionally for one sign.

    Readings do not expire. Someone who liked last October's should be able to
    find it, and someone arriving in March should be able to read back rather
    than meet an empty page because the month's twelve are not written yet.
    """
    if period not in PERIODS:
        raise HTTPException(400, f"unknown period; choose from {list(PERIODS)}")

    query = select(Horoscope).where(
        Horoscope.period == period, Horoscope.published.is_(True)
    )
    if sign:
        if sign not in SIGNS:
            raise HTTPException(404, "no such sign")
        query = query.where(Horoscope.sign == sign)

    rows = (await session.execute(query.order_by(Horoscope.covers.desc()))).scalars().all()

    # Group by the period covered, so the archive reads as a list of months
    # rather than a list of a hundred and forty-four readings.
    periods: dict[str, list[str]] = {}
    for r in rows:
        periods.setdefault(r.covers, []).append(r.sign)

    return {
        "period": period,
        "sign": sign,
        "current": _current(period),
        "periods": [
            {"covers": covers, "signs": sorted(signs), "count": len(signs)}
            for covers, signs in sorted(periods.items(), reverse=True)
        ],
    }
