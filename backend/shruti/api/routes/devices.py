# SPDX-License-Identifier: AGPL-3.0-only
"""
Phones registering to be told things.

⚠ **No account required.** Somebody who installed the app to be told when a
stream starts should be told, whether or not they ever sign up — asking for an
account first is a toll booth on a favour. `user_id` is set when they happen to
be signed in, only so that deleting an account takes their devices with it, and
so that "somebody replied to your reading" has somewhere to go.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.db import get_session
from shruti.models.devices import AppDevice

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/devices", tags=["devices"])

PLATFORMS = {"android", "ios"}


class DeviceIn(BaseModel):
    token: str = Field(min_length=8, max_length=400)
    platform: str = "android"
    wants_live: bool = True
    wants_video: bool = True
    wants_horoscope: bool = False
    wants_writing: bool = False
    wants_replies: bool = True


def _out(row: AppDevice) -> dict:
    return {
        "platform": row.platform,
        "wantsLive": row.wants_live,
        "wantsVideo": row.wants_video,
        "wantsHoroscope": row.wants_horoscope,
        "wantsWriting": row.wants_writing,
        "wantsReplies": row.wants_replies,
        # So the app can say "replies need an account" rather than showing a
        # switch that quietly does nothing.
        "attachedToAccount": row.user_id is not None,
    }


@router.put("")
async def register(
    body: DeviceIn, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Register this phone, or change what it wants.

    ⚠ One row per token, updated rather than added to. A token that collected
    duplicate rows would mean being told twice about the same stream, which is
    the fastest way to make somebody turn all of it off.
    """
    from shruti.api.routes.accounts import current_user

    if body.platform not in PLATFORMS:
        raise HTTPException(400, "unknown platform")

    user = await current_user(request, session)
    row = (
        await session.execute(select(AppDevice).where(AppDevice.token == body.token))
    ).scalars().first()
    if row is None:
        row = AppDevice(token=body.token)
        session.add(row)

    row.platform = body.platform
    row.wants_live = body.wants_live
    row.wants_video = body.wants_video
    row.wants_horoscope = body.wants_horoscope
    row.wants_writing = body.wants_writing
    row.wants_replies = body.wants_replies
    # ⚠ Only ever attached, never detached here. Signing out on the phone
    # should stop replies reaching it, and that is what DELETE is for — but a
    # request that simply arrives without a session (an expired token, a
    # background refresh) must not silently orphan the device.
    if user is not None:
        row.user_id = user.id
    # A token that starts working again has served its sentence.
    row.failures = 0

    await session.commit()
    return _out(row)


@router.get("/{token}")
async def what_it_wants(
    token: str, session: AsyncSession = Depends(get_session),
) -> dict:
    row = (
        await session.execute(select(AppDevice).where(AppDevice.token == token))
    ).scalars().first()
    if row is None:
        raise HTTPException(404, "this device is not registered")
    return _out(row)


@router.delete("/{token}", status_code=204)
async def forget(
    token: str, session: AsyncSession = Depends(get_session),
) -> None:
    """
    Stop telling this phone anything.

    ⚠ Not gated on an account, deliberately. Somebody who wants notifications to
    stop must be able to stop them — including somebody who has lost the account
    they registered under, and including this app deleting its own row when the
    permission is revoked.
    """
    row = (
        await session.execute(select(AppDevice).where(AppDevice.token == token))
    ).scalars().first()
    if row is not None:
        await session.delete(row)
        await session.commit()


# ── the bot telling us something happened ───────────────────────────────────

class NoticeIn(BaseModel):
    kind: str
    title: str = Field(max_length=120)
    body: str = Field(default="", max_length=300)
    url: str = Field(default="/", max_length=300)


@router.post("/notify")
async def notify(
    body: NoticeIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Something happened that people asked to hear about.

    Called by the BOT, which is the only thing that knows when a stream starts:
    the site polls a status, the bot watches for the transition and already
    decides to say it once. Duplicating that decision here would mean two things
    with two ideas about whether she is live.

    ⚠ **Not public.** It wakes every phone that opted in, so an open endpoint
    here is an open endpoint for pushing a notification to her whole audience.
    A missing secret refuses everything rather than defaulting to open.
    """
    import hmac
    import os

    from shruti.core.notify import WHO, tell

    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    given = request.headers.get("X-Shruti-Internal", "")
    if not secret or not hmac.compare_digest(given, secret):
        raise HTTPException(401, "no")
    if body.kind not in WHO:
        raise HTTPException(422, f"no such kind; try one of {sorted(WHO)}")

    sent = await tell(session, body.kind, title=body.title,
                      body=body.body, url=body.url)
    return {"ok": True, "phones": sent.phones, "browsers": sent.browsers}
