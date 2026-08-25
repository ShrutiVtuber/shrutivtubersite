# SPDX-License-Identifier: AGPL-3.0-only
"""
How much each thing gets used.

**Nothing here identifies anybody, by construction rather than by promise.**

A visitor is a hash of their address, their browser string, today's date and a
server secret. Same person, same number, all day; a different number tomorrow;
and no way back to an address from the number. No cookie is set, no
localStorage is written, nothing is stored that outlives the day it was made.

That is what makes this answerable without a consent banner. There is no
personal data held, so there is nothing to ask permission for — which is a
better outcome than asking and being refused, because a statistic gathered from
the third of people who say yes is worse than no statistic at all.

The address is used and never written down. It reaches the hash and stops.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models import Visit

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/insight", tags=["insight"])

# Anything that says it is a robot, plus the common libraries. Not a security
# measure — a determined crawler can say anything — but it keeps the numbers
# from being mostly uptime checks.
ROBOTS = ("bot", "crawler", "spider", "curl", "wget", "python-requests",
          "httpx", "headless", "monitor", "probe", "lighthouse", "pingdom")


def _visitor(request: Request, when: date) -> str:
    """
    Today's number for this person.

    The address goes in and never comes out — not into a column, not into a
    log. The date is in the hash, so the number changes at midnight and cannot
    be joined across days even by whoever holds this database.
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    address = forwarded.split(",")[0].strip() or (
        request.client.host if request.client else ""
    )
    agent = request.headers.get("user-agent", "")
    secret = get_settings().secret_key
    return hashlib.sha256(
        f"{secret}|{when.isoformat()}|{address}|{agent}".encode()
    ).hexdigest()[:32]


def _referrer_host(raw: str) -> str:
    """
    Just the host.

    A full referring URL can carry a search query, which is somebody's own
    words about what they were looking for. The host answers "where did they
    come from" and nothing more.
    """
    if not raw:
        return ""
    from urllib.parse import urlparse

    try:
        host = urlparse(raw).hostname or ""
    except ValueError:
        return ""
    return "" if host.endswith("shrutivtuber.com") else host[:120]


class Beacon(BaseModel):
    path: str = Field(max_length=300)
    event: str = Field(default="", max_length=60)
    # Small, and never anything a visitor typed — which tool, not what they
    # asked it.
    props: dict[str, str] = Field(default_factory=dict)
    referrer: str = Field(default="", max_length=400)


@router.post("/beacon", status_code=204)
async def beacon(
    body: Beacon, request: Request, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Record one page or one thing done.

    Answers 204 whatever happens. A page must not appear broken because a
    counter had an opinion, and a visitor should never be told their visit was
    rejected — there is nothing they could do about it and nothing at stake.
    """
    agent = (request.headers.get("user-agent") or "").lower()
    if not agent or any(robot in agent for robot in ROBOTS):
        return Response(status_code=204)

    try:
        today = datetime.now(timezone.utc).date()
        props = {k[:40]: str(v)[:80] for k, v in list(body.props.items())[:8]}
        session.add(Visit(
            day=today.isoformat(),
            path=body.path[:300] or "/",
            event=body.event[:60],
            props=json.dumps(props, ensure_ascii=False) if props else "",
            visitor=_visitor(request, today),
            referrer=_referrer_host(body.referrer),
        ))
        await session.commit()
    except Exception:                                  # noqa: BLE001
        log.exception("a visit could not be recorded")

    return Response(status_code=204)


# ── reading it back ─────────────────────────────────────────────────────────

def _window(days: int) -> list[str]:
    today = datetime.now(timezone.utc).date()
    return [(today - timedelta(days=n)).isoformat() for n in range(days - 1, -1, -1)]


@router.get("/summary", dependencies=[Depends(require_admin)])
async def summary(
    days: int = 30, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    What happened, over a window.

    Counted rather than sampled, because at this size there is no reason to
    estimate anything.
    """
    days = max(1, min(days, 365))
    window = _window(days)
    since = window[0]

    rows = (
        await session.execute(select(Visit).where(Visit.day >= since))
    ).scalars().all()

    pages = [v for v in rows if not v.event]
    events = [v for v in rows if v.event]

    def top(items, key, limit=12):
        counts: dict[str, int] = {}
        for item in items:
            counts[key(item)] = counts.get(key(item), 0) + 1
        return [
            {"name": name, "count": n}
            for name, n in sorted(counts.items(), key=lambda kv: -kv[1])[:limit]
        ]

    by_day = []
    for day in window:
        of_day = [v for v in pages if v.day == day]
        by_day.append({
            "day": day,
            "views": len(of_day),
            "visitors": len({v.visitor for v in of_day}),
        })

    # Which tool, from the props, falling back to the event name.
    def tool_of(v: Visit) -> str:
        try:
            return json.loads(v.props or "{}").get("tool") or v.event
        except ValueError:
            return v.event

    tools = [v for v in events if v.event.startswith("tool:") or "tool" in (v.props or "")]

    return {
        "days": days,
        "views": len(pages),
        "visitors": len({v.visitor for v in pages}),
        "byDay": by_day,
        "topPages": top(pages, lambda v: v.path),
        "referrers": top([v for v in pages if v.referrer], lambda v: v.referrer, 10),
        "events": top(events, lambda v: v.event, 15),
        "tools": [
            {"name": t["name"], "count": t["count"],
             "people": len({v.visitor for v in tools if tool_of(v) == t["name"]})}
            for t in top(tools, tool_of, 15)
        ],
    }


@router.get("/journeys", dependencies=[Depends(require_admin)])
async def journeys(
    days: int = 7, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Which page tends to follow which.

    Built from a day's worth of one visitor's pages in order — which is as far
    as it can go, because the number changes at midnight. That is enough to
    answer "do people find the tools from the home page" and not enough to
    follow anybody.
    """
    days = max(1, min(days, 60))
    since = _window(days)[0]

    rows = (
        await session.execute(
            select(Visit)
            .where(Visit.day >= since, Visit.event == "")
            .order_by(Visit.visitor, Visit.id)
        )
    ).scalars().all()

    steps: dict[str, int] = {}
    landed: dict[str, int] = {}
    previous_visitor, previous_path = None, None

    for visit in rows:
        if visit.visitor != previous_visitor:
            landed[visit.path] = landed.get(visit.path, 0) + 1
            previous_visitor, previous_path = visit.visitor, visit.path
            continue
        if previous_path and previous_path != visit.path:
            key = f"{previous_path} → {visit.path}"
            steps[key] = steps.get(key, 0) + 1
        previous_path = visit.path

    top = lambda d, n: [{"name": k, "count": v}
                        for k, v in sorted(d.items(), key=lambda kv: -kv[1])[:n]]
    return {"days": days, "landings": top(landed, 10), "steps": top(steps, 20)}


@router.delete("/all", status_code=204, dependencies=[Depends(require_admin)])
async def forget_everything(session: AsyncSession = Depends(get_session)) -> Response:
    """
    Throw the lot away.

    Here because a thing that collects should always have a way to stop
    holding, and because she should never have to ask anybody to run a query
    for her.
    """
    await session.execute(Visit.__table__.delete())
    await session.commit()
    return Response(status_code=204)
