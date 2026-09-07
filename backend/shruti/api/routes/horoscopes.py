# SPDX-License-Identifier: AGPL-3.0-only
"""
Horoscopes: twelve at a time, written by hand.

Four periods — daily, weekly, monthly, yearly. **A period that does not exist
renders as ABSENT** — never as an error and never as a disabled control with a
tooltip.

**Weeks are ISO-8601**: Monday starts the week, week one contains the first
Thursday, and the id is `2026-W38`. That id is the database key and the URL, so
it does not move if anyone ever wants a Sunday-start display — that would be a
way of RENDERING the same seven days, never a second set of columns.

`covers` is checked against the shape its period requires. Unchecked, a typo
becomes a row nobody can find again: it saves, it does not appear in the list
it was meant for, and the work is simply gone.
"""
from __future__ import annotations

import re
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
PERIODS = ("daily", "weekly", "monthly", "yearly")

# What a period id has to look like. A weekly id is the ISO week, so `2026-W38`
# and never `2026-38`, because the W is what says which of the two conventions
# for numbering a week is meant.
COVERS_SHAPE = {
    "daily": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "weekly": re.compile(r"^\d{4}-W\d{2}$"),
    "monthly": re.compile(r"^\d{4}-\d{2}$"),
    "yearly": re.compile(r"^\d{4}$"),
}


def _opening(body_md: str, limit: int = 240) -> str:
    """The first sentence or so, as plain text, for feed summaries."""
    text = re.sub(r"[*_`#>\[\]]", "", body_md or "").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[: stop + 1] if stop > 80 else cut.rsplit(" ", 1)[0] + "…").strip()


def _valid_covers(period: str, covers: str) -> bool:
    shape = COVERS_SHAPE.get(period)
    return bool(shape and shape.match(covers or ""))


def _current(period: str) -> str:
    """
    The period we are in now.

    The ISO week year is NOT always the calendar year — the last days of
    December can belong to week 1 of the year after, and the first days of
    January to week 52 or 53 of the year before. `isocalendar()` knows this and
    arithmetic on `now.year` does not, which is why it is used.
    """
    now = datetime.now(timezone.utc)
    if period == "daily":
        return now.date().isoformat()
    if period == "weekly":
        iso = now.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    if period == "yearly":
        return str(now.year)
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
    if not _valid_covers(body.period, body.covers):
        raise HTTPException(
            400, f"a {body.period} period is written like "
                 f"{_current(body.period)!r}, not {body.covers!r}")

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


@router.get("/published")
async def published(
    sign: str | None = None, limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    A flat list of published readings, newest published first.

    /archive answers "what months exist" and groups by period to do it, which
    is right for a reader browsing but wrong for a machine: a feed needs one
    entry per reading and a real timestamp to put in <pubDate>, and a sitemap
    needs <lastmod>. Both were reading /archive and both would have been
    quietly wrong — it has no timestamp at all and returns one period per call.

    Sorted by `published_at` rather than by `covers`, because those differ:
    a reading for next month written today is published now and covers later.
    A feed sorted by `covers` would put it above readings the subscriber has
    not been shown yet.
    """
    query = select(Horoscope).where(Horoscope.published.is_(True))
    if sign:
        if sign not in SIGNS:
            raise HTTPException(404, "no such sign")
        query = query.where(Horoscope.sign == sign)

    rows = (await session.execute(
        query.order_by(Horoscope.published_at.desc().nullslast(),
                       Horoscope.covers.desc())
        .limit(max(1, min(500, limit)))
    )).scalars().all()

    return [
        {
            "sign": r.sign,
            "period": r.period,
            "covers": r.covers,
            "publishedAt": r.published_at.isoformat() if r.published_at else None,
            # Enough of the opening for a feed summary, without shipping the
            # whole reading — a feed that carries the full text is a feed
            # people read instead of visiting, and she signs these.
            "opening": _opening(r.body_md),
        }
        for r in rows
    ]


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
