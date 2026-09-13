# SPDX-License-Identifier: AGPL-3.0-only
"""
Shruti's Guides — the catalogue people read from, and the desk authors write at.

⚠ **Route order.** Literal paths first (`/games`, `/mine`, `/draft`,
`/admin/…`, `/by-id/…`), the two-segment reader `/{game}/{slug}` last. This
file has been bitten by the opposite order before — a literal path declared
under a catch-all is read as the catch-all's argument and answers 422 about
integer parsing, which names nothing that would lead anybody here. Guides are
addressed by id under `/by-id/` rather than `/{id}/` so that a slug can never
be mistaken for a number or the other way round.

⚠ **A draft may be saved with problems; only a clean one may be submitted.**
An author saving work in progress must not be refused because a gate names a
step they have not written yet. Every save returns the validator's problems
beside the saved draft, so the editor can show them; submit is where they
have to be gone.

Votes, reports and blocks are the practice room's, by the same rules and at
the same threshold. A guide is other people's writing in front of readers and
the same things go wrong with it.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shrutisguides.format import validate as validate_guide

from shruti.api.deps import require_admin
import copy

from shruti.core import guide_diff
from shruti.api.routes.practice import (
    REPORTS_TO_HIDE, REPORT_REASONS as REASONS, _hidden_from, _name, _reader, _refuse_if_suspended,
)
from shruti.core.db import get_session
from shruti.models.accounts import User
from shruti.models.guides import Game, Guide, GuideReport, GuideVersion, GuideVote

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/guides", tags=["guides"])

SORTS = ("featured", "top", "new")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _problems(body: dict) -> list[dict]:
    return [{"path": p.path, "message": p.message} for p in validate_guide(body)]


# ── reading ──────────────────────────────────────────────────────────────────

async def _game_by_slug(session: AsyncSession, slug: str) -> Game | None:
    return (await session.execute(select(Game).where(Game.slug == slug))).scalars().first()


async def _votes_for(session: AsyncSession, guide_ids: list[int]) -> dict[int, int]:
    if not guide_ids:
        return {}
    rows = (await session.execute(
        select(GuideVote.guide_id, func.count().label("n"))
        .where(GuideVote.guide_id.in_(guide_ids))
        .group_by(GuideVote.guide_id)
    )).all()
    return {gid: n for gid, n in rows}


async def _voted_by(session: AsyncSession, viewer: User | None, guide_ids: list[int]) -> set[int]:
    if viewer is None or not guide_ids:
        return set()
    rows = (await session.execute(
        select(GuideVote.guide_id).where(
            GuideVote.user_id == viewer.id, GuideVote.guide_id.in_(guide_ids))
    )).scalars().all()
    return set(rows)


def _card(g: Guide, game: Game, author: User | None, version: GuideVersion | None,
          votes: int, voted: bool, viewer: User | None) -> dict:
    """What a listing shows about a guide — everything but the body."""
    body = version.body if version else {}
    meta = body.get("guide", {})
    return {
        "id": g.id,
        "slug": g.slug,
        "title": g.title,
        "game": {"id": game.id, "slug": game.slug, "name": game.name},
        "author": _name(author),
        "authorId": g.created_by,
        "version": meta.get("version", ""),
        "gamePatch": meta.get("game_patch", ""),
        "summary": meta.get("summary", ""),
        "licence": str(meta.get("licence") or ""),
        "phases": len(body.get("phases", [])),
        "steps": len(body.get("steps", [])),
        # The boards print "8 · ~30 h": the path's declared minutes, in hours.
        "hours": round(sum(int(s.get("minutes") or 0) for s in body.get("steps", [])
                           if isinstance(s, dict)) / 60),
        # Which publication this is — "new" on the landing page, then v2, v3.
        "number": version.number if version else None,
        "votes": votes,
        "voted": voted,
        "featured": g.featured,
        "mine": viewer is not None and viewer.id == g.created_by,
        "hidden": g.hidden,
        "hiddenBy": g.hidden_by,
        "publishedAt": version.published_at.isoformat() if version and version.published_at else None,
    }


@router.get("/games")
async def games(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Every game that has at least one published guide, with a count."""
    rows = (await session.execute(
        select(Game, func.count(Guide.id))
        .join(Guide, Guide.game_id == Game.id)
        .where(Guide.published_version_id.is_not(None), Guide.hidden.is_(False))
        .group_by(Game.id)
        .order_by(Game.name)
    )).all()
    return [{"id": g.id, "slug": g.slug, "name": g.name, "variants": g.variants,
             "guides": n} for g, n in rows]


@router.get("")
async def catalogue(
    request: Request,
    sort: str = "featured",
    game: str = "",
    limit: int = 30,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    Published guides. No account needed to read.

    `sort=featured` is the landing page: hers first, then most voted, then
    newest. `top` and `new` are the other two tabs.
    """
    from shruti.api.routes.accounts import current_user

    if sort not in SORTS:
        raise HTTPException(422, f"sort must be one of {', '.join(SORTS)}")
    viewer = await current_user(request, session)

    q = (
        select(Guide, Game, User, GuideVersion)
        .join(Game, Game.id == Guide.game_id)
        .join(User, User.id == Guide.created_by, isouter=True)
        .join(GuideVersion, GuideVersion.id == Guide.published_version_id)
        .where(Guide.published_version_id.is_not(None))
        .where(Guide.hidden.is_(False))
    )
    if game:
        q = q.where(Game.slug == game)
    # ⚠ Before the limit, as in the practice room: filtering after it would
    # hand somebody who has blocked people a shorter page with a gap in it.
    hidden = await _hidden_from(session, viewer)
    if hidden:
        q = q.where(Guide.created_by.not_in(hidden))

    votes_sub = (
        select(GuideVote.guide_id, func.count().label("n"))
        .group_by(GuideVote.guide_id).subquery()
    )
    q = q.join(votes_sub, votes_sub.c.guide_id == Guide.id, isouter=True)
    n = func.coalesce(votes_sub.c.n, 0)
    if sort == "featured":
        q = q.order_by(Guide.featured.desc(), Guide.featured_at.desc().nulls_last(),
                       n.desc(), GuideVersion.published_at.desc())
    elif sort == "top":
        q = q.order_by(n.desc(), GuideVersion.published_at.desc())
    else:
        q = q.order_by(GuideVersion.published_at.desc())

    rows = (await session.execute(q.limit(min(limit, 100)))).all()
    ids = [g.id for g, _, _, _ in rows]
    votes = await _votes_for(session, ids)
    voted = await _voted_by(session, viewer, ids)
    return [_card(g, game_, author, version, votes.get(g.id, 0), g.id in voted, viewer)
            for g, game_, author, version in rows]


@router.get("/mine")
async def mine(request: Request, session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The author's own guides, with the state of each version — drafts included."""
    user = await _reader(request, session)
    rows = (await session.execute(
        select(Guide, Game).join(Game, Game.id == Guide.game_id)
        .where(Guide.created_by == user.id).order_by(Guide.updated_at.desc())
    )).all()
    out = []
    for g, game in rows:
        versions = (await session.execute(
            select(GuideVersion).where(GuideVersion.guide_id == g.id, GuideVersion.contributed_by.is_(None))
            .order_by(GuideVersion.number.desc())
        )).scalars().all()
        out.append({
            "id": g.id, "slug": g.slug, "title": g.title,
            "game": {"slug": game.slug, "name": game.name},
            "published": g.published_version_id,
            "hidden": g.hidden, "hiddenBy": g.hidden_by,
            "versions": [{"id": v.id, "number": v.number, "state": v.state,
                          "note": v.note, "problems": len(_problems(v.body))}
                         for v in versions],
        })
    return out


# ── writing ──────────────────────────────────────────────────────────────────

@router.get("/mine/by-id/{version_id}")
async def my_version(
    version_id: int, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    One of the author's own versions, in full — what the desk opens.

    ⚠ Author or 404, never 403: a stranger learns nothing about whether the
    id exists. Any state is readable; only draft and sent_back are editable,
    and the desk reads `state` to know which it is.
    """
    user = await _reader(request, session)
    version = await session.get(GuideVersion, version_id)
    guide = await session.get(Guide, version.guide_id) if version else None
    if version is None or guide is None or not _may_open(user, guide, version):
        raise HTTPException(404, "no such draft")
    game = await session.get(Game, guide.game_id)
    contribution = None
    if version.contributed_by is not None:
        author = await session.get(User, guide.created_by)
        who = await session.get(User, version.contributed_by)
        contribution = {"by": _name(who), "byId": version.contributed_by, "author": _name(author),
                        "mine": version.contributed_by == user.id, "owner": guide.created_by == user.id,
                        "against": version.against_id, "accepted": version.accepted_at is not None}
    return {
        "id": version.id, "number": version.number, "state": version.state, "note": version.note,
        "editable": version.state in ("draft", "sent_back") and (version.contributed_by in (None, user.id) or version.accepted_at is not None),
        "guide": {"id": guide.id, "slug": guide.slug, "title": guide.title,
                  "published": guide.published_version_id,
                  "game": {"slug": game.slug, "name": game.name} if game else None},
        "contribution": contribution,
        "body": version.body,
        "problems": _problems(version.body),
    }


def _may_open(user: User, guide: Guide, version: GuideVersion) -> bool:
    """The author, or the person whose contribution it is. Nobody else, and 404 either way."""
    return guide.created_by == user.id or version.contributed_by == user.id


def _may_edit(user: User, guide: Guide, version: GuideVersion) -> bool:
    """
    A contribution is edited by its contributor until it is accepted; once
    accepted it is the author's draft. The author never edits somebody's
    open proposal — they accept it or decline it with a note.
    """
    if version.contributed_by is None or version.accepted_at is not None:
        return guide.created_by == user.id
    return version.contributed_by == user.id


SOURCES = ("desk", "agent", "file")


class DraftIn(BaseModel):
    # ⚠ Absent means "make a new guide"; present means "this draft".
    version_id: int | None = None
    body: dict
    # Which tool is saving: desk | agent | file. Anything else is the desk.
    source: str = "desk"


async def _open_draft(session: AsyncSession, guide_id: int) -> GuideVersion | None:
    """The one version an author may still edit, if there is one."""
    return (await session.execute(
        select(GuideVersion).where(
            GuideVersion.guide_id == guide_id,
            GuideVersion.state.in_(("draft", "sent_back")),
            (GuideVersion.contributed_by.is_(None)) | (GuideVersion.accepted_at.is_not(None)),
        ).order_by(GuideVersion.number.desc())
    )).scalars().first()


@router.put("/draft")
async def save_draft(
    body: DraftIn, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep what an author is writing.

    ⚠ Saved even with problems. The validator's answer comes back beside the
    draft so the editor can show it, but an author must not be refused for a
    gate that names a step they have not written yet. Submit is the gate.
    """
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    doc = body.body
    problems = _problems(doc)

    # Enough shape to file it, even if the rest is unfinished.
    meta = doc.get("guide") if isinstance(doc.get("guide"), dict) else {}
    game_meta = doc.get("game") if isinstance(doc.get("game"), dict) else {}
    slug = str(meta.get("id", "")).strip()
    title = str(meta.get("title", "")).strip()
    game_slug = str(game_meta.get("id", "")).strip()
    if not (_SLUG.match(slug) and title and _SLUG.match(game_slug)):
        raise HTTPException(
            422, "a draft needs at least guide.id, guide.title and game.id to be filed under")

    game = await _game_by_slug(session, game_slug)
    if game is None:
        game = Game(slug=game_slug, name=str(game_meta.get("name") or game_slug),
                    variants=game_meta.get("variants") or [])
        session.add(game)
        await session.flush()
    elif game_meta.get("variants"):
        game.variants = game_meta["variants"]

    if body.version_id is None:
        guide = (await session.execute(
            select(Guide).where(Guide.game_id == game.id, Guide.slug == slug)
        )).scalars().first()
        if guide is not None and guide.created_by != user.id:
            raise HTTPException(409, "somebody else already has a guide at that address for this game")
        if guide is None:
            guide = Guide(game_id=game.id, slug=slug, title=title, created_by=user.id)
            session.add(guide)
            await session.flush()
        version = await _open_draft(session, guide.id)
        if version is None:
            last = (await session.execute(
                select(func.max(GuideVersion.number)).where(GuideVersion.guide_id == guide.id)
            )).scalar() or 0
            version = GuideVersion(guide_id=guide.id, number=last + 1, created_by=user.id)
            session.add(version)
    else:
        version = await session.get(GuideVersion, body.version_id)
        if version is None:
            raise HTTPException(404, "no such draft")
        guide = await session.get(Guide, version.guide_id)
        if guide is None or not _may_open(user, guide, version):
            raise HTTPException(404, "no such draft")
        if not _may_edit(user, guide, version):
            raise HTTPException(409, "that version is somebody's proposal; accept it or decline it with a note")
        if version.state not in ("draft", "sent_back"):
            raise HTTPException(409, f"that version is {version.state} and cannot be edited")

    version.body = doc
    version.state = "draft"
    version.source = body.source if body.source in SOURCES else "desk"
    if version.contributed_by is None or version.accepted_at is not None:
        guide.title = title           # a proposal does not rename the guide; accepting it may
    await session.commit()
    return {"ok": True, "guideId": guide.id, "versionId": version.id,
            "number": version.number, "problems": problems}


@router.post("/by-id/{version_id}/submit")
async def submit(
    version_id: int, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """Put a draft in her queue. Only a clean one; the problems are the answer otherwise."""
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    version = await session.get(GuideVersion, version_id)
    guide = await session.get(Guide, version.guide_id) if version else None
    if version is None or guide is None or not _may_open(user, guide, version):
        raise HTTPException(404, "no such draft")
    if not _may_edit(user, guide, version):
        raise HTTPException(409, "that version is somebody's proposal")
    if version.state not in ("draft", "sent_back"):
        raise HTTPException(409, f"that version is {version.state}")
    problems = _problems(version.body)
    if problems:
        return JSONResponse(status_code=422, content={
            "ok": False, "problems": problems,
            "detail": f"{len(problems)} thing(s) to fix before it can be submitted"})
    # ⚠ A contribution is proposed to the guide's author; only the author's
    # own version goes into her queue. Nothing anybody proposes publishes.
    proposal = version.contributed_by is not None and version.accepted_at is None
    version.state = "proposed" if proposal else "submitted"
    version.submitted_at = _now()
    await session.commit()
    return {"ok": True, "versionId": version.id, "state": version.state}


# ── forks and contributions ──────────────────────────────────────────────────

# The licences under which somebody may take a guide and make it their own.
FORKABLE = ("CC-BY-SA-4.0", "CC-BY-4.0", "CC0-1.0")


def _forkable(version: GuideVersion | None) -> bool:
    meta = (version.body if version else {}).get("guide", {})
    return str(meta.get("licence") or "") in FORKABLE


async def _published(session: AsyncSession, guide_id: int) -> tuple[Guide, GuideVersion]:
    guide = await session.get(Guide, guide_id)
    version = await session.get(GuideVersion, guide.published_version_id) if guide and guide.published_version_id else None
    if guide is None or version is None or guide.hidden:
        raise HTTPException(404, "no such guide")
    return guide, version


@router.post("/by-id/{guide_id}/fork", status_code=201)
async def fork(guide_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    A copy of a published guide, under the forker's name, remembering where
    it came from. Only under a licence that allows it: CC BY-SA, CC BY or
    CC0. The original authors stay in the credits; the forker is added.
    """
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    guide, version = await _published(session, guide_id)
    if not _forkable(version):
        raise HTTPException(409, "this guide's licence does not allow forks")
    game = await session.get(Game, guide.game_id)
    base = f"{guide.slug}-{_slugify(_name(user))}"[:150] or f"{guide.slug}-fork"
    slug, n = base, 2
    while (await session.execute(select(Guide).where(Guide.game_id == game.id, Guide.slug == slug))).scalars().first() is not None:
        slug, n = f"{base}-{n}", n + 1
    body = copy.deepcopy(version.body)
    meta = body.setdefault("guide", {})
    meta["id"] = slug
    authors = [a for a in (meta.get("authors") or []) if isinstance(a, str)]
    if _name(user) not in authors:
        authors.append(_name(user))
    meta["authors"] = authors
    meta["version"] = "1"
    new = Guide(game_id=game.id, slug=slug, title=guide.title, created_by=user.id, forked_from_id=guide.id)
    session.add(new)
    await session.flush()
    draft = GuideVersion(guide_id=new.id, number=1, body=body, created_by=user.id, source="desk")
    session.add(draft)
    await session.commit()
    await session.refresh(draft)
    return {"ok": True, "guideId": new.id, "versionId": draft.id, "slug": slug}


def _slugify(text: str) -> str:
    out = "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out[:40]


@router.post("/by-id/{guide_id}/contribute", status_code=201)
async def contribute(guide_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Suggest a change: a copy of the published version to edit, which goes to
    the guide's author as a proposal — a difference against what is
    published, never a silent edit. One open proposal per person per guide.
    """
    user = await _reader(request, session)
    await _refuse_if_suspended(session, user)
    guide, version = await _published(session, guide_id)
    if guide.created_by == user.id:
        raise HTTPException(409, "it is your own guide: start a new version instead")
    existing = (await session.execute(
        select(GuideVersion).where(GuideVersion.guide_id == guide.id, GuideVersion.contributed_by == user.id,
                                   GuideVersion.state.in_(("draft", "proposed")))
    )).scalars().first()
    if existing is not None:
        return {"ok": True, "versionId": existing.id, "state": existing.state, "existing": True}
    last = (await session.execute(select(func.max(GuideVersion.number)).where(GuideVersion.guide_id == guide.id))).scalar() or 0
    draft = GuideVersion(guide_id=guide.id, number=last + 1, body=copy.deepcopy(version.body), created_by=user.id,
                         source="desk", contributed_by=user.id, against_id=version.id)
    session.add(draft)
    await session.commit()
    await session.refresh(draft)
    return {"ok": True, "versionId": draft.id, "state": draft.state, "existing": False}


@router.get("/mine/contributions")
async def contributions(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """The proposals this person made, and the ones made to their guides."""
    user = await _reader(request, session)

    async def shape(v: GuideVersion) -> dict:
        guide = await session.get(Guide, v.guide_id)
        game = await session.get(Game, guide.game_id) if guide else None
        who = await session.get(User, v.contributed_by) if v.contributed_by else None
        author = await session.get(User, guide.created_by) if guide else None
        against = await session.get(GuideVersion, v.against_id) if v.against_id else None
        return {"id": v.id, "state": v.state, "note": v.note, "accepted": v.accepted_at is not None,
                "by": _name(who), "byId": v.contributed_by, "author": _name(author),
                "guide": {"id": guide.id, "slug": guide.slug, "title": guide.title,
                          "game": {"slug": game.slug, "name": game.name} if game else None} if guide else None,
                "changes": guide_diff.summary(guide_diff.changes(against.body if against else {}, v.body)),
                "problems": len(_problems(v.body)),
                "updatedAt": v.updated_at.isoformat() if v.updated_at else None}

    given = (await session.execute(
        select(GuideVersion).where(GuideVersion.contributed_by == user.id).order_by(GuideVersion.updated_at.desc())
    )).scalars().all()
    received = (await session.execute(
        select(GuideVersion).join(Guide, Guide.id == GuideVersion.guide_id)
        .where(Guide.created_by == user.id, GuideVersion.contributed_by.is_not(None), GuideVersion.contributed_by != user.id,
               GuideVersion.state.in_(("proposed", "declined")) | GuideVersion.accepted_at.is_not(None))
        .order_by(GuideVersion.updated_at.desc())
    )).scalars().all()
    return {"given": [await shape(v) for v in given], "received": [await shape(v) for v in received]}


@router.get("/mine/by-id/{version_id}/changes")
async def version_changes(version_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """What a proposal changes against the version it was written against."""
    user = await _reader(request, session)
    version = await session.get(GuideVersion, version_id)
    guide = await session.get(Guide, version.guide_id) if version else None
    if version is None or guide is None or not _may_open(user, guide, version):
        raise HTTPException(404, "no such draft")
    against = await session.get(GuideVersion, version.against_id) if version.against_id else None
    if against is None and guide.published_version_id:
        against = await session.get(GuideVersion, guide.published_version_id)
    items = guide_diff.changes(against.body if against else {}, version.body)
    who = await session.get(User, version.contributed_by) if version.contributed_by else None
    return {"id": version.id, "state": version.state, "note": version.note, "by": _name(who),
            "owner": guide.created_by == user.id, "mine": version.contributed_by == user.id,
            "accepted": version.accepted_at is not None,
            "guide": {"id": guide.id, "slug": guide.slug, "title": guide.title},
            "against": {"id": against.id, "number": against.number} if against else None,
            "changes": items, "summary": guide_diff.summary(items)}


@router.post("/mine/by-id/{version_id}/accept")
async def accept_contribution(version_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    The author takes a proposal: it becomes their open draft, credited to
    the contributor, and goes to her queue when the author submits it.
    Nothing is published by accepting.
    """
    user = await _reader(request, session)
    version = await session.get(GuideVersion, version_id)
    guide = await session.get(Guide, version.guide_id) if version else None
    if version is None or guide is None or guide.created_by != user.id or version.contributed_by is None:
        raise HTTPException(404, "no such proposal")
    if version.state != "proposed":
        raise HTTPException(409, f"that proposal is {version.state}")
    if await _open_draft(session, guide.id) is not None:
        raise HTTPException(409, "you have an open draft of this guide; submit or discard it first")
    version.accepted_at = _now()
    version.state = "draft"
    version.note = ""
    await session.commit()
    return {"ok": True, "versionId": version.id, "state": version.state}


class DeclineIn(BaseModel):
    note: str = Field(min_length=1, max_length=1000)


@router.post("/mine/by-id/{version_id}/decline")
async def decline_contribution(version_id: int, body: DeclineIn, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Declined, with a note — a bare "no" is the practice room's lesson again."""
    user = await _reader(request, session)
    version = await session.get(GuideVersion, version_id)
    guide = await session.get(Guide, version.guide_id) if version else None
    if version is None or guide is None or guide.created_by != user.id or version.contributed_by is None:
        raise HTTPException(404, "no such proposal")
    if version.state != "proposed":
        raise HTTPException(409, f"that proposal is {version.state}")
    version.state = "declined"
    version.note = body.note.strip()
    await session.commit()
    return {"ok": True, "versionId": version.id, "state": version.state}


@router.post("/by-id/{guide_id}/vote")
async def vote(guide_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    user = await _reader(request, session)
    guide = await session.get(Guide, guide_id)
    if guide is None or guide.published_version_id is None or guide.hidden:
        raise HTTPException(404, "no such guide")
    existing = (await session.execute(
        select(GuideVote).where(GuideVote.guide_id == guide_id, GuideVote.user_id == user.id)
    )).scalars().first()
    if existing is not None:
        await session.delete(existing)
        voted = False
    else:
        session.add(GuideVote(guide_id=guide_id, user_id=user.id))
        voted = True
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        voted = True
    votes = (await _votes_for(session, [guide_id])).get(guide_id, 0)
    return {"ok": True, "voted": voted, "votes": votes}


class ReportIn(BaseModel):
    reason: str = "other"
    detail: str = Field(default="", max_length=1000)


@router.post("/by-id/{guide_id}/report", status_code=201)
async def report(
    guide_id: int, body: ReportIn, request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    ⚠ The same words whether it was the first report or the fourth, and
    whether or not it hid anything — the practice room's rule, for the
    practice room's reasons.
    """
    user = await _reader(request, session)
    guide = await session.get(Guide, guide_id)
    if guide is None or guide.published_version_id is None:
        raise HTTPException(404, "no such guide")
    # ⚠ A flat list of strings, not (value, label) pairs — the first draft
    # unpacked pairs and would have crashed on the first report.
    reason = body.reason if body.reason in REASONS else "other"
    session.add(GuideReport(guide_id=guide_id, user_id=user.id, reason=reason,
                            detail=body.detail.strip()))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return {"ok": True}
    total = (await session.execute(
        select(func.count()).select_from(GuideReport)
        .where(GuideReport.guide_id == guide_id, GuideReport.reviewed_at.is_(None))
    )).scalar_one()
    if total >= REPORTS_TO_HIDE and not guide.hidden:
        guide.hidden = True
        guide.hidden_by = "reports"
        await session.commit()
    return {"ok": True}


@router.post("/by-id/{guide_id}/withdraw")
async def withdraw(guide_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """An author taking their own guide down. Not a moderation event."""
    user = await _reader(request, session)
    guide = await session.get(Guide, guide_id)
    if guide is None or guide.created_by != user.id:
        raise HTTPException(404, "no such guide")
    guide.hidden = True
    guide.hidden_by = "author"
    await session.commit()
    return {"ok": True}


# ── her desk ─────────────────────────────────────────────────────────────────

@router.get("/admin/queue", dependencies=[Depends(require_admin)])
async def queue(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Drafts waiting to be read, oldest first — the one that has waited longest is on top."""
    rows = (await session.execute(
        select(GuideVersion, Guide, Game, User)
        .join(Guide, Guide.id == GuideVersion.guide_id)
        .join(Game, Game.id == Guide.game_id)
        .join(User, User.id == GuideVersion.created_by, isouter=True)
        .where(GuideVersion.state == "submitted")
        .order_by(GuideVersion.submitted_at)
    )).all()
    live_ids = [g.published_version_id for _, g, _, _ in rows if g.published_version_id]
    live = {lv.id: lv.number for lv in (await session.execute(
        select(GuideVersion).where(GuideVersion.id.in_(live_ids)))).scalars().all()} if live_ids else {}
    return [{
        "versionId": v.id, "number": v.number, "guideId": g.id, "title": g.title,
        "game": game.name, "author": _name(u), "submittedAt": v.submitted_at.isoformat() if v.submitted_at else None,
        "isUpdate": g.published_version_id is not None,
        # "v4 against v3": the number of the version that is live, if any.
        "against": live.get(g.published_version_id) if g.published_version_id else None,
        "steps": len(v.body.get("steps", [])),
        "phases": len(v.body.get("phases", [])),
        "source": v.source,
    } for v, g, game, u in rows]


@router.get("/admin/by-id/{version_id}", dependencies=[Depends(require_admin)])
async def read_version(version_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    """A version in full, with what is currently published beside it for the diff."""
    v = await session.get(GuideVersion, version_id)
    if v is None:
        raise HTTPException(404, "no such version")
    g = await session.get(Guide, v.guide_id)
    live = await session.get(GuideVersion, g.published_version_id) if g and g.published_version_id else None
    return {"version": {"id": v.id, "number": v.number, "state": v.state, "note": v.note, "body": v.body},
            "published": {"id": live.id, "number": live.number, "body": live.body} if live else None,
            "problems": _problems(v.body)}


@router.post("/admin/by-id/{version_id}/publish", dependencies=[Depends(require_admin)])
async def publish(version_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Make a version the one that is served.

    ⚠ Refuses a version with problems even from her — a published guide that
    fails its own validator is a guide the tracker cannot run.
    """
    v = await session.get(GuideVersion, version_id)
    if v is None or v.state not in ("submitted", "draft", "sent_back"):
        raise HTTPException(404, "no such version to publish")
    problems = _problems(v.body)
    if problems:
        return JSONResponse(status_code=422, content={"ok": False, "problems": problems})
    g = await session.get(Guide, v.guide_id)
    was_update = bool(g.published_version_id) and g.published_version_id != v.id
    if was_update:
        old = await session.get(GuideVersion, g.published_version_id)
        if old is not None:
            old.state = "superseded"
    v.state = "published"
    v.published_at = _now()
    g.published_version_id = v.id
    g.title = str(v.body.get("guide", {}).get("title") or g.title)
    # ⚠ A guide hidden by reports comes back when she publishes it herself:
    # publishing IS her looking at it, which is what the reports were waiting
    # for. A guide the author withdrew stays withdrawn.
    if g.hidden and g.hidden_by == "reports":
        g.hidden, g.hidden_by = False, ""
    await session.commit()
    game = await session.get(Game, g.game_id)
    author = await session.get(User, g.created_by)
    await _tell_discord({
        "id": g.id, "slug": g.slug, "title": g.title,
        "game": game.name if game else "", "gameSlug": game.slug if game else "",
        "author": _name(author),
        "steps": len(v.body.get("steps", [])), "phases": len(v.body.get("phases", [])),
        "summary": str(v.body.get("guide", {}).get("summary") or ""),
        "isUpdate": was_update,
    })
    return {"ok": True, "guideId": g.id, "versionId": v.id}


async def _tell_discord(guide: dict) -> None:
    """
    Let the channel know a guide went up, if there is one.

    The bot owns every fact about Discord; this says only that something was
    published, to an endpoint that refuses anybody without the shared secret.
    Built field by field so nothing about a reader ever reaches the bot.
    ⚠ After the commit, never before: a Discord outage must not fail her
    publish — the guide is up, and the channel can catch up.
    """
    import os

    import httpx

    bot = os.environ.get("VCORDBOT_INTERNAL_URL", "").strip()
    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    if not (bot and secret):
        return                      # no bridge configured; a working state
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(f"{bot}/internal/guides", json=guide,
                              headers={"X-Shruti-Internal": secret})
    except Exception as exc:                       # noqa: BLE001
        log.warning("guides channel not told: %s", type(exc).__name__)


class SendBackIn(BaseModel):
    note: str = Field(max_length=2000)


@router.post("/admin/by-id/{version_id}/send-back", dependencies=[Depends(require_admin)])
async def send_back(version_id: int, body: SendBackIn, session: AsyncSession = Depends(get_session)) -> dict:
    """Back to the author with a reason. ⚠ A reason, always — 'rejected' alone is the room's lesson."""
    v = await session.get(GuideVersion, version_id)
    if v is None or v.state != "submitted":
        raise HTTPException(404, "no such submitted version")
    if not body.note.strip():
        raise HTTPException(422, "say why, in a sentence — the author cannot fix a silence")
    v.state = "sent_back"
    v.note = body.note.strip()
    await session.commit()
    return {"ok": True}


class FeatureIn(BaseModel):
    featured: bool


@router.post("/admin/by-id/{guide_id}/feature", dependencies=[Depends(require_admin)])
async def feature(guide_id: int, body: FeatureIn, session: AsyncSession = Depends(get_session)) -> dict:
    g = await session.get(Guide, guide_id)
    if g is None:
        raise HTTPException(404, "no such guide")
    g.featured = body.featured
    g.featured_at = _now() if body.featured else None
    await session.commit()
    return {"ok": True, "featured": g.featured}


class HideIn(BaseModel):
    hidden: bool


@router.post("/admin/by-id/{guide_id}/hide", dependencies=[Depends(require_admin)])
async def hide(guide_id: int, body: HideIn, session: AsyncSession = Depends(get_session)) -> dict:
    g = await session.get(Guide, guide_id)
    if g is None:
        raise HTTPException(404, "no such guide")
    g.hidden = body.hidden
    g.hidden_by = "her" if body.hidden else ""
    # ⚠ Her decision settles the open reports EITHER way. Keeping it down
    # without reviewing them left them open for ever — still counting, still
    # listed as waiting for a look she had already given.
    for r in (await session.execute(
        select(GuideReport).where(GuideReport.guide_id == guide_id, GuideReport.reviewed_at.is_(None))
    )).scalars().all():
        r.reviewed_at, r.outcome = _now(), ("upheld" if body.hidden else "dismissed")
    await session.commit()
    return {"ok": True, "hidden": g.hidden}


@router.get("/admin/guides", dependencies=[Depends(require_admin)])
async def admin_guides(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    Every guide, hers to feature, hide or put back — with what is open against
    it. Reports are grouped by the guide, never one row per report: three
    people reporting one guide is ONE decision.
    """
    rows = (await session.execute(
        select(Guide, Game, User)
        .join(Game, Game.id == Guide.game_id)
        .join(User, User.id == Guide.created_by, isouter=True)
        .order_by(Guide.featured.desc(), Guide.updated_at.desc())
    )).all()
    ids = [g.id for g, _, _ in rows]
    votes = await _votes_for(session, ids)
    open_reports = (await session.execute(
        select(GuideReport).where(GuideReport.guide_id.in_(ids), GuideReport.reviewed_at.is_(None))
    )).scalars().all() if ids else []
    by_guide: dict[int, list[GuideReport]] = {}
    for r in open_reports:
        by_guide.setdefault(r.guide_id, []).append(r)
    out = []
    for g, game, u in rows:
        reps = by_guide.get(g.id, [])
        reasons: dict[str, int] = {}
        for r in reps:
            reasons[r.reason] = reasons.get(r.reason, 0) + 1
        out.append({
            "id": g.id, "slug": g.slug, "title": g.title,
            "game": {"slug": game.slug, "name": game.name},
            "author": _name(u), "authorId": g.created_by,
            "published": g.published_version_id is not None,
            "featured": g.featured, "hidden": g.hidden, "hiddenBy": g.hidden_by,
            "votes": votes.get(g.id, 0),
            "reports": {"open": len(reps), "reasons": reasons,
                        "details": [r.detail for r in reps if r.detail]},
            "updatedAt": g.updated_at.isoformat() if g.updated_at else None,
        })
    return out


# ── an author's page (board W10) ─────────────────────────────────────────────

@router.get("/by/{user_id}")
async def by_author(user_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    What an author has published: each guide with its licence, its state and
    its votes. Drafts stay private; a hidden guide shows as hidden only to
    its author. The name is the same one the catalogue prints.
    """
    author = await session.get(User, user_id)
    if author is None:
        raise HTTPException(404, "no such author")
    from shruti.api.routes.accounts import current_user
    viewer = await current_user(request, session)
    own = viewer is not None and viewer.id == user_id
    rows = (await session.execute(
        select(Guide, Game).join(Game, Game.id == Guide.game_id).where(Guide.created_by == user_id).order_by(Guide.updated_at.desc())
    )).all()
    ids = [g.id for g, _ in rows]
    votes = dict((await session.execute(
        select(GuideVote.guide_id, func.count()).where(GuideVote.guide_id.in_(ids)).group_by(GuideVote.guide_id)
    )).all()) if ids else {}
    pending = set((await session.execute(
        select(GuideVersion.guide_id).where(GuideVersion.guide_id.in_(ids), GuideVersion.state == "submitted")
    )).scalars().all()) if ids else set()
    guides = []
    for g, game in rows:
        version = await session.get(GuideVersion, g.published_version_id) if g.published_version_id else None
        if version is None and g.id not in pending:
            continue                      # a draft nobody has submitted is nobody's business
        if g.hidden and not own:
            continue
        meta = (version.body if version else {}).get("guide", {})
        status = "hidden" if g.hidden else ("published" if version else "in review")
        if version and g.id in pending:
            status = "update in review"
        guides.append({"id": g.id, "slug": g.slug, "title": g.title, "game": {"slug": game.slug, "name": game.name},
                       "licence": str(meta.get("licence") or ""), "status": status, "votes": int(votes.get(g.id, 0))})
    contributed = (await session.execute(
        select(func.count()).select_from(GuideVersion).where(GuideVersion.contributed_by == user_id, GuideVersion.accepted_at.is_not(None))
    )).scalar_one()
    return {
        "id": author.id, "name": _name(author), "own": own, "contributed": int(contributed),
        "published": sum(1 for g in guides if g["status"] in ("published", "update in review")),
        "votes": sum(g["votes"] for g in guides),
        "guides": guides,
    }


# ── the reader, and the pack ─────────────────────────────────────────────────

@router.get("/by-id/{guide_id}/download")
async def download(guide_id: int, session: AsyncSession = Depends(get_session)):
    """
    The published document, as a file — the pack model. A self-hosted
    instance pulls guides this way, and a person can keep a copy.
    """
    g = await session.get(Guide, guide_id)
    if g is None or g.published_version_id is None or g.hidden:
        raise HTTPException(404, "no such guide")
    v = await session.get(GuideVersion, g.published_version_id)
    return JSONResponse(
        content=v.body,
        headers={"Content-Disposition": f'attachment; filename="{g.slug}.guide.json"'},
    )


@router.get("/{game}/{slug}")
async def one(
    game: str, slug: str, request: Request, session: AsyncSession = Depends(get_session),
) -> dict:
    """
    A published guide, in full, with what a reader needs around it.

    ⚠ Hidden is 404 for everybody EXCEPT its author, who gets it with the
    reason — the practice room's rule, for the same reason: they wrote it, they
    still have it, and they are the one person who needs to know what happened.
    """
    from shruti.api.routes.accounts import current_user

    viewer = await current_user(request, session)
    game_row = await _game_by_slug(session, game)
    if game_row is None:
        raise HTTPException(404, "no such guide")
    g = (await session.execute(
        select(Guide).where(Guide.game_id == game_row.id, Guide.slug == slug)
    )).scalars().first()
    mine_ = viewer is not None and g is not None and viewer.id == g.created_by
    if g is None or (g.published_version_id is None and not mine_) or (g.hidden and not mine_):
        raise HTTPException(404, "no such guide")
    hidden = await _hidden_from(session, viewer)
    if g.created_by in hidden:
        raise HTTPException(404, "no such guide")

    v = await session.get(GuideVersion, g.published_version_id) if g.published_version_id else None
    if v is None:
        v = await _open_draft(session, g.id)          # the author, before publishing
    author = await session.get(User, g.created_by)
    votes = (await _votes_for(session, [g.id])).get(g.id, 0)
    voted = g.id in await _voted_by(session, viewer, [g.id])
    out = _card(g, game_row, author, v, votes, voted, viewer)
    out["body"] = v.body if v else {}
    # Forks and credits: whether the licence allows a fork, where a fork came
    # from, and who contributed the published version, if somebody did.
    out["forkable"] = _forkable(v)
    out["forkedFrom"] = None
    if g.forked_from_id:
        origin = await session.get(Guide, g.forked_from_id)
        origin_game = await session.get(Game, origin.game_id) if origin else None
        if origin is not None and origin_game is not None and origin.published_version_id and not origin.hidden:
            out["forkedFrom"] = {"title": origin.title, "game": origin_game.slug, "slug": origin.slug}
    contributor = await session.get(User, v.contributed_by) if v is not None and v.contributed_by else None
    out["contributor"] = _name(contributor) if contributor is not None and v.accepted_at is not None else ""
    return out
