"""
Editable page content.

Astro fetches these server-side on each render, so an edit in the admin is live
immediately — no rebuild, no deploy. That is the whole point: the site can ship
before the art exists, and you unhide blocks from Athens as they arrive.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.db import get_session
from shruti.models import Credit, Media, ProfileField, Project, Section, SocialLink

router = APIRouter(prefix="/api/content", tags=["content"])


def _media_payload(m: Media | None) -> dict | None:
    if m is None:
        return None
    return {
        "url": f"/media/{m.filename}",
        "alt": m.alt_text,
        "width": m.width,
        "height": m.height,
        "credit": m.credit,
        "creditUrl": m.credit_url,
    }


@router.get("/page/{page}")
async def get_page(page: str, session: AsyncSession = Depends(get_session)) -> dict:
    """Visible sections for one page, in order, with their art resolved."""
    rows = (
        await session.execute(
            select(Section, Media)
            .join(Media, Section.media_id == Media.id, isouter=True)
            .where(Section.page == page, Section.visible.is_(True))
            .order_by(Section.position)
        )
    ).all()

    return {
        "page": page,
        "sections": [
            {
                "key": s.key,
                "kind": s.kind,
                "eyebrow": s.eyebrow,
                "title": s.title,
                "bodyMd": s.body_md,
                "linkUrl": s.link_url,
                "linkLabel": s.link_label,
                "media": _media_payload(m),
            }
            for s, m in rows
        ],
    }


@router.get("/profile")
async def get_profile(session: AsyncSession = Depends(get_session)) -> dict:
    """The §03 field vocabulary plus credits — the agency-tier About block."""
    fields = (
        await session.execute(
            select(ProfileField)
            .where(ProfileField.visible.is_(True))
            .order_by(ProfileField.position)
        )
    ).scalars().all()

    credits = (
        await session.execute(
            select(Credit).where(Credit.visible.is_(True)).order_by(Credit.position)
        )
    ).scalars().all()

    return {
        "fields": [{"label": f.label, "value": f.value} for f in fields],
        "credits": [{"role": c.role, "name": c.name, "url": c.url} for c in credits],
    }


@router.get("/links")
async def get_links(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(
            select(SocialLink).where(SocialLink.visible.is_(True)).order_by(SocialLink.position)
        )
    ).scalars().all()
    return [{"platform": r.platform, "url": r.url, "label": r.label} for r in rows]


@router.get("/projects")
async def get_projects(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The /work surface — the niche-specific page (plan §04)."""
    rows = (
        await session.execute(
            select(Project, Media)
            .join(Media, Project.media_id == Media.id, isouter=True)
            .where(Project.visible.is_(True))
            .order_by(Project.position)
        )
    ).all()
    return [
        {
            "slug": p.slug,
            "name": p.name,
            "tagline": p.tagline,
            "bodyMd": p.body_md,
            "repoUrl": p.repo_url,
            "siteUrl": p.site_url,
            "status": p.status,
            "media": _media_payload(m),
        }
        for p, m in rows
    ]
