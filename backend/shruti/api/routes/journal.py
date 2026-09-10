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
import re
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.db import engine, get_session
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


# The two moments an entry has. "published" is discoverable from the synced
# page; "written" is not, and has to be told to us.
KINDS = ("published", "written")


class CaptureIn(BaseModel):
    slug: str = Field(min_length=1, max_length=200)
    kind: str = Field(default="published", pattern="^(published|written)$")
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
    return await _capture(
        session,
        slug=body.slug,
        kind=body.kind,
        at_iso=body.at,
        lat=body.lat,
        lon=body.lon,
        place_name=body.place_name,
        recapture=body.recapture,
    )


async def _capture(
    session: AsyncSession,
    *,
    slug: str,
    kind: str,
    at_iso: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    place_name: str = "",
    recapture: bool = False,
) -> dict:
    """
    The capture itself, so the endpoint and the reconciler share one path.

    Two callers, one behaviour: a sky captured by the nightly pass and a sky
    captured by hand are the same record, made the same way.
    """
    existing = (
        await session.execute(
            select(JournalSky).where(JournalSky.slug == slug, JournalSky.kind == kind)
        )
    ).scalar_one_or_none()
    if existing is not None and not recapture:
        return _payload(existing) | {"created": False}

    if at_iso:
        try:
            at = datetime.fromisoformat(at_iso.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(400, "at must be an ISO-8601 datetime")
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
    else:
        at = datetime.now(timezone.utc)

    lat_v = lat if lat is not None else DEFAULT_PLACE[0]
    lon_v = lon if lon is not None else DEFAULT_PLACE[1]
    place = place_name or (DEFAULT_PLACE[2] if lat is None else "")

    reading: dict = {}
    failure = ""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(
                f"{_astro_base()}/today",
                params={"lat": lat_v, "lon": lon_v, "when": at.isoformat()},
            )
        if r.status_code == 200:
            reading = r.json()
        else:
            failure = f"the ephemeris returned {r.status_code}"
    except Exception as exc:                       # noqa: BLE001
        failure = f"the ephemeris could not be reached ({type(exc).__name__})"

    row = existing or JournalSky(slug=slug, kind=kind, at=at)
    row.at = at
    row.lat, row.lon, row.place_name = lat_v, lon_v, place
    row.reading = json.dumps(reading, ensure_ascii=False) if reading else ""
    row.summary = _summarise(reading) if reading else ""
    row.failure_reason = failure
    if existing is None:
        session.add(row)
    try:
        await session.commit()
    except IntegrityError:
        # Someone captured this moment while we were casting it. Theirs is as
        # good as ours — same slug, same instant, same ephemeris — so take it
        # rather than overwrite it.
        await session.rollback()
        found = (
            await session.execute(
                select(JournalSky).where(
                    JournalSky.slug == slug, JournalSky.kind == kind
                )
            )
        ).scalar_one_or_none()
        if found is None:
            raise
        return _payload(found) | {"created": False}
    await session.refresh(row)

    return _payload(row) | {"created": existing is None}


@router.get("/sky/{slug}")
async def read_sky(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Both moments for one entry.

    Either may be absent and that is not an error — most entries will have a
    publication sky and no writing sky, because only she can say when she
    started. A 404 here would make "she has not told us" look like a fault.
    """
    rows = (
        await session.execute(select(JournalSky).where(JournalSky.slug == slug))
    ).scalars().all()
    if not rows:
        raise HTTPException(404, "no sky recorded for that entry")
    return _by_kind(rows)


@router.get("/recent")
async def recent(limit: int = 10) -> list[dict]:
    """
    Her latest writing, as JSON, for the app.

    ⚠ The site reads these pages directly and the RSS feed is a PAGE, which
    means the holding page gates it — so the app cannot use either. This is the
    same synced entries, over the API the app can actually reach.

    Title and opening come out of the HTML BeeRanked wrote; nothing is stored
    and nothing is recomputed. An entry with no timestamp is left out rather
    than guessed at, because the order is the whole point of a "recent" list.
    """
    import re

    out: list[dict] = []
    for slug, path in _entry_slugs():
        try:
            with open(path, encoding="utf-8") as handle:
                html = handle.read()
        except OSError:
            continue
        when = _published_at(html)
        if not when:
            continue
        title = ""
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        if match:
            title = re.sub(r"\s+", " ", match.group(1)).strip()
            # ⚠ BeeRanked appends the site name, and not always with the same
            # separator. Splitting on one of them leaves ", Shruti" on the end
            # of every title in the app.
            title = re.split(r"\s*[—|·]\s*|,\s*Shruti\s*$", title)[0].strip()

        # ⚠ The <meta name="description"> here is the SITE's, identical on every
        # entry — using it gives a list where every row says the same sentence.
        # The entry's own opening is its first paragraph.
        opening = ""
        body = re.search(r"<article[^>]*>(.*?)</article>", html, re.S | re.I)
        for para in re.finditer(r"<p[^>]*>(.*?)</p>",
                                body.group(1) if body else html, re.S | re.I):
            text = re.sub(r"<[^>]+>", " ", para.group(1))
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 40:
                opening = text[:240]
                break
        out.append({
            "slug": slug,
            "title": title or slug.replace("-", " ").title(),
            "opening": opening,
            "publishedAt": when,
            "url": f"/journal/{slug}",
        })

    out.sort(key=lambda e: e["publishedAt"], reverse=True)
    return out[:max(1, min(limit, 50))]


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
    out: dict[str, dict] = {}
    for r in rows:
        out.setdefault(r.slug, {})[r.kind] = _payload(r)
    return {"skies": {slug: _fill(kinds) for slug, kinds in out.items()}}


def _fill(kinds: dict) -> dict:
    return {k: kinds.get(k) for k in KINDS}


def _by_kind(rows) -> dict:
    return _fill({r.kind: _payload(r) for r in rows})


JOURNAL_DIR = os.environ.get("SHRUTI_JOURNAL_DIR", "/srv/journal")

# A JSON-LD block. Matched loosely and then parsed — a false match is not a
# risk here because anything that is not JSON simply fails to load, which is
# the check. (Pattern-matching HTML to find *content* is what once rendered a
# CSS comment as an article; this matches a container and lets json decide.)
_LD = re.compile(
    r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", re.S | re.I
)


def _published_at(html: str) -> str:
    """
    The publication timestamp BeeRanked stamps into the page, or "".

    Searched recursively, because the block is an `@graph` — the entry's own
    node sits inside it alongside the site and the breadcrumbs, and looking
    only at the top level finds nothing.
    """

    def find(node) -> str:
        if isinstance(node, dict):
            if node.get("datePublished"):
                return str(node["datePublished"])
            for value in node.values():
                found = find(value)
                if found:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = find(value)
                if found:
                    return found
        return ""

    for block in _LD.findall(html):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        found = find(data)
        if found:
            return found
    return ""


def _entry_slugs() -> list[tuple[str, str]]:
    """
    (slug, file) for every synced entry.

    Only entries — a slug two or more segments deep. The hub, the section
    indexes and the sitemap are not things that were written at a moment.
    """
    out: list[tuple[str, str]] = []
    for dirpath, _dirs, files in os.walk(JOURNAL_DIR):
        if "index.html" not in files:
            continue
        rel = os.path.relpath(dirpath, JOURNAL_DIR)
        parts = [p for p in rel.split(os.sep) if p and p != "."]
        if len(parts) < 2:
            continue
        out.append((parts[-1], os.path.join(dirpath, "index.html")))
    return out


async def reconcile_published(session: AsyncSession) -> dict:
    """
    Capture the publication sky for every entry that lacks one.

    Safe to run at any time, and safe to run repeatedly: the moment captured is
    the entry's own `datePublished`, never the clock. Running this next year
    produces the same record as running it today, which is the whole reason the
    capture is allowed to be automatic at all.

    The writing sky is never touched here. Nothing can discover it.
    """
    entries = _entry_slugs()
    if not entries:
        return {"checked": 0, "captured": 0, "skipped": 0, "failed": 0}

    # The API runs with two uvicorn workers and each gets its own lifespan, so
    # without this both wake up and cast the same charts — racing to the same
    # unique key and burning two ephemeris calls per entry to store one row.
    #
    # The lock is held on a connection of its own for the whole pass. A
    # session-level lock taken on the working session would not survive: the
    # captures commit as they go, the session hands its connection back, and
    # the lock would go with it.
    async with engine.connect() as conn:
        got = (await conn.execute(select(func.pg_try_advisory_lock(SKY_LOCK)))).scalar()
        if not got:
            return {"checked": len(entries), "captured": 0,
                    "skipped": len(entries), "failed": 0, "lock": "held elsewhere"}
        try:
            return await _reconcile(session, entries)
        finally:
            await conn.execute(select(func.pg_advisory_unlock(SKY_LOCK)))


# An arbitrary but fixed key; advisory locks share one namespace per database.
SKY_LOCK = 8_140_233_517


async def _reconcile(session: AsyncSession, entries: list[tuple[str, str]]) -> dict:
    """The pass itself, once this worker holds the lock."""
    have = set(
        (
            await session.execute(
                select(JournalSky.slug).where(JournalSky.kind == "published")
            )
        ).scalars().all()
    )

    captured = failed = 0
    for slug, path in entries:
        if slug in have:
            continue
        try:
            with open(path, encoding="utf8") as fh:
                iso = _published_at(fh.read())
        except OSError:
            iso = ""
        if not iso:
            # No timestamp means no honest moment to record. Better a missing
            # record than one stamped with the moment this happened to run.
            failed += 1
            continue
        await _capture(session, slug=slug, kind="published", at_iso=iso)
        captured += 1

    return {
        "checked": len(entries),
        "captured": captured,
        "skipped": len(entries) - captured - failed,
        "failed": failed,
    }


@router.get("/entries", dependencies=[Depends(require_admin)])
async def list_entries(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Every synced entry and which of its two skies exist.

    For the admin surface, which is only there for the one moment nothing can
    discover — she can capture a writing sky, and the other column tells her
    whether the automatic pass has done its half.
    """
    entries = _entry_slugs()
    rows = (await session.execute(select(JournalSky))).scalars().all()
    have: dict[str, dict] = {}
    for r in rows:
        have.setdefault(r.slug, {})[r.kind] = _payload(r)

    out = []
    for slug, path in sorted(entries):
        try:
            with open(path, encoding="utf8") as fh:
                published_at = _published_at(fh.read())
        except OSError:
            published_at = ""
        kinds = have.get(slug, {})
        out.append({
            "slug": slug,
            "publishedAt": published_at,
            "published": kinds.get("published"),
            "written": kinds.get("written"),
        })
    return {"entries": out}


@router.post("/sky/reconcile", dependencies=[Depends(require_admin)])
async def reconcile(session: AsyncSession = Depends(get_session)) -> dict:
    return await reconcile_published(session)


def _payload(row: JournalSky) -> dict:
    return {
        "slug": row.slug,
        "kind": row.kind,
        "at": row.at.isoformat() if row.at else None,
        "place": {"lat": row.lat, "lon": row.lon, "name": row.place_name},
        "summary": row.summary,
        "reading": json.loads(row.reading) if row.reading else None,
        # Never a blank: a missing sky says why it is missing.
        "failureReason": row.failure_reason,
    }
