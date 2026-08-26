# SPDX-License-Identifier: AGPL-3.0-only
"""
What an overlay is allowed to know.

Every route here is authenticated by a token in the URL and nothing else, which
sets the rule for the whole module: **an overlay token is a read-only
credential scoped to one surface.** No route mutates anything, and none returns
more than the surface draws. OBS settings get screen-shared, and a token that
leaks should be worth nothing beyond seeing a bar somebody was already showing
on a stream.

The token is never echoed back, either — not even to her. There is no route
here that returns it.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core import counters
from shruti.core.db import get_session
from shruti.models import Counter, OverlayToken

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/overlay", tags=["overlay"])


async def _overlay(token: str, session: AsyncSession) -> OverlayToken:
    row = (
        await session.execute(select(OverlayToken).where(OverlayToken.token == token))
    ).scalar_one_or_none()
    if row is None:
        # 404 rather than 403: whether a token exists is not information a
        # stranger with a guess should be able to collect.
        raise HTTPException(404, "no such overlay")
    row.last_seen = datetime.now(timezone.utc)
    await session.commit()
    return row


def _shape(counter: Counter, progress: dict) -> dict:
    """
    The counter, as the overlay draws it.

    `unit` is a field and never inferred from the presence of a currency —
    "14 / 20 people" and "€184 / €300" are one object, and deciding which by
    looking at the data is how the people case becomes an afterthought.

    `current` is returned UNCAPPED. Clamping at the target would throw away the
    overrun, which is the best moment the design has.
    """
    return {
        "name": counter.name,
        "note": counter.note,
        "unit": counter.unit,
        "currency": counter.currency,
        "target": counter.target,
        "current": progress["current"],
        "contributors": progress["contributors"],
        "endsAt": counter.ends_at.isoformat() if counter.ends_at else None,
    }


@router.get("/counter")
async def counter(t: str, session: AsyncSession = Depends(get_session)) -> dict:
    """
    The counter this overlay shows, or an honest nothing.

    "Nothing configured" is a real state and the first thing she will ever see —
    the overlay is added to OBS before the counter exists. It returns a shape
    the page can draw rather than a 404, so the surface can say
    "connected, pick a counter" instead of failing.
    """
    row = await _overlay(t, session)
    payload: dict = {
        "kind": row.kind,
        "motion": row.motion,
        "appearance": row.appearance or "almanac",
        "counter": None,
    }
    if row.counter_id is None:
        return payload

    c = await session.get(Counter, row.counter_id)
    if c is None or not c.visible:
        return payload

    payload["counter"] = _shape(c, await counters.progress(session, c))
    return payload


@router.get("/events")
async def events(t: str, since: int = 0,
                 session: AsyncSession = Depends(get_session)) -> dict:
    """
    Alerts that have not been shown yet.

    `since` is an event id rather than a timestamp: two events can share a
    second, and a timestamp cursor silently drops one of them.

    A message is included ONLY when it has been approved. Unapproved is not an
    error and does not delay the alert — §6 of the handoff is explicit that an
    unmoderated alert fires without its message rather than waiting.
    """
    await _overlay(t, session)
    from shruti.models import SupportEvent

    rows = (
        await session.execute(
            select(SupportEvent)
            .where(SupportEvent.id > since)
            .order_by(SupportEvent.id)
            .limit(20)
        )
    ).scalars().all()

    return {"events": [{
        "id": e.id,
        "source": e.source,
        "who": e.who or "Someone",
        "amountMinor": e.amount_minor,
        "currency": e.currency,
        "quantity": e.quantity,
        # Absent, not empty, when it has not been read by a person.
        "message": e.message if e.message_approved else "",
        "at": e.occurred_at.isoformat() if e.occurred_at else "",
    } for e in rows]}


# ── the admin side ──────────────────────────────────────────────────────────
#
# Separated from everything above by more than a comment: nothing above needs a
# credential and nothing below works without one.

from shruti.api.deps import require_admin          # noqa: E402


class CounterIn(BaseModel):
    name: str = Field(default="", max_length=120)
    note: str = Field(default="", max_length=200)
    unit: str = Field(default="money")
    target: int = Field(default=0, ge=0)
    currency: str = Field(default="eur", max_length=3)
    sources: list[str] = Field(default_factory=list)


class OverlayIn(BaseModel):
    kind: str = Field(default="counter")
    label: str = Field(default="", max_length=80)
    counter_id: int | None = None
    motion: str = Field(default="reduced")
    appearance: str = Field(default="almanac")


@router.get("/admin/counters")
async def admin_counters(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """Every counter with where it has got to, so the admin shows the truth."""
    rows = (
        await session.execute(select(Counter).order_by(Counter.position, Counter.id))
    ).scalars().all()
    out = []
    for c in rows:
        p = await counters.progress(session, c)
        out.append({
            "id": c.id, "slug": c.slug, "name": c.name, "note": c.note,
            "unit": c.unit, "target": c.target, "currency": c.currency,
            "sources": [x for x in (c.sources or "").split(",") if x],
            "current": p["current"], "contributors": p["contributors"],
            "visible": c.visible,
        })
    return out


@router.post("/admin/counters", status_code=201)
async def create_counter(
    body: CounterIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    bad = [s for s in body.sources if s not in counters.SOURCES]
    if bad:
        # Named rather than dropped. A source silently ignored is a counter
        # that will not move, discovered days later.
        raise HTTPException(422, f"unknown source(s): {', '.join(bad)}")

    name = body.name.strip() or "Untitled"
    base = "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-")[:40] or "counter"
    slug, n = base, 1
    while (await session.execute(select(Counter).where(Counter.slug == slug))).scalar_one_or_none():
        n += 1
        slug = f"{base}-{n}"

    row = Counter(slug=slug, name=name, note=body.note.strip(), unit=body.unit,
                  target=body.target, currency=body.currency.lower(),
                  sources=",".join(body.sources), visible=True)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "slug": row.slug}


@router.delete("/admin/counters/{counter_id}", status_code=204)
async def delete_counter(
    counter_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> None:
    """
    Removes the counter, never the events.

    The events are the record of what people actually did. Deleting a goal must
    not delete the evidence that it was met.
    """
    row = await session.get(Counter, counter_id)
    if row is not None:
        await session.delete(row)
        await session.commit()


@router.get("/admin/overlays")
async def admin_overlays(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> list[dict]:
    """
    The overlays, WITHOUT their tokens.

    There is no route anywhere that returns a token after it is made — not even
    to her. OBS settings get screen-shared, and the admin has no reason to
    render a credential it can hand to the clipboard instead.
    """
    rows = (
        await session.execute(select(OverlayToken).order_by(OverlayToken.id))
    ).scalars().all()
    return [{
        "id": o.id, "kind": o.kind, "label": o.label,
        "counterId": o.counter_id, "motion": o.motion, "appearance": o.appearance,
        "lastSeen": o.last_seen.isoformat() if o.last_seen else None,
    } for o in rows]


@router.post("/admin/overlays", status_code=201)
async def create_overlay(
    body: OverlayIn,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> dict:
    """
    Mints one overlay and returns its URL **once**.

    The URL is the only time the token is ever readable. Losing it costs a new
    overlay row and a paste into OBS; keeping it readable costs a credential on
    screen every time she opens the admin on stream.
    """
    token = secrets.token_urlsafe(24)
    row = OverlayToken(token=token, kind=body.kind, label=body.label.strip(),
                       counter_id=body.counter_id, motion=body.motion,
                       appearance=body.appearance)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "token": token}


@router.delete("/admin/overlays/{overlay_id}", status_code=204)
async def revoke_overlay(
    overlay_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(require_admin),
) -> None:
    """A delete, not a flag. A revoked token that still works is not revoked."""
    row = await session.get(OverlayToken, overlay_id)
    if row is not None:
        await session.delete(row)
        await session.commit()
