# SPDX-License-Identifier: AGPL-3.0-only
"""
The Discord room, and the polls.

**The Discord call is made by this server, not by the visitor's browser.**
That is the whole reason it exists as a route: Discord's own embed widget is an
iframe, and an iframe means every reader's browser talks to Discord whether or
not they have an account there. The site currently makes zero third-party
requests on every page, which is rarer than any feature on it and trivially
easy to lose. So the server asks, caches the answer, and hands over a number.

What comes back is deliberately thin: how many people are in the room, and the
invite. Discord's widget also returns a list of who is online, with usernames
and avatar URLs, and that is not shown — displaying a hundred people's handles
on a public page because they happened to be in a voice channel is a thing
done to them, not for them.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.api.routes.accounts import current_user
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.models import Poll, PollOption, PollVote, PushSubscription
from shruti.models.accounts import User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/community", tags=["community"])

# Discord asks for no more than one call every few seconds per guild. A minute
# is far inside that and the number does not need to be fresher: "about thirty
# people are in there" does not become wrong in fifty seconds.
DISCORD_TTL = 60.0
_discord_cache: tuple[float, dict] | None = None


@router.get("/discord")
async def discord() -> dict:
    """
    How many are in the room right now.

    Never raises. A community panel that turns into an error because Discord
    had a bad minute is worse than one that quietly stops showing a number.
    """
    global _discord_cache
    s = get_settings()
    invite = s.discord_invite

    if not s.discord_guild_id:
        return {"online": None, "invite": invite, "name": ""}

    now = time.monotonic()
    if _discord_cache and now - _discord_cache[0] < DISCORD_TTL:
        return _discord_cache[1]

    answer = {"online": None, "invite": invite, "name": ""}
    try:
        import httpx

        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(
                f"https://discord.com/api/guilds/{s.discord_guild_id}/widget.json"
            )
        if r.status_code == 200:
            body = r.json()
            answer = {
                "online": body.get("presence_count"),
                # Their own invite when the widget carries one; hers otherwise.
                "invite": body.get("instant_invite") or invite,
                "name": body.get("name", ""),
                # Deliberately NOT body["members"]. See the module docstring.
            }
        elif r.status_code == 403:
            log.info("the Discord widget is disabled for this guild")
    except Exception:                                  # noqa: BLE001
        log.info("Discord did not answer; the panel will show the invite only")

    _discord_cache = (now, answer)
    return answer


# ── polls ───────────────────────────────────────────────────────────────────
#
# One vote per person, and "person" is the honest problem here. Signed in, it
# is the account. Signed out, it is a hash of address and browser for the day —
# the same construction the visit counter uses, and with the same limits: it
# cannot be joined across days and somebody determined can vote again from
# another network. That is a poll on a VTuber's website, not an election, and
# pretending otherwise would mean asking every voter to make an account.


def _voter(request: Request, user: User | None) -> str:
    if user is not None:
        return f"user:{user.id}"
    from shruti.api.routes.insight import _visitor

    return f"day:{_visitor(request, datetime.now(timezone.utc).date())}"


def _poll_payload(poll: Poll, options: list[PollOption], counts: dict[int, int],
                  mine: int | None) -> dict:
    total = sum(counts.values())
    return {
        "id": poll.id,
        "slug": poll.slug,
        "question": poll.question,
        "note": poll.note,
        "closesAt": poll.closes_at,
        "closed": poll.closed,
        "total": total,
        "youChose": mine,
        "options": [
            {
                "id": o.id,
                "label": o.label,
                "votes": counts.get(o.id or 0, 0),
                # Rounded for display only; the count above is the truth.
                "share": round(100 * counts.get(o.id or 0, 0) / total) if total else 0,
            }
            for o in options
        ],
    }


async def _load(poll: Poll, request: Request, user: User | None,
                session: AsyncSession) -> dict:
    options = (
        await session.execute(
            select(PollOption).where(PollOption.poll_id == poll.id)
            .order_by(PollOption.position, PollOption.id)
        )
    ).scalars().all()
    votes = (
        await session.execute(select(PollVote).where(PollVote.poll_id == poll.id))
    ).scalars().all()
    counts: dict[int, int] = {}
    for v in votes:
        counts[v.option_id] = counts.get(v.option_id, 0) + 1
    who = _voter(request, user)
    mine = next((v.option_id for v in votes if v.voter == who), None)
    return _poll_payload(poll, list(options), counts, mine)


@router.get("/polls/open")
async def open_polls(
    request: Request,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Every poll she has opened, newest first."""
    rows = (
        await session.execute(
            select(Poll).where(Poll.visible.is_(True)).order_by(Poll.id.desc())
        )
    ).scalars().all()
    return [await _load(p, request, user, session) for p in rows]


@router.get("/polls/{slug}")
async def one_poll(
    slug: str, request: Request,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    poll = (
        await session.execute(
            select(Poll).where(Poll.slug == slug, Poll.visible.is_(True))
        )
    ).scalar_one_or_none()
    if poll is None:
        raise HTTPException(404, "no such poll")
    return await _load(poll, request, user, session)


class VoteIn(BaseModel):
    option_id: int


@router.post("/polls/{slug}/vote")
async def vote(
    slug: str, body: VoteIn, request: Request,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Cast, or change, one vote.

    **Changing it moves the vote rather than adding one.** A poll that counts
    somebody twice because they reconsidered is a poll nobody should read.
    """
    poll = (
        await session.execute(
            select(Poll).where(Poll.slug == slug, Poll.visible.is_(True))
        )
    ).scalar_one_or_none()
    if poll is None:
        raise HTTPException(404, "no such poll")
    if poll.closed:
        raise HTTPException(409, "this poll has closed")
    if poll.closes_at and poll.closes_at < datetime.now(timezone.utc).isoformat():
        raise HTTPException(409, "this poll has closed")

    option = await session.get(PollOption, body.option_id)
    if option is None or option.poll_id != poll.id:
        raise HTTPException(400, "that is not one of the answers")

    who = _voter(request, user)
    existing = (
        await session.execute(
            select(PollVote).where(PollVote.poll_id == poll.id, PollVote.voter == who)
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(PollVote(poll_id=poll.id, option_id=option.id, voter=who))
    else:
        existing.option_id = option.id
    await session.commit()
    return await _load(poll, request, user, session)


# ── the admin side ──────────────────────────────────────────────────────────

class PollIn(BaseModel):
    question: str = Field(default="", max_length=200)
    note: str = Field(default="", max_length=400)
    slug: str = Field(default="", max_length=80)
    options: list[str] = Field(default_factory=list)
    closes_at: str = ""
    closed: bool = False
    visible: bool = True


def _slugify(text: str) -> str:
    import re

    out = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return out[:80] or "poll"


@router.get("/admin/polls", dependencies=[Depends(require_admin)])
async def admin_polls(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(Poll).order_by(Poll.id.desc()))
    ).scalars().all()
    out = []
    for poll in rows:
        options = (
            await session.execute(
                select(PollOption).where(PollOption.poll_id == poll.id)
                .order_by(PollOption.position, PollOption.id)
            )
        ).scalars().all()
        votes = (
            await session.execute(select(PollVote).where(PollVote.poll_id == poll.id))
        ).scalars().all()
        counts: dict[int, int] = {}
        for v in votes:
            counts[v.option_id] = counts.get(v.option_id, 0) + 1
        out.append({
            **_poll_payload(poll, list(options), counts, None),
            "visible": poll.visible,
        })
    return out


@router.post("/admin/polls", status_code=201, dependencies=[Depends(require_admin)])
async def create_poll(
    body: PollIn, session: AsyncSession = Depends(get_session)
) -> dict:
    labels = [o.strip() for o in body.options if o.strip()]
    if len(labels) < 2:
        raise HTTPException(400, "a poll needs at least two answers")
    slug = _slugify(body.slug or body.question)
    if (await session.execute(select(Poll).where(Poll.slug == slug))).scalar_one_or_none():
        slug = f"{slug}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"

    poll = Poll(slug=slug, question=body.question, note=body.note,
                closes_at=body.closes_at, closed=body.closed, visible=body.visible)
    session.add(poll)
    await session.commit()
    await session.refresh(poll)
    for i, label in enumerate(labels):
        session.add(PollOption(poll_id=poll.id, label=label[:120], position=i))
    await session.commit()
    return {"id": poll.id, "slug": poll.slug}


@router.put("/admin/polls/{poll_id}", dependencies=[Depends(require_admin)])
async def update_poll(
    poll_id: int, body: PollIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    The wording and the state, never the answers.

    Editing an answer after people have voted silently changes what their vote
    meant — the count stays attached to a row whose label now says something
    else. Answers are fixed at creation; a different set of answers is a
    different poll.
    """
    poll = await session.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "no such poll")
    poll.question = body.question
    poll.note = body.note
    poll.closes_at = body.closes_at
    poll.closed = body.closed
    poll.visible = body.visible
    await session.commit()
    return {"ok": True}


@router.delete("/admin/polls/{poll_id}", status_code=204,
               dependencies=[Depends(require_admin)])
async def delete_poll(
    poll_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    poll = await session.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(404, "no such poll")
    for model in (PollVote, PollOption):
        rows = (
            await session.execute(select(model).where(model.poll_id == poll_id))
        ).scalars().all()
        for r in rows:
            await session.delete(r)
    await session.delete(poll)
    await session.commit()
    return Response(status_code=204)


# ── being told ──────────────────────────────────────────────────────────────
#
# **Never account-gated.** Asking somebody to make an account before telling
# them a stream started is a toll booth on a favour. The account is only
# recorded when there already is one, so that deleting it takes the
# subscriptions with it.

class SubscribeIn(BaseModel):
    endpoint: str = Field(max_length=800)
    wants_live: bool = True
    wants_writing: bool = False


@router.get("/push/key")
async def push_key() -> dict:
    """
    The public half, for the browser to subscribe with.

    Returns an empty key rather than an error when push is not set up, so the
    button can say "not available yet" instead of the page showing a failure.
    """
    from shruti.core.push import configured

    s = get_settings()
    return {"key": s.vapid_public_key if configured() else ""}


@router.post("/push/subscribe", status_code=201)
async def push_subscribe(
    body: SubscribeIn,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not body.endpoint.startswith("https://"):
        raise HTTPException(400, "that is not a push endpoint")

    row = (
        await session.execute(
            select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
        )
    ).scalar_one_or_none()
    if row is None:
        row = PushSubscription(endpoint=body.endpoint)
        session.add(row)
    row.wants_live = body.wants_live
    row.wants_writing = body.wants_writing
    row.failures = 0
    if user is not None:
        row.user_id = user.id
    await session.commit()
    return {"ok": True}


@router.post("/push/unsubscribe", status_code=204)
async def push_unsubscribe(
    body: SubscribeIn, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Forget this browser.

    Deletes rather than flagging: somebody turning notifications off is asking
    to stop being on a list, not to be on it quietly.
    """
    row = (
        await session.execute(
            select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
        )
    ).scalar_one_or_none()
    if row is not None:
        await session.delete(row)
        await session.commit()
    return Response(status_code=204)


# What the service worker fetches after being woken. Held in memory rather than
# in a table: it is one line, it changes a few times a week, and a notice that
# does not survive a restart is the correct behaviour — a browser waking up an
# hour after a deploy should not be told about a stream that has ended.
_notice: dict = {
    "kind": "", "title": "", "body": "", "url": "/", "at": 0.0,
}
# After this, the notice is stale and the worker shows nothing rather than
# something wrong.
NOTICE_LIFE = 6 * 60 * 60


@router.get("/push/notice")
async def push_notice() -> dict:
    """
    What to say. Public, and deliberately says nothing about who is asking.

    Empty when nothing is current, and the service worker shows no
    notification at all in that case rather than an empty one.
    """
    if not _notice["title"] or time.monotonic() - _notice["at"] > NOTICE_LIFE:
        return {"title": ""}
    return {k: v for k, v in _notice.items() if k != "at"}


class NoticeIn(BaseModel):
    kind: str = Field(default="live", max_length=20)
    title: str = Field(max_length=120)
    body: str = Field(default="", max_length=200)
    url: str = Field(default="/", max_length=200)
    only_live_subscribers: bool = True


@router.post("/admin/push/send", dependencies=[Depends(require_admin)])
async def push_send(
    body: NoticeIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Wake everybody who asked, and tidy up the ones that have gone.

    A push service that keeps being handed a dead endpoint starts rate-limiting
    the sender, so pruning on 404/410 is housekeeping with consequences rather
    than neatness.
    """
    from shruti.core.push import configured, push_one

    if not configured():
        raise HTTPException(503, "push is not set up — no VAPID keys are configured")

    _notice.update({
        "kind": body.kind, "title": body.title, "body": body.body,
        "url": body.url, "at": time.monotonic(),
    })

    rows = (await session.execute(select(PushSubscription))).scalars().all()
    if body.only_live_subscribers:
        rows = [r for r in rows if r.wants_live]
    else:
        rows = [r for r in rows if r.wants_writing]

    sent = gone = failed = 0
    for row in rows:
        ok, status = await push_one(row.endpoint)
        if ok:
            sent += 1
            row.last_sent_at = datetime.now(timezone.utc)
            row.failures = 0
        elif status in (404, 410):
            gone += 1
            await session.delete(row)
        else:
            failed += 1
            row.failures += 1
    await session.commit()
    return {"sent": sent, "gone": gone, "failed": failed, "of": len(rows)}


@router.get("/admin/push/count", dependencies=[Depends(require_admin)])
async def push_count(session: AsyncSession = Depends(get_session)) -> dict:
    from shruti.core.push import configured

    rows = (await session.execute(select(PushSubscription))).scalars().all()
    return {
        "configured": configured(),
        "total": len(rows),
        "live": len([r for r in rows if r.wants_live]),
        "writing": len([r for r in rows if r.wants_writing]),
    }
