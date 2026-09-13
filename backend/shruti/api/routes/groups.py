# SPDX-License-Identifier: AGPL-3.0-only
"""
Groups: a shared goal, contributed to by a crew, with no path.

A group has a goal and nothing else — no steps, no schedule. Its sigil is
the goal's tiers, filled by contributions. Nobody is ranked: the list is
by size with "and N others", and nobody is reminded.

Reading a group needs no account; joining and contributing do. The join
code is six letters, spoken on stream.
"""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import get_session
from shruti.api.routes.practice import _name, _reader, _refuse_if_suspended
from shruti.models import OverlayToken, User
from shruti.models.guides import Group, GroupContribution, GroupMember

router = APIRouter(prefix="/api/groups", tags=["groups"])
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"          # no I or O: they read as digits on stream


def _code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(6))


async def _group(session: AsyncSession, code: str) -> Group:
    g = (await session.execute(select(Group).where(Group.code == code.upper()))).scalar_one_or_none()
    if g is None:
        raise HTTPException(404, "no such group")
    return g


async def _view(session: AsyncSession, g: Group, viewer: User | None) -> dict:
    total = (await session.execute(
        select(func.coalesce(func.sum(GroupContribution.amount), 0)).where(GroupContribution.group_id == g.id))).scalar_one()
    members = (await session.execute(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id))).scalar_one()
    rows = (await session.execute(
        select(GroupContribution.user_id, func.sum(GroupContribution.amount).label("n"))
        .where(GroupContribution.group_id == g.id).group_by(GroupContribution.user_id).order_by(func.sum(GroupContribution.amount).desc())
    )).all()
    names = {}
    for uid, _ in rows[:3]:
        u = await session.get(User, uid)
        names[uid] = _name(u)
    shown = [{"who": names[uid], "amount": int(n)} for uid, n in rows[:3]]
    others = rows[3:]
    tier_size = g.target / g.tiers if g.tiers and g.target else 0
    tier = int(min(g.tiers, total // tier_size)) if tier_size else 0
    parts = []
    for i in range(g.tiers):
        lo = i * tier_size
        pct = 0.0 if not tier_size else max(0.0, min(1.0, (total - lo) / tier_size))
        parts.append({"pct": pct, "state": "done" if pct >= 1 else ("now" if pct > 0 else "todo")})
    mine = viewer is not None and (await session.execute(
        select(GroupMember).where(GroupMember.group_id == g.id, GroupMember.user_id == viewer.id))).scalar_one_or_none() is not None
    return {
        "code": g.code, "name": g.name, "goal": g.goal, "target": g.target, "tiers": g.tiers,
        "total": int(total), "tier": tier, "members": int(members), "closed": g.closed,
        "contributions": shown,
        "others": {"count": len(others), "amount": int(sum(int(n) for _, n in others))},
        "sigil": parts,
        "member": mine, "owner": viewer is not None and viewer.id == g.created_by,
        "since": g.created_at.isoformat() if g.created_at else None,
    }


def goal_element(view: dict) -> dict:
    """What the goal overlay draws: the title, the count, the tiers, the crew — and no ranks."""
    return {
        "name": view["name"], "goal": view["goal"], "total": view["total"], "target": view["target"],
        "tier": view["tier"], "tiers": view["tiers"], "parts": view["sigil"],
        "count": f"{view['total']:,} of {view['target']:,}" if view["target"] else f"{view['total']:,}",
        "contributors": [c["who"] for c in view["contributions"]],
        "others": view["others"]["count"],
        "members": view["members"],
    }


async def goal_by_code(session: AsyncSession, code: str) -> dict | None:
    g = (await session.execute(select(Group).where(Group.code == code.upper()))).scalar_one_or_none()
    return None if g is None else goal_element(await _view(session, g, None))


class GroupIn(BaseModel):
    name: str
    goal: str = ""
    target: int = 0
    tiers: int = 5


@router.post("", status_code=201)
async def create(body: GroupIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    name = body.name.strip()[:80]
    if not name:
        raise HTTPException(422, "a group needs a name")
    for _ in range(8):
        g = Group(code=_code(), name=name, goal=body.goal.strip()[:120], target=max(0, body.target),
                  tiers=max(1, min(12, body.tiers)), created_by=user.id)
        session.add(g)
        try:
            await session.flush()
            break
        except IntegrityError:
            await session.rollback()
    else:
        raise HTTPException(500, "could not find a free code")
    session.add(GroupMember(group_id=g.id, user_id=user.id))
    await session.commit()
    return await _view(session, g, user)


@router.get("/mine")
async def mine(request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    user = await _reader(request, session)
    rows = (await session.execute(
        select(Group).join(GroupMember, GroupMember.group_id == Group.id).where(GroupMember.user_id == user.id).order_by(Group.updated_at.desc())
    )).scalars().all()
    return [await _view(session, g, user) for g in rows]


@router.get("/{code}")
async def one(code: str, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    from shruti.api.routes.accounts import current_user
    viewer = await current_user(request, session)
    return await _view(session, await _group(session, code), viewer)


@router.post("/{code}/join")
async def join(code: str, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    g = await _group(session, code)
    if g.closed:
        raise HTTPException(409, "this group is closed")
    session.add(GroupMember(group_id=g.id, user_id=user.id))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
    return await _view(session, g, user)


@router.post("/{code}/leave")
async def leave(code: str, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    g = await _group(session, code)
    m = (await session.execute(select(GroupMember).where(GroupMember.group_id == g.id, GroupMember.user_id == user.id))).scalar_one_or_none()
    if m is not None:
        await session.delete(m)
        await session.commit()
    return await _view(session, g, user)


class ContributeIn(BaseModel):
    amount: int


@router.post("/{code}/contribute", status_code=201)
async def contribute(code: str, body: ContributeIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """One number. Nobody is ranked, and nobody is reminded."""
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    g = await _group(session, code)
    if g.closed:
        raise HTTPException(409, "this group is closed")
    member = (await session.execute(select(GroupMember).where(GroupMember.group_id == g.id, GroupMember.user_id == user.id))).scalar_one_or_none()
    if member is None:
        raise HTTPException(403, "join the group first")
    amount = max(1, min(1_000_000, int(body.amount)))
    session.add(GroupContribution(group_id=g.id, user_id=user.id, amount=amount))
    await session.commit()
    return await _view(session, g, user)


class CloseIn(BaseModel):
    closed: bool


@router.post("/{code}/close")
async def close(code: str, body: CloseIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    g = await _group(session, code)
    if g.created_by != user.id:
        raise HTTPException(404, "no such group")
    g.closed = body.closed
    await session.commit()
    return await _view(session, g, user)


# ── the group's own overlay: the goal element, minted by a member ────────────

class GoalTokenIn(BaseModel):
    label: str = ""
    theme: str = "almanac"
    motion: str = "reduced"


@router.get("/{code}/overlays")
async def goal_tokens(code: str, request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """This person's goal overlays for the group, WITHOUT their tokens."""
    user = await _reader(request, session)
    g = await _group(session, code)
    rows = (await session.execute(
        select(OverlayToken).where(OverlayToken.group_id == g.id, OverlayToken.user_id == user.id).order_by(OverlayToken.id))).scalars().all()
    return [{"id": o.id, "kind": o.kind, "label": o.label, "theme": o.theme, "motion": o.motion,
             "lastSeen": o.last_seen.isoformat() if o.last_seen else None} for o in rows]


@router.post("/{code}/overlays", status_code=201)
async def mint_goal_token(code: str, body: GoalTokenIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """A member mints a goal overlay for the group; the token is returned once."""
    from shrutisguides.progress import MOTIONS, THEMES
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    g = await _group(session, code)
    member = (await session.execute(select(GroupMember).where(GroupMember.group_id == g.id, GroupMember.user_id == user.id))).scalar_one_or_none()
    if member is None:
        raise HTTPException(403, "join the group first")
    token = secrets.token_urlsafe(24)
    row = OverlayToken(token=token, kind="guide-goal", label=body.label.strip()[:80] or g.name, user_id=user.id, group_id=g.id,
                       theme=body.theme if body.theme in THEMES else "almanac",
                       motion=body.motion if body.motion in MOTIONS else "reduced")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"id": row.id, "token": token, "kind": row.kind, "theme": row.theme, "motion": row.motion}


@router.delete("/{code}/overlays/{token_id}", status_code=204)
async def drop_goal_token(code: str, token_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> None:
    user = await _reader(request, session)
    g = await _group(session, code)
    row = (await session.execute(
        select(OverlayToken).where(OverlayToken.id == token_id, OverlayToken.group_id == g.id, OverlayToken.user_id == user.id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such overlay")
    await session.delete(row)
    await session.commit()
