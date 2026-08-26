"""
Editable page content.

Astro fetches these server-side on each render, so an edit in the admin is live
immediately — no rebuild, no deploy. That is the whole point: the site can ship
before the art exists, and you unhide blocks from Athens as they arrive.
"""

from __future__ import annotations

import re
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.core.db import get_session
from shruti.models import (
    Credit, FanArt, Media, Outfit, ProfileField, Project, Section, SocialLink,
    Sponsor,
)

router = APIRouter(prefix="/api/content", tags=["content"])


def _media_payload(m: Media | None) -> dict | None:
    if m is None:
        return None
    from shruti.core.storage import public_url

    return {
        # Resolved per row: a file stored locally before R2 was configured must
        # keep pointing at /media/*, not at a bucket it was never put in.
        "url": public_url(m.filename, m.storage_backend),
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


# Render order for the typed link taxonomy. Anything unrecognised sorts last
# rather than vanishing.
_LINK_GROUPS = ("channels", "socials", "supports", "code")


@router.get("/links")
async def get_links(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Links grouped by category, not one flat list.

    Channels / Socials / Supports / Code. The Supports group is where GitHub
    Sponsors and a hosted Theourgia tier live — a distinction a typical VTuber
    links block has no use for, and the reason this is grouped at all.
    """
    rows = (
        await session.execute(
            select(SocialLink).where(SocialLink.visible.is_(True)).order_by(SocialLink.position)
        )
    ).scalars().all()

    grouped: dict[str, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r.category, []).append(
            {"platform": r.platform, "url": r.url, "label": r.label}
        )

    ordered = {g: grouped[g] for g in _LINK_GROUPS if g in grouped}
    ordered.update({g: v for g, v in grouped.items() if g not in _LINK_GROUPS})
    return {"groups": ordered}


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
            "role": p.role,
            "stack": p.stack,
            "licence": p.licence,
            "contributors": p.contributors,
            "featured": p.featured,
            "media": _media_payload(m),
        }
        for p, m in rows
    ]


# At most three on the landing page. The cap lives here rather than in the
# database, so a fourth sponsor is a decision she makes and not an error she
# hits — she can tick a fourth and see the first three win, which is the
# behaviour the admin's help text promises.
FEATURED_SPONSORS = 3

# A colour arriving from the admin is written into a style attribute, so it is
# checked rather than trusted: anything that is not exactly #RRGGBB is dropped
# and the card falls back to the site's own surface. Not a security fix on its
# own — the value is escaped anyway — but a typo should look like a plain card,
# not like a broken one.
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _sponsor_payload(s: Sponsor, light: Media | None, dark: Media | None) -> dict:
    return {
        "slug": s.slug,
        "name": s.name,
        "tagline": s.tagline,
        "bodyMd": s.body_md,
        "url": s.url,
        "ctaLabel": s.cta_label or "Visit",
        "background": s.background if _HEX.match(s.background or "") else "",
        "ink": s.ink if _HEX.match(s.ink or "") else "",
        "media": _media_payload(light),
        # Falls back to the light mark rather than to nothing: one wordmark that
        # reads on both is the common case, and a missing logo is worse than a
        # slightly-wrong one.
        "mediaDark": _media_payload(dark) or _media_payload(light),
        "featured": s.featured,
        "since": s.since,
        "until": s.until,
    }


async def _sponsor_rows(session: AsyncSession):
    light = aliased(Media)
    dark = aliased(Media)
    return (
        await session.execute(
            select(Sponsor, light, dark)
            .join(light, Sponsor.media_id == light.id, isouter=True)
            .join(dark, Sponsor.media_dark_id == dark.id, isouter=True)
            .where(Sponsor.visible.is_(True))
            .order_by(Sponsor.position, Sponsor.id)
        )
    ).all()


@router.get("/outfits")
async def get_outfits(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The costumes, in her order. The artist travels with the art."""
    rows = (
        await session.execute(
            select(Outfit, Media)
            .join(Media, Outfit.media_id == Media.id, isouter=True)
            .where(Outfit.visible.is_(True))
            .order_by(Outfit.position, Outfit.id)
        )
    ).all()
    return [
        {
            "slug": o.slug, "name": o.name, "status": o.status, "note": o.note,
            "artist": o.artist, "artistUrl": o.artist_url,
            "media": _media_payload(m),
        }
        for o, m in rows
    ]


@router.get("/sponsors")
async def get_sponsors(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Everyone on the Partners page, current and past, in her order."""
    return [_sponsor_payload(s, light, dark) for s, light, dark in await _sponsor_rows(session)]


@router.get("/sponsors/featured")
async def get_featured_sponsors(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """
    The landing page's row, capped.

    A sponsor whose `until` has passed is not featured even if the tick is
    still on — the home page is the loudest place on the site and it should not
    be thanking somebody who stopped six months ago.
    """
    today = date.today().isoformat()
    out = []
    for s, light, dark in await _sponsor_rows(session):
        if not s.featured:
            continue
        if s.until and s.until < today:
            continue
        out.append(_sponsor_payload(s, light, dark))
        if len(out) == FEATURED_SPONSORS:
            break
    return out


@router.get("/fan-art")
async def get_fan_art(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """
    The fan-works gallery.

    Artist credit travels with every piece and is never optional — the design
    makes it the loudest text on the card, and a gallery that loses the credit
    is worse than no gallery. `media` is nullable: a piece can be recorded
    before its file is uploaded and the card has a designed absent state.
    """
    rows = (
        await session.execute(
            select(FanArt, Media)
            .join(Media, FanArt.media_id == Media.id, isouter=True)
            .where(FanArt.visible.is_(True))
            .order_by(FanArt.position, FanArt.id)
        )
    ).all()
    return [
        {
            "artist": f.artist,
            "artistUrl": f.artist_url,
            "platform": f.platform,
            "title": f.title,
            "media": _media_payload(m),
        }
        for f, m in rows
    ]


@router.get("/imprint")
async def get_imprint(session: AsyncSession = Depends(get_session)) -> dict:
    """
    The legal imprint, or `{"visible": false}`.

    Hidden until it is filled in and switched on. The design ships bracketed
    placeholders, which is right for a mock-up and wrong to publish: a registry
    number that looks real and is not is worse than no imprint. It goes up from
    the admin the day the company exists.
    """
    from shruti.core.settings_store import imprint

    return await imprint(session)


@router.get("/site-state")
async def site_state(session: AsyncSession = Depends(get_session)) -> dict:
    """
    What the front of the site should be.

    Public and unauthenticated on purpose: the Astro middleware asks this on
    every request, and making it require a credential would mean shipping one
    to a process that has no user.
    """
    from shruti.core.settings_store import coming_soon, sections_live

    return {
        "comingSoon": await coming_soon(session),
        # Which whole sections a visitor may reach. The middleware asks for
        # this in the same call it already makes for the holding page, so
        # gating a section costs no extra round trip on every request.
        "sections": await sections_live(session),
    }
