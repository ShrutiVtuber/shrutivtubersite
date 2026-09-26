# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio, the Carnatic music school at /carnatic: its data, what it keeps
about a person, songs and sheets, the Listen room, the review queue, and the
codes that sign the app in. The contract is docs/carnatic/API.md.

⚠ **Nothing here is ever a wall.** Reading the data needs no account, and
`GET /me` answers signed-out visitors rather than refusing them. An account
keeps things across devices and is needed to publish; nothing else.

⚠ **Route order.** The literal paths (`/songs/mine`-style, `/listen/comments`,
`/device-link/redeem`) are declared before the `{id}` routes they would
otherwise be read as. `test_carnatic.py` holds the order.
"""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.deps import require_admin
from shruti.api.routes.accounts import current_user, require_user
from shruti.core import carnatic as rules
from shruti.core.config import get_settings
from shruti.core.db import get_session
from shruti.core.sessions import issue_session
from shruti.models.accounts import Supporter, User
from shruti.models.carnatic import (
    CarnaticComment, CarnaticDeviceLink, CarnaticLike, CarnaticPost, CarnaticPracticeDay,
    CarnaticProfile, CarnaticProgress, CarnaticReport, CarnaticReview, CarnaticSong,
)

router = APIRouter(prefix="/api/carnatic", tags=["carnatic"])

# Per backend process; see docs/carnatic/API.md §1b.
FAILED_BY_CLIENT = rules.Window(limit=10)
FAILED_CODES = rules.Window(limit=100)
CREATED_BY_USER = rules.Window(limit=30)
# Listen, the same for the website and the app (API.md §6): a person may
# share 10 performances an hour, write 30 comments in 10 minutes and file
# 30 reports an hour. Past that, 429 SLOW_DOWN.
SHARED_BY_USER = rules.Window(limit=10, seconds=3600)
COMMENTED_BY_USER = rules.Window(limit=30, seconds=600)
REPORTED_BY_USER = rules.Window(limit=30, seconds=3600)
SLOW_DOWN = {"code": "SLOW_DOWN", "detail": "That is a lot at once. Please wait a little and try again."}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _public_name(user: User | None) -> str:
    """Never the front half of an email address."""
    name = (getattr(user, "display_name", "") or "").strip()
    return name or "somebody"


async def is_supporter(user: User | None, session: AsyncSession) -> bool:
    """
    A Swaras supporter: a live subscription at any tier. The owner's rule is
    that a Swaras supporter gets every gated tool, Swara Studio included. The
    operator is never limited on her own site.
    """
    if user is None:
        return False
    rows = (await session.execute(
        select(Supporter).where((Supporter.user_id == user.id) | (Supporter.email == user.email.lower()))
    )).scalars().all()
    if any(r.status in {"active", "trialing"} for r in rows):
        return True
    from shruti.core.operator import operator_email
    op = (await operator_email(session) or "").strip().lower()
    return bool(op) and op == (user.email or "").strip().lower()


# ── the data ────────────────────────────────────────────────────────────────

@router.get("/data/manifest")
def data_manifest(request: Request):
    """What is published: every file with its digest. 404 means nothing is yet."""
    m = rules.manifest()
    if m is None:
        raise HTTPException(404, "The school's data has not been published yet.")
    etag = f'"{m.get("digest", "")}"'
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag, "Cache-Control": "no-cache"})
    return JSONResponse(m, headers={"ETag": etag, "Cache-Control": "no-cache"})


@router.get("/data/version")
def data_version(request: Request):
    """
    The cheapest question the app can ask: has anything changed? The digest
    is the manifest's own (a hash over every file's digest), so an unchanged
    digest means every file is unchanged.
    """
    m = rules.manifest()
    if m is None:
        raise HTTPException(404, "The school's data has not been published yet.")
    etag = f'"{m.get("digest", "")}"'
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag, "Cache-Control": "no-cache"})
    return JSONResponse({"format": m.get("format"), "digest": m.get("digest"), "built_at": m.get("built_at")},
                        headers={"ETag": etag, "Cache-Control": "no-cache"})


@router.get("/data/{name}")
def data_file(name: str, request: Request):
    path = rules.data_path(name)
    if path is None:
        raise HTTPException(404, "No such data file.")
    etag = f'"{rules.digest_of(name)}"'
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})
    return FileResponse(path, media_type="application/json; charset=utf-8",
                        headers={"ETag": etag, "Cache-Control": "public, max-age=300"})


@router.get("/reviews")
async def reviews(session: AsyncSession = Depends(get_session)) -> dict:
    """Which script names and flagged facts a reviewer has checked. Absent means unverified."""
    rows = (await session.execute(select(CarnaticReview))).scalars().all()
    latest = max((r.updated_at for r in rows), default=None)
    return {"items": {r.key: {"status": r.status, "text": r.text} for r in rows}, "updatedAt": _iso(latest)}


# ── who is asking ───────────────────────────────────────────────────────────

@router.get("/me")
async def me(user: User | None = Depends(current_user), session: AsyncSession = Depends(get_session)) -> dict:
    """Never 401: a signed-out visitor is an ordinary visitor."""
    supporter = await is_supporter(user, session)
    if user is None:
        return {"signedIn": False, "limits": {"partsPerSong": rules.part_limit(False)}, "settings": None}
    profile = await session.get(CarnaticProfile, user.id)
    return {
        "signedIn": True,
        "displayName": _public_name(user) if user.display_name else "",
        "supporter": supporter,
        "limits": {"partsPerSong": rules.part_limit(supporter)},
        "settings": rules.with_defaults(profile.settings if profile else None),
        "settingsUpdatedAt": _iso(profile.updated_at) if profile else None,
    }


# ── settings ────────────────────────────────────────────────────────────────

class SettingsIn(BaseModel):
    settings: dict
    baseUpdatedAt: str | None = None


def _same_moment(a: datetime | None, b: str | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    try:
        parsed = datetime.fromisoformat(b)
    except ValueError:
        return False
    if a.tzinfo is None:
        a = a.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return abs((a - parsed).total_seconds()) < 0.001


@router.get("/me/settings")
async def get_settings_(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    profile = await session.get(CarnaticProfile, user.id)
    return {"settings": rules.with_defaults(profile.settings if profile else None),
            "updatedAt": _iso(profile.updated_at) if profile else None}


@router.put("/me/settings")
async def put_settings(body: SettingsIn, user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)):
    try:
        clean = rules.clean_settings(body.settings)
    except rules.Invalid as e:
        raise HTTPException(422, str(e))
    profile = await session.get(CarnaticProfile, user.id)
    if profile is not None and not _same_moment(profile.updated_at, body.baseUpdatedAt):
        # Another device saved in between: hand back theirs rather than overwrite it.
        return JSONResponse(status_code=409, content={
            "code": "CONFLICT", "detail": "These settings were changed on another device.",
            "settings": rules.with_defaults(profile.settings), "updatedAt": _iso(profile.updated_at)})
    if profile is None:
        profile = CarnaticProfile(user_id=user.id, settings=clean)
        session.add(profile)
    else:
        profile.settings = clean
        profile.updated_at = _now()
    await session.commit()
    await session.refresh(profile)
    return {"settings": rules.with_defaults(profile.settings), "updatedAt": _iso(profile.updated_at)}


# ── progress and the practice log ───────────────────────────────────────────

class ProgressIn(BaseModel):
    speeds: list[int] = Field(default_factory=list, max_length=4)
    reset: bool = False


@router.get("/me/progress")
async def get_progress(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticProgress).where(CarnaticProgress.user_id == user.id))).scalars().all()
    return {"items": {r.item_id: {"speeds": sorted(r.speeds), "updatedAt": _iso(r.updated_at)} for r in rows}}


@router.put("/me/progress/{item_id}")
async def put_progress(item_id: str, body: ProgressIn, user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)) -> dict:
    if not re.fullmatch(r"[a-z0-9_]{1,60}", item_id):
        raise HTTPException(422, "That is not a path item.")
    if any(s not in (1, 2, 3, 4) for s in body.speeds):
        raise HTTPException(422, "Speeds are 1 to 4.")
    row = (await session.execute(select(CarnaticProgress).where(
        CarnaticProgress.user_id == user.id, CarnaticProgress.item_id == item_id))).scalar_one_or_none()
    if row is None:
        row = CarnaticProgress(user_id=user.id, item_id=item_id, speeds=sorted(set(body.speeds)))
        session.add(row)
    else:
        # Only upwards, unless the person asked to start again: a stale phone
        # syncing late must never un-finish anything.
        row.speeds = sorted(set(body.speeds)) if body.reset else sorted(set(row.speeds) | set(body.speeds))
        row.updated_at = _now()
    await session.commit()
    return {"itemId": item_id, "speeds": row.speeds, "updatedAt": _iso(row.updated_at)}


class PracticeIn(BaseModel):
    day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    seconds: int = Field(ge=1, le=6 * 3600)


@router.post("/me/practice")
async def add_practice(body: PracticeIn, user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)) -> dict:
    row = (await session.execute(select(CarnaticPracticeDay).where(
        CarnaticPracticeDay.user_id == user.id, CarnaticPracticeDay.day == body.day))).scalar_one_or_none()
    if row is None:
        row = CarnaticPracticeDay(user_id=user.id, day=body.day, seconds=body.seconds, sessions=1)
        session.add(row)
    else:
        row.seconds = min(row.seconds + body.seconds, 24 * 3600)
        row.sessions += 1
        row.updated_at = _now()
    await session.commit()
    return {"day": row.day, "seconds": row.seconds, "sessions": row.sessions}


@router.get("/me/practice")
async def get_practice(month: str = Query(pattern=r"^\d{4}-\d{2}$"), user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)) -> dict:
    """Time per day this month. It counts time; it never counts days missed."""
    rows = (await session.execute(select(CarnaticPracticeDay).where(
        CarnaticPracticeDay.user_id == user.id, CarnaticPracticeDay.day.like(f"{month}-%")))).scalars().all()
    return {"days": {r.day: r.seconds for r in rows},
            "totalSeconds": sum(r.seconds for r in rows), "sessions": sum(r.sessions for r in rows)}


# ── songs and sheets ────────────────────────────────────────────────────────

class SongIn(BaseModel):
    song: dict
    baseUpdatedAt: str | None = None


def _song_summary(s: CarnaticSong) -> dict:
    return {"id": s.id, "slug": s.slug, "title": s.title, "raga": s.raga, "tala": s.tala,
            "published": s.published, "publishedAt": _iso(s.published_at), "updatedAt": _iso(s.updated_at)}


def _song_full(s: CarnaticSong) -> dict:
    return {**_song_summary(s), "song": s.body}


class PartLimit(Exception):
    def __init__(self, limit: int):
        self.limit = limit

    def response(self) -> JSONResponse:
        return JSONResponse(status_code=413, content={
            "code": "PART_LIMIT", "limit": self.limit,
            "detail": f"Songs have up to {self.limit} parts. Swaras supporters can add more."})


async def _check_body(body: dict, user: User, session: AsyncSession, before: dict | None = None) -> dict:
    try:
        rules.check_song(body)
    except rules.Invalid as e:
        raise HTTPException(422, str(e))
    limit = rules.part_limit(await is_supporter(user, session))
    parts = rules.parts_in(body)
    # A song kept from a supporter year keeps its parts; it cannot grow past
    # the limit, and saving it without adding one is always accepted.
    if limit is not None and parts > limit and parts > rules.parts_in(before or {}):
        raise PartLimit(limit)
    return body


async def _mine(song_id: int, user: User, session: AsyncSession) -> CarnaticSong:
    s = await session.get(CarnaticSong, song_id)
    if s is None or s.user_id != user.id:
        raise HTTPException(404, "No such song.")
    return s


@router.get("/songs")
async def my_songs(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    rows = (await session.execute(select(CarnaticSong).where(CarnaticSong.user_id == user.id)
                                  .order_by(CarnaticSong.updated_at.desc()))).scalars().all()
    return {"items": [_song_summary(s) for s in rows]}


@router.post("/songs", status_code=201)
async def create_song(body: SongIn, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)):
    n = (await session.execute(select(func.count()).select_from(CarnaticSong)
                               .where(CarnaticSong.user_id == user.id))).scalar_one()
    if n >= rules.SONGS_PER_PERSON:
        raise HTTPException(422, f"An account keeps up to {rules.SONGS_PER_PERSON} songs.")
    try:
        song = await _check_body(body.song, user, session)
    except PartLimit as e:
        return e.response()
    row = CarnaticSong(user_id=user.id, slug=rules.song_slug(song["title"]), title=song["title"].strip(),
                       raga=str(song.get("raga", ""))[:60], tala=song["tala"], body=song)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _song_full(row)


@router.get("/sheets/{slug}")
async def sheet(slug: str, viewer: User | None = Depends(current_user),
                session: AsyncSession = Depends(get_session)) -> dict:
    """A published song, for anyone; an unpublished one only for its author (the preview)."""
    row = (await session.execute(select(CarnaticSong).where(CarnaticSong.slug == slug))).scalar_one_or_none()
    if row is None or (not row.published and (viewer is None or viewer.id != row.user_id)):
        raise HTTPException(404, "No such sheet.")
    author = await session.get(User, row.user_id)
    ragas = rules.data("ragas.json") or {}
    raga = next((r for r in ragas.get("janyas", []) + ragas.get("performed", []) if r["id"] == row.raga), None)
    return {**_song_full(row), "author": _public_name(author), "mine": bool(viewer and viewer.id == row.user_id),
            "outOfRaga": rules.out_of_raga(row.body, raga)}


@router.get("/songs/{song_id}")
async def get_song(song_id: int, user: User = Depends(require_user),
                   session: AsyncSession = Depends(get_session)) -> dict:
    return _song_full(await _mine(song_id, user, session))


@router.put("/songs/{song_id}")
async def put_song(song_id: int, body: SongIn, user: User = Depends(require_user),
                   session: AsyncSession = Depends(get_session)):
    row = await _mine(song_id, user, session)
    if not _same_moment(row.updated_at, body.baseUpdatedAt):
        return JSONResponse(status_code=409, content={
            "code": "CONFLICT", "detail": "This song was changed on another device.", **_song_full(row),
            "updatedAt": _iso(row.updated_at)})
    try:
        song = await _check_body(body.song, user, session, before=row.body)
    except PartLimit as e:
        return e.response()
    row.body, row.title, row.raga, row.tala = song, song["title"].strip(), str(song.get("raga", ""))[:60], song["tala"]
    row.updated_at = _now()
    await session.commit()
    await session.refresh(row)
    return _song_full(row)


@router.delete("/songs/{song_id}", status_code=204)
async def delete_song(song_id: int, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)) -> Response:
    row = await _mine(song_id, user, session)
    await session.delete(row)
    await session.commit()
    return Response(status_code=204)


@router.post("/songs/{song_id}/publish")
async def publish_song(song_id: int, user: User = Depends(require_user),
                       session: AsyncSession = Depends(get_session)) -> dict:
    row = await _mine(song_id, user, session)
    row.published, row.published_at = True, row.published_at or _now()
    await session.commit()
    await session.refresh(row)
    return _song_summary(row)


@router.post("/songs/{song_id}/unpublish")
async def unpublish_song(song_id: int, user: User = Depends(require_user),
                         session: AsyncSession = Depends(get_session)) -> dict:
    row = await _mine(song_id, user, session)
    row.published = False
    await session.commit()
    await session.refresh(row)
    return _song_summary(row)


# ── Listen ──────────────────────────────────────────────────────────────────

class PostIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    instrument: str = Field(default="", max_length=30)
    raga: str = Field(default="", max_length=60)
    tala: str = Field(default="", max_length=40)
    url: str = Field(max_length=500)
    sheetSlug: str | None = Field(default=None, max_length=80)


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


async def _post_view(p: CarnaticPost, viewer: User | None, session: AsyncSession) -> dict:
    author = await session.get(User, p.user_id)
    likes = (await session.execute(select(func.count()).select_from(CarnaticLike)
                                   .where(CarnaticLike.post_id == p.id))).scalar_one()
    comments = (await session.execute(select(func.count()).select_from(CarnaticComment)
                                      .where(CarnaticComment.post_id == p.id, CarnaticComment.hidden.is_(False)))).scalar_one()
    liked = False
    if viewer is not None:
        liked = (await session.get(CarnaticLike, (p.id, viewer.id))) is not None
    sheet = await session.get(CarnaticSong, p.song_id) if p.song_id else None
    return {"id": p.id, "title": p.title, "author": _public_name(author), "mine": bool(viewer and viewer.id == p.user_id),
            "instrument": p.instrument, "raga": p.raga, "tala": p.tala,
            "player": {"kind": p.player, "url": p.url},
            "sheetSlug": sheet.slug if sheet is not None and sheet.published else None,
            "likes": likes, "liked": liked, "comments": comments, "createdAt": _iso(p.created_at)}


@router.get("/listen")
async def listen(raga: str = "", tala: str = "", instrument: str = "", before: int | None = None,
                 viewer: User | None = Depends(current_user), session: AsyncSession = Depends(get_session)) -> dict:
    q = select(CarnaticPost).where(CarnaticPost.hidden.is_(False))
    if raga:
        q = q.where(CarnaticPost.raga == raga)
    if tala:
        q = q.where(CarnaticPost.tala == tala)
    if instrument:
        q = q.where(CarnaticPost.instrument == instrument)
    if before:
        q = q.where(CarnaticPost.id < before)
    rows = (await session.execute(q.order_by(CarnaticPost.id.desc()).limit(25))).scalars().all()
    items = [await _post_view(p, viewer, session) for p in rows]
    return {"items": items, "next": rows[-1].id if len(rows) == 25 else None}


@router.post("/listen", status_code=201)
async def share(body: PostIn, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    if SHARED_BY_USER.full(str(user.id)):
        return JSONResponse(status_code=429, content=SLOW_DOWN)
    player = rules.player_of(body.url)
    if player is None:
        raise HTTPException(422, "Share a YouTube, SoundCloud, Vimeo or Bandcamp link.")
    song_id = None
    if body.sheetSlug:
        song = (await session.execute(select(CarnaticSong).where(CarnaticSong.slug == body.sheetSlug))).scalar_one_or_none()
        if song is None or song.user_id != user.id:
            raise HTTPException(422, "That sheet is not one of yours.")
        song_id = song.id
    row = CarnaticPost(user_id=user.id, song_id=song_id, title=body.title.strip(), instrument=body.instrument,
                       raga=body.raga, tala=body.tala, player=player, url=body.url.strip())
    session.add(row)
    await session.commit()
    SHARED_BY_USER.add(str(user.id))
    await session.refresh(row)
    return await _post_view(row, user, session)


@router.delete("/listen/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user: User = Depends(require_user),
                         session: AsyncSession = Depends(get_session)) -> Response:
    c = await session.get(CarnaticComment, comment_id)
    if c is None or c.user_id != user.id:
        raise HTTPException(404, "No such comment.")
    await session.delete(c)
    await session.commit()
    return Response(status_code=204)


@router.delete("/listen/{post_id}", status_code=204)
async def delete_post(post_id: int, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)) -> Response:
    p = await session.get(CarnaticPost, post_id)
    if p is None or p.user_id != user.id:
        raise HTTPException(404, "No such post.")
    await session.delete(p)
    await session.commit()
    return Response(status_code=204)


@router.get("/listen/{post_id}")
async def listen_post(post_id: int, viewer: User | None = Depends(current_user),
                      session: AsyncSession = Depends(get_session)) -> dict:
    """One post, as the list shows it. A hidden post is not found, for anyone."""
    return await _post_view(await _visible_post(post_id, session), viewer, session)


async def _visible_post(post_id: int, session: AsyncSession) -> CarnaticPost:
    p = await session.get(CarnaticPost, post_id)
    if p is None or p.hidden:
        raise HTTPException(404, "No such post.")
    return p


@router.put("/listen/{post_id}/like")
async def like(post_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    await _visible_post(post_id, session)
    if await session.get(CarnaticLike, (post_id, user.id)) is None:
        session.add(CarnaticLike(post_id=post_id, user_id=user.id, created_at=_now()))
        await session.commit()
    return {"liked": True}


@router.delete("/listen/{post_id}/like")
async def unlike(post_id: int, user: User = Depends(require_user), session: AsyncSession = Depends(get_session)) -> dict:
    await session.execute(delete(CarnaticLike).where(CarnaticLike.post_id == post_id, CarnaticLike.user_id == user.id))
    await session.commit()
    return {"liked": False}


@router.get("/listen/{post_id}/comments")
async def comments(post_id: int, viewer: User | None = Depends(current_user),
                   session: AsyncSession = Depends(get_session)) -> dict:
    await _visible_post(post_id, session)
    rows = (await session.execute(select(CarnaticComment).where(
        CarnaticComment.post_id == post_id, CarnaticComment.hidden.is_(False)).order_by(CarnaticComment.id))).scalars().all()
    out = []
    for c in rows:
        author = await session.get(User, c.user_id)
        out.append({"id": c.id, "author": _public_name(author), "mine": bool(viewer and viewer.id == c.user_id),
                    "body": c.body, "createdAt": _iso(c.created_at)})
    return {"items": out}


@router.post("/listen/{post_id}/comments", status_code=201)
async def comment(post_id: int, body: CommentIn, user: User = Depends(require_user),
                  session: AsyncSession = Depends(get_session)):
    await _visible_post(post_id, session)
    if COMMENTED_BY_USER.full(str(user.id)):
        return JSONResponse(status_code=429, content=SLOW_DOWN)
    row = CarnaticComment(post_id=post_id, user_id=user.id, body=body.body.strip())
    session.add(row)
    await session.commit()
    COMMENTED_BY_USER.add(str(user.id))
    await session.refresh(row)
    return {"id": row.id, "author": _public_name(user), "mine": True, "body": row.body, "createdAt": _iso(row.created_at)}


class ReportIn(BaseModel):
    reason: str = Field(default="", max_length=300)


async def _report(user: User, reason: str, session: AsyncSession, *, post_id: int | None = None,
                  comment_id: int | None = None):
    """One report per person per thing; a second is accepted and changes nothing."""
    col = CarnaticReport.post_id if post_id is not None else CarnaticReport.comment_id
    ref = post_id if post_id is not None else comment_id
    existing = (await session.execute(select(CarnaticReport).where(
        CarnaticReport.user_id == user.id, col == ref))).scalar_one_or_none()
    if existing is None:
        if REPORTED_BY_USER.full(str(user.id)):
            return JSONResponse(status_code=429, content=SLOW_DOWN)
        session.add(CarnaticReport(user_id=user.id, post_id=post_id, comment_id=comment_id, reason=reason.strip()))
        await session.commit()
        REPORTED_BY_USER.add(str(user.id))
    return {"reported": True}


@router.post("/listen/comments/{comment_id}/report")
async def report_comment(comment_id: int, body: ReportIn, user: User = Depends(require_user),
                         session: AsyncSession = Depends(get_session)):
    c = await session.get(CarnaticComment, comment_id)
    if c is None or c.hidden:
        raise HTTPException(404, "No such comment.")
    return await _report(user, body.reason, session, comment_id=comment_id)


@router.post("/listen/{post_id}/report")
async def report_post(post_id: int, body: ReportIn, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)):
    await _visible_post(post_id, session)
    return await _report(user, body.reason, session, post_id=post_id)


# ── signing in on the app ───────────────────────────────────────────────────

class RedeemIn(BaseModel):
    token: str | None = Field(default=None, max_length=200)
    code: str | None = Field(default=None, max_length=40)
    device_name: str | None = Field(default=None, max_length=200)


INVALID_LINK = {"code": "INVALID_LINK", "detail": "This sign-in code is not valid. Make a new one on the website."}
TOO_MANY = {"code": "TOO_MANY_ATTEMPTS", "detail": "Too many attempts. Please wait a few minutes and try again."}


def _client(request: Request) -> str:
    forwarded = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


@router.post("/device-link", status_code=201)
async def create_link(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    key = f"user:{user.id}"
    if CREATED_BY_USER.full(key):
        return JSONResponse(status_code=429, content=TOO_MANY)
    CREATED_BY_USER.add(key)
    now = _now()
    live = (await session.execute(select(CarnaticDeviceLink).where(
        CarnaticDeviceLink.user_id == user.id, CarnaticDeviceLink.used_at.is_(None),
        CarnaticDeviceLink.revoked_at.is_(None), CarnaticDeviceLink.expires_at > now)
        .order_by(CarnaticDeviceLink.id))).scalars().all()
    for old in live[: max(0, len(live) - (rules.LIVE_LINKS - 1))]:
        old.revoked_at = now
    token = secrets.token_urlsafe(32)
    code = rules.new_code()
    row = CarnaticDeviceLink(user_id=user.id, token_hash=rules.token_hash(token),
                             code_hash=rules.code_hash(code.replace("-", ""), get_settings().secret_key),
                             expires_at=now + timedelta(seconds=rules.LINK_SECONDS))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"link_id": row.id, "code": code, "token": token, "qr_payload": f"swarastudio://link?t={token}",
            "expires_at": _iso(row.expires_at), "expires_in": rules.LINK_SECONDS}


@router.post("/device-link/redeem")
async def redeem(body: RedeemIn, request: Request, session: AsyncSession = Depends(get_session)):
    client = _client(request)
    if FAILED_BY_CLIENT.full(client):
        return JSONResponse(status_code=429, content=TOO_MANY)
    typed = body.code is not None and body.token is None
    if typed and FAILED_CODES.full("all"):
        return JSONResponse(status_code=429, content=TOO_MANY)

    def fail():
        FAILED_BY_CLIENT.add(client)
        if typed:
            FAILED_CODES.add("all")
        return JSONResponse(status_code=400, content=INVALID_LINK)

    if (body.token is None) == (body.code is None):
        return fail()
    if body.token is not None:
        where = CarnaticDeviceLink.token_hash == rules.token_hash(body.token.strip())
    else:
        code = rules.normalise_code(body.code or "")
        if code is None:
            return fail()
        where = CarnaticDeviceLink.code_hash == rules.code_hash(code, get_settings().secret_key)
    now = _now()
    # Marked used in one statement, so two phones racing for one code get one sign-in.
    claimed = (await session.execute(
        update(CarnaticDeviceLink)
        .where(where, CarnaticDeviceLink.used_at.is_(None), CarnaticDeviceLink.revoked_at.is_(None),
               CarnaticDeviceLink.expires_at > now)
        .values(used_at=now, method="code" if typed else "qr",
                device_name=(body.device_name or "")[:64],
                user_agent=(request.headers.get("user-agent") or "")[:255])
        .returning(CarnaticDeviceLink.user_id)
    )).scalar_one_or_none()
    if claimed is None:
        await session.rollback()
        return fail()
    await session.commit()
    user = await session.get(User, claimed)
    if user is None:
        return fail()
    token = issue_session(user.id, user.email)
    return {"access_token": token, "token_type": "bearer", "token": token,
            "id": user.id, "email": user.email, "displayName": user.display_name}


@router.get("/device-link/{link_id}/status")
async def link_status(link_id: int, user: User = Depends(require_user),
                      session: AsyncSession = Depends(get_session)) -> dict:
    row = await session.get(CarnaticDeviceLink, link_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Not found")
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=timezone.utc)
    status = "used" if row.used_at else ("expired" if row.revoked_at or expires <= _now() else "pending")
    return {"status": status, "expires_at": _iso(row.expires_at), "used_at": _iso(row.used_at)}


# ── the review queue and moderation (the operator) ──────────────────────────

class ReviewIn(BaseModel):
    key: str = Field(min_length=3, max_length=120, pattern=r"^[a-z]+:[A-Za-z0-9:_.\-]+$")
    status: str = Field(pattern=r"^(confirmed|corrected|reopened)$")
    text: str | None = Field(default=None, max_length=200)
    note: str = Field(default="", max_length=500)


LANGS = {"ta": "Tamil", "te": "Telugu", "kn": "Kannada"}


def queue_items(ragas: dict | None, instruments: dict | None) -> list[dict]:
    """
    Everything that awaits a reader or a consultant, derived from the data:
    every Tamil, Telugu and Kannada name, and every fact below high confidence
    that the pages show a note for. Built on each request from the synced
    files, so the queue follows the research without a migration.
    """
    items: list[dict] = []
    if ragas:
        def scripts(prefix: str, rid: str, name: str, s: dict, where: str):
            for lang, label in LANGS.items():
                if lang == "ta":
                    for style in ("grantha", "pure"):
                        text = (s.get("ta") or {}).get(style)
                        if text:
                            suffix = "" if style == "grantha" else ":pure"
                            items.append({"key": f"script:{prefix}:{rid}:ta{suffix}", "item": text,
                                          "what": f"{name} · raga name · Tamil{' (pure-Tamil style)' if suffix else ''}",
                                          "flag": "Script name not yet checked by a native reader",
                                          "level": "unverified", "where": where, "lang": "ta"})
                elif s.get(lang):
                    items.append({"key": f"script:{prefix}:{rid}:{lang}", "item": s[lang],
                                  "what": f"{name} · raga name · {label}",
                                  "flag": "Script name not yet checked by a native reader",
                                  "level": "unverified", "where": where, "lang": lang})
        for r in ragas.get("janyas", []):
            scripts("janya", r["id"], r["name"], r.get("scripts") or {}, "ragas/janya.json")
        # A melakarta raga's page (Todi, Kalyani…) shows its mela's names, so
        # it has no keys of its own: `script:mela:N:lang` clears both.
        for r in ragas.get("janyas", []) + ragas.get("performed", []):
            if r.get("confidence") in ("medium", "low"):
                items.append({"key": f"fact:raga:{r['id']}", "item": r["name"],
                              "what": f"{r['name']} · lakshana", "flag": (r.get("confidenceReason") or "")[:160],
                              "level": r["confidence"], "where": "ragas/janya.json"})
        for m in ragas.get("melakartas", []):
            scripts("mela", str(m["number"]), f"{m['number']} {m['name']}", m.get("scripts") or {}, "ragas/melakarta.json")
    if instruments:
        for f in (instruments.get("venu") or {}).get("fingerings", []):
            if f.get("confidence") in ("low", "unknown"):
                key = f"fact:venu:{f['sthayi']}-{f['swara']}-{f.get('kind', 'primary')}"
                items.append({"key": key, "item": f"{f['sthayi']} {f['swara']} · venu",
                              "what": f"{f['sthayi'].capitalize()} {f['swara']} · venu",
                              "flag": "Fingering varies by flute", "level": f["confidence"],
                              "where": "instruments/venu"})
        for s in (instruments.get("mridangam") or {}).get("strokes", []):
            for lang, cell in (s.get("scripts") or {}).items():
                if cell and cell.get("text"):
                    items.append({"key": f"script:stroke:{s['id']}:{lang}", "item": cell["text"],
                                  "what": f"{s['id']} · mridangam stroke · {LANGS[lang]}",
                                  "flag": "Sourced; not yet checked by a native reader" if cell.get("sourced")
                                  else "Transliterated candidate; not sourced",
                                  "level": "unverified", "where": "instruments/mridangam", "lang": lang})
    return items


@router.get("/admin/queue")
async def admin_queue(_: str = Depends(require_admin), session: AsyncSession = Depends(get_session)) -> dict:
    rows = {r.key: r for r in (await session.execute(select(CarnaticReview))).scalars().all()}
    items = queue_items(rules.data("ragas.json"), rules.data("instruments.json"))
    for it in items:
        r = rows.get(it["key"])
        it["review"] = {"status": r.status, "text": r.text, "note": r.note, "by": r.reviewed_by,
                        "at": _iso(r.updated_at)} if r else None
    open_items = [i for i in items if i["review"] is None]
    posts = (await session.execute(select(func.count()).select_from(CarnaticPost)
                                   .where(CarnaticPost.hidden.is_(True)))).scalar_one()
    return {"loaded": rules.manifest() is not None, "open": len(open_items), "total": len(items),
            "items": items, "hiddenPosts": posts}


@router.post("/admin/reviews")
async def admin_review(body: ReviewIn, operator: str = Depends(require_admin),
                       session: AsyncSession = Depends(get_session)) -> dict:
    if body.status == "corrected" and not (body.text or "").strip():
        raise HTTPException(422, "A correction needs the corrected text.")
    row = await session.get(CarnaticReview, body.key)
    if body.status == "reopened":
        if row is not None:
            await session.delete(row)
            await session.commit()
        return {"key": body.key, "status": None}
    if row is None:
        row = CarnaticReview(key=body.key, status=body.status)
        session.add(row)
    row.status, row.text, row.note, row.reviewed_by = body.status, (body.text or "").strip() or None, body.note, operator
    row.updated_at = _now()
    await session.commit()
    return {"key": row.key, "status": row.status, "text": row.text}


@router.get("/admin/moderation")
async def admin_moderation(_: str = Depends(require_admin), session: AsyncSession = Depends(get_session)) -> dict:
    reports = (await session.execute(select(CarnaticReport))).scalars().all()
    by_post: dict[int, list[str]] = {}
    by_comment: dict[int, list[str]] = {}
    for r in reports:
        target = by_post.setdefault(r.post_id, []) if r.post_id is not None else by_comment.setdefault(r.comment_id, [])
        target.append(r.reason)
    posts = (await session.execute(select(CarnaticPost).order_by(CarnaticPost.id.desc()).limit(100))).scalars().all()
    comments_ = (await session.execute(select(CarnaticComment).order_by(CarnaticComment.id.desc()).limit(100))).scalars().all()
    # Reported things first, however old: a report older than the 100 newest
    # must not fall off the list.
    seen_posts = {p.id for p in posts}
    posts = [*(await session.execute(select(CarnaticPost).where(CarnaticPost.id.in_(
        [i for i in by_post if i not in seen_posts] or [-1])))).scalars().all(), *posts]
    seen_comments = {c.id for c in comments_}
    comments_ = [*(await session.execute(select(CarnaticComment).where(CarnaticComment.id.in_(
        [i for i in by_comment if i not in seen_comments] or [-1])))).scalars().all(), *comments_]
    posts.sort(key=lambda p: (-len(by_post.get(p.id, [])), -p.id))
    comments_.sort(key=lambda c: (-len(by_comment.get(c.id, [])), -c.id))
    return {
        "posts": [{"id": p.id, "title": p.title, "url": p.url, "hidden": p.hidden, "createdAt": _iso(p.created_at),
                   "reports": len(by_post.get(p.id, [])), "reasons": [x for x in by_post.get(p.id, []) if x]}
                  for p in posts],
        "comments": [{"id": c.id, "postId": c.post_id, "body": c.body, "hidden": c.hidden, "createdAt": _iso(c.created_at),
                      "reports": len(by_comment.get(c.id, [])), "reasons": [x for x in by_comment.get(c.id, []) if x]}
                     for c in comments_],
        "reported": len(by_post) + len(by_comment),
    }


class HideIn(BaseModel):
    hidden: bool


@router.post("/admin/posts/{post_id}/hide")
async def admin_hide_post(post_id: int, body: HideIn, _: str = Depends(require_admin),
                          session: AsyncSession = Depends(get_session)) -> dict:
    p = await session.get(CarnaticPost, post_id)
    if p is None:
        raise HTTPException(404, "No such post.")
    p.hidden, p.hidden_by = body.hidden, "her" if body.hidden else ""
    await session.commit()
    return {"id": p.id, "hidden": p.hidden}


@router.post("/admin/comments/{comment_id}/hide")
async def admin_hide_comment(comment_id: int, body: HideIn, _: str = Depends(require_admin),
                             session: AsyncSession = Depends(get_session)) -> dict:
    c = await session.get(CarnaticComment, comment_id)
    if c is None:
        raise HTTPException(404, "No such comment.")
    c.hidden = body.hidden
    await session.commit()
    return {"id": c.id, "hidden": c.hidden}
