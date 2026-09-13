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
        "phases": len(body.get("phases", [])),
        "steps": len(body.get("steps", [])),
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
            select(GuideVersion).where(GuideVersion.guide_id == g.id)
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

class DraftIn(BaseModel):
    # ⚠ Absent means "make a new guide"; present means "this draft".
    version_id: int | None = None
    body: dict


async def _open_draft(session: AsyncSession, guide_id: int) -> GuideVersion | None:
    """The one version an author may still edit, if there is one."""
    return (await session.execute(
        select(GuideVersion).where(
            GuideVersion.guide_id == guide_id,
            GuideVersion.state.in_(("draft", "sent_back")),
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
        if guide is None or guide.created_by != user.id:
            raise HTTPException(404, "no such draft")
        if version.state not in ("draft", "sent_back"):
            raise HTTPException(409, f"that version is {version.state} and cannot be edited")

    version.body = doc
    version.state = "draft"
    guide.title = title
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
    if version is None or guide is None or guide.created_by != user.id:
        raise HTTPException(404, "no such draft")
    if version.state not in ("draft", "sent_back"):
        raise HTTPException(409, f"that version is {version.state}")
    problems = _problems(version.body)
    if problems:
        return JSONResponse(status_code=422, content={
            "ok": False, "problems": problems,
            "detail": f"{len(problems)} thing(s) to fix before it can be submitted"})
    version.state = "submitted"
    version.submitted_at = _now()
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
    return [{
        "versionId": v.id, "number": v.number, "guideId": g.id, "title": g.title,
        "game": game.name, "author": _name(u), "submittedAt": v.submitted_at.isoformat() if v.submitted_at else None,
        "isUpdate": g.published_version_id is not None,
        "steps": len(v.body.get("steps", [])),
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
    if g.published_version_id and g.published_version_id != v.id:
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
    return {"ok": True, "guideId": g.id, "versionId": v.id}


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
    if not body.hidden:
        # Her decision settles the open reports.
        for r in (await session.execute(
            select(GuideReport).where(GuideReport.guide_id == guide_id, GuideReport.reviewed_at.is_(None))
        )).scalars().all():
            r.reviewed_at, r.outcome = _now(), "dismissed"
    await session.commit()
    return {"ok": True, "hidden": g.hidden}


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
    return out
