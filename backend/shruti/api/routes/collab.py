# SPDX-License-Identifier: AGPL-3.0-only
"""
Saved groups for the collab planner.

The planner itself has no backend and needs none: the plan is the URL. This is
the one part that cannot be, because remembering a group across devices is
exactly the thing a URL cannot do for you — and it is therefore the honest
thing to offer an account for.

Nothing here is required to use the tool. Everything degrades to "keep the
link", which is what a signed-out visitor is told.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.routes.accounts import current_user
from shruti.core.db import get_session
from shruti.models.accounts import CollabGroup, User

router = APIRouter(prefix="/api/collab", tags=["collab"])

# A group is a handful of people, not a mailing list. The cap is here so a
# crafted request cannot turn a convenience into storage.
MAX_PEOPLE = 12
MAX_GROUPS = 40


class GroupIn(BaseModel):
    name: str = Field(default="", max_length=80)
    # One "name|zone|from|to" per entry, exactly as the page encodes them.
    participants: list[str] = Field(default_factory=list)


def _payload(g: CollabGroup) -> dict:
    return {
        "id": g.id,
        "name": g.name or "Untitled group",
        "participants": [p for p in g.participants.split("\n") if p.strip()],
    }


@router.get("/groups")
async def list_groups(
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Hers, newest first. Signed out is an empty list rather than an error."""
    if user is None:
        return []
    rows = (
        await session.execute(
            select(CollabGroup)
            .where(CollabGroup.user_id == user.id)
            .order_by(CollabGroup.updated_at.desc())
        )
    ).scalars().all()
    return [_payload(g) for g in rows]


@router.post("/groups", status_code=201)
async def save_group(
    body: GroupIn,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep a group.

    Saving the same name twice updates rather than duplicating: somebody
    adjusting one person's hours and pressing save again means "this group,
    corrected", and two rows with one name would be worse than either outcome.
    """
    if user is None:
        raise HTTPException(401, "sign in to keep a group")

    people = [p.strip() for p in body.participants if p.strip()][:MAX_PEOPLE]
    if not people:
        raise HTTPException(422, "there is nobody in that group")

    name = body.name.strip() or "Untitled group"
    existing = (
        await session.execute(
            select(CollabGroup)
            .where(CollabGroup.user_id == user.id, CollabGroup.name == name)
        )
    ).scalars().first()

    if existing is None:
        count = len((
            await session.execute(
                select(CollabGroup).where(CollabGroup.user_id == user.id)
            )
        ).scalars().all())
        if count >= MAX_GROUPS:
            raise HTTPException(409, "that is a lot of groups — delete one first")
        existing = CollabGroup(user_id=user.id, name=name)
        session.add(existing)

    existing.participants = "\n".join(people)
    await session.commit()
    await session.refresh(existing)
    return _payload(existing)


@router.delete("/groups/{group_id}", status_code=204)
async def delete_group(
    group_id: int,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    if user is None:
        raise HTTPException(401, "sign in first")
    row = await session.get(CollabGroup, group_id)
    # A wrong owner is told the same thing as a missing row: whether somebody
    # else's group exists is not this person's business.
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "no such group")
    await session.delete(row)
    await session.commit()
