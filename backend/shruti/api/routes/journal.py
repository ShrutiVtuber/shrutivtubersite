# SPDX-License-Identifier: AGPL-3.0-only
"""
The sky attached to a journal entry.

The entries themselves live in BeeRanked. This holds the one thing BeeRanked
cannot know: what the sky was doing at the moment each was published.

Three rules, taken from how theourgia stamps its records:

  - **Capture describes a moment, and that moment does not move.** An entry
    written under a Mars hour was written under a Mars hour. Re-casting it next
    year would quietly replace that with a different sky, and the record would
    stop being a record.
  - **It is the machine's half of the entry and is not editable.** There is a
    route to capture and a route to read; there is deliberately none to amend.
  - **Absence states its reason.** A capture that failed stores why, so the
    reader sees "the ephemeris could not be reached" instead of a blank.

Stored rather than recomputed, so rendering an index of twenty entries does not
cast twenty charts.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.db import get_session
from shruti.models.accounts import JournalSky

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/journal", tags=["journal"])

# Athens, where the writing happens, unless an entry says otherwise.
DEFAULT_PLACE = (37.9838, 23.7275, "Athens")


def _astro_base() -> str:
    return os.environ.get("SHRUTI_ASTRO_INTERNAL", "http://shruti-astro:8000").rstrip("/")


def _summarise(reading: dict) -> str:
    """
    One line for cards and indexes, composed once at capture.

    Deliberately the things that change fastest and mean most to a
    practitioner: the Moon, the planetary hour, and the day in the two
    traditional reckonings.
    """
    bits: list[str] = []
    moon = (reading.get("moon") or {}).get("tropical") or {}
    if moon.get("sign"):
        bits.append(f"Moon in {moon['sign']}")
    hour = (reading.get("planetaryHours") or {}).get("current") or {}
    if hour.get("ruler"):
        bits.append(f"hour of {hour['ruler']}")
    attic = (reading.get("reckonings") or {}).get("attic") or {}
    if attic.get("month"):
        bits.append(f"{attic['month']} {attic.get('day', '')}".strip())
    hindu = (reading.get("reckonings") or {}).get("hindu") or {}
    if hindu.get("tithi"):
        bits.append(hindu["tithi"])
    return " · ".join(bits)


class CaptureIn(BaseModel):
    slug: str = Field(min_length=1, max_length=200)
    # The moment being described. Defaults to now, which is right when an entry
    # is captured as it publishes.
    at: str | None = None
    lat: float | None = None
    lon: float | None = None
    place_name: str = ""
    # Re-capture an existing slug. Off by default, because the ordinary case of
    # calling twice is a duplicate webhook, not a correction.
    recapture: bool = False


@router.post("/sky", status_code=201, dependencies=[Depends(require_admin)])
async def capture_sky(
    body: CaptureIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """Compute and store the sky for one entry. Idempotent unless recapture."""
    existing = (
        await session.execute(select(JournalSky).where(JournalSky.slug == body.slug))
    ).scalar_one_or_none()
    if existing is not None and not body.recapture:
        return _payload(existing) | {"created": False}

    if body.at:
        try:
            at = datetime.fromisoformat(body.at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(400, "at must be an ISO-8601 datetime")
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
    else:
        at = datetime.now(timezone.utc)

    lat = body.lat if body.lat is not None else DEFAULT_PLACE[0]
    lon = body.lon if body.lon is not None else DEFAULT_PLACE[1]
    place = body.place_name or (DEFAULT_PLACE[2] if body.lat is None else "")

    reading: dict = {}
    failure = ""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(
                f"{_astro_base()}/today",
                params={"lat": lat, "lon": lon, "when": at.isoformat()},
            )
        if r.status_code == 200:
            reading = r.json()
        else:
            failure = f"the ephemeris returned {r.status_code}"
    except Exception as exc:                       # noqa: BLE001
        failure = f"the ephemeris could not be reached ({type(exc).__name__})"

    row = existing or JournalSky(slug=body.slug, at=at)
    row.at = at
    row.lat, row.lon, row.place_name = lat, lon, place
    row.reading = json.dumps(reading, ensure_ascii=False) if reading else ""
    row.summary = _summarise(reading) if reading else ""
    row.failure_reason = failure
    if existing is None:
        session.add(row)
    await session.commit()
    await session.refresh(row)

    return _payload(row) | {"created": existing is None}


@router.get("/sky/{slug}")
async def read_sky(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    row = (
        await session.execute(select(JournalSky).where(JournalSky.slug == slug))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no sky recorded for that entry")
    return _payload(row)


@router.get("/skies")
async def read_skies(
    slugs: str = "", session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Several at once, for an index.

    The whole reason these are stored is that rendering twenty cards should not
    cast twenty charts; fetching them one at a time would give that back.
    """
    wanted = [s for s in (slugs.split(",") if slugs else []) if s][:100]
    if not wanted:
        return {"skies": {}}
    rows = (
        await session.execute(select(JournalSky).where(JournalSky.slug.in_(wanted)))
    ).scalars().all()
    return {"skies": {r.slug: _payload(r) for r in rows}}


def _payload(row: JournalSky) -> dict:
    return {
        "slug": row.slug,
        "at": row.at.isoformat() if row.at else None,
        "place": {"lat": row.lat, "lon": row.lon, "name": row.place_name},
        "summary": row.summary,
        "reading": json.loads(row.reading) if row.reading else None,
        # Never a blank: a missing sky says why it is missing.
        "failureReason": row.failure_reason,
    }
