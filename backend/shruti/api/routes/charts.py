# SPDX-License-Identifier: AGPL-3.0-only
"""
Keeping a chart, and handing one to a friend.

**Two tokens per chart.** `owner_token` is how a person gets back to their own
chart. `share_token` is what they give away. They are different strings on
purpose: with one token, sharing would mean handing over your only way in, and
unsharing would be impossible. With two, a share can be revoked without the
owner losing anything.

**Neither token carries birth data**, so the date, time and place stay out of
the URL, out of a browser history, and out of a screenshot of the address bar.
The shared view does not print them either.

What that does **not** do — and the share dialogue says so in as many words —
is hide the birth data from someone who can read a chart. The ascendant gives
the birth time to within a few minutes and the planets give the date. The
figure IS the birth data, drawn. Hiding it from the URL stops the casual case
completely and the informed case not at all, and it would be dishonest to
imply otherwise.

**This holds special-category data.** Birth data used for an astrological
reading arguably reveals philosophical belief, so the lawful basis is explicit
consent — as with `Nativity`. An account holder has that on record against
their account. Somebody without an account has nothing to hang it on, so the
consent is stored on the chart row, verbatim and versioned. And because it
cannot be renewed by asking somebody we have no address for, an ownerless
chart expires; opening it puts the clock back.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.api.routes.accounts import current_user
from shruti.core.consents import CONSENT_VERSION, NATIVITY
from shruti.core.db import get_session
from shruti.models import CardDesign, Media
from shruti.models.accounts import Comparison, SavedChart, User

router = APIRouter(prefix="/api/charts", tags=["charts"])

# Long enough that guessing is not a strategy: 32 bytes of urlsafe randomness.
# These are bearer tokens for special-category data, so they are sized like
# passwords rather than like slugs.
TOKEN_BYTES = 32

# How long a chart nobody owns is kept, pushed forward every time it is opened.
# Not a tidy-up policy — the consent behind it cannot be renewed by asking, so
# it must not be relied on indefinitely.
ORPHAN_DAYS = 365

TRADITIONS = ("hellenistic", "vedic")
FIGURES = ("wheel", "north", "south")
HOUSE_SYSTEMS = ("whole_sign", "placidus", "equal", "porphyry",
                 "regiomontanus", "campanus")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


class Keep(BaseModel):
    """What it takes to keep a chart."""

    label: str = Field(default="", max_length=80)
    tradition: str = "hellenistic"
    house_system: str = "whole_sign"
    figure: str = "wheel"

    birth_date: str = Field(max_length=10)
    birth_time: Optional[str] = Field(default=None, max_length=5)
    time_unknown: bool = False
    place_name: str = Field(default="", max_length=160)
    lat: float = 0.0
    lon: float = 0.0

    # Required for somebody without an account, ignored for somebody with one
    # — their account already carries the consent, and asking twice for the
    # same permission teaches people to click past it.
    consent: bool = False


def _owner_view(chart: SavedChart) -> dict:
    """Everything, because it is theirs."""
    return {
        "label": chart.label,
        "tradition": chart.tradition,
        "houseSystem": chart.house_system,
        "figure": chart.figure,
        "birthDate": chart.birth_date,
        "birthTime": chart.birth_time,
        "timeUnknown": chart.time_unknown,
        "placeName": chart.place_name,
        "lat": chart.lat,
        "lon": chart.lon,
        "mine": chart.user_id is not None,
        "shared": chart.share_token is not None,
        "shareToken": chart.share_token,
        "sharedAt": chart.shared_at.isoformat() if chart.shared_at else None,
        "expiresAt": chart.expires_at.isoformat() if chart.expires_at else None,
        "createdAt": chart.created_at.isoformat() if chart.created_at else None,
    }


def _shared_view(chart: SavedChart) -> dict:
    """
    The figure, and nothing that spells out the moment.

    No birth date, no time, no place, no coordinates — not because they cannot
    be inferred from the chart by somebody who reads charts, but because
    printing them hands the same thing to everybody else too.

    What is passed on is what it takes to DRAW the chart, which necessarily
    includes the instant. That is the honest shape of the compromise: the
    drawing carries it, the page does not spell it out, and the person sharing
    was told as much before they made the link.
    """
    return {
        "label": chart.label,
        "tradition": chart.tradition,
        "houseSystem": chart.house_system,
        "figure": chart.figure,
        "timeUnknown": chart.time_unknown,
        # Needed to cast the chart at all. Not shown as text by the page.
        "birthDate": chart.birth_date,
        "birthTime": chart.birth_time,
        "lat": chart.lat,
        "lon": chart.lon,
    }


async def _by_owner(token: str, session: AsyncSession) -> SavedChart:
    chart = (
        await session.execute(select(SavedChart).where(SavedChart.owner_token == token))
    ).scalar_one_or_none()
    if chart is None:
        raise HTTPException(404, "no such chart")
    if chart.expires_at and chart.expires_at < _now():
        raise HTTPException(410, "this chart has expired")
    return chart


@router.post("", status_code=201)
async def keep(
    body: Keep,
    request: Request,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep this chart, whether or not there is an account.

    Works signed out. That is the point: a person who has just cast their chart
    should be able to keep it without being made to sign up first, and be
    *offered* an account because keeping it is nicer with one — not because the
    door is shut without one.
    """
    if body.tradition not in TRADITIONS:
        raise HTTPException(400, "unknown tradition")
    if body.figure not in FIGURES:
        raise HTTPException(400, "unknown figure")
    if body.house_system not in HOUSE_SYSTEMS:
        raise HTTPException(400, "unknown house system")
    if not body.birth_date:
        raise HTTPException(400, "a chart needs a date")

    chart = SavedChart(
        owner_token=_token(),
        user_id=user.id if user else None,
        label=body.label.strip(),
        tradition=body.tradition,
        house_system=body.house_system,
        figure=body.figure,
        birth_date=body.birth_date,
        birth_time=None if body.time_unknown else (body.birth_time or None),
        time_unknown=body.time_unknown,
        place_name=body.place_name.strip(),
        lat=body.lat,
        lon=body.lon,
        last_seen_at=_now(),
    )

    if user is None:
        # No account to hang a consent record on, so it is evidenced here,
        # verbatim, under the version they were shown.
        if not body.consent:
            raise HTTPException(
                400,
                "keeping a chart means storing birth data, which needs consent",
            )
        chart.consent_version = CONSENT_VERSION
        chart.consent_wording = NATIVITY.wording
        chart.consent_source = "chart-keep"
        chart.consent_at = _now()
        chart.expires_at = _now() + timedelta(days=ORPHAN_DAYS)

    session.add(chart)
    await session.commit()
    await session.refresh(chart)
    return {"ownerToken": chart.owner_token, "chart": _owner_view(chart)}


@router.get("/mine", dependencies=[])
async def mine(
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Every chart on this account, newest first."""
    if user is None:
        raise HTTPException(401, "not signed in")
    rows = (
        await session.execute(
            select(SavedChart)
            .where(SavedChart.user_id == user.id)
            .order_by(SavedChart.id.desc())
        )
    ).scalars().all()
    return [{**_owner_view(c), "ownerToken": c.owner_token} for c in rows]


@router.get("/o/{token}")
async def open_mine(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Open a chart by its owner token, and push the expiry back."""
    chart = await _by_owner(token, session)
    chart.last_seen_at = _now()
    if chart.user_id is None:
        chart.expires_at = _now() + timedelta(days=ORPHAN_DAYS)
    await session.commit()
    return _owner_view(chart)


@router.post("/o/{token}/share")
async def start_sharing(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Mint a link to hand out. Idempotent: asking twice returns the same link.

    Re-minting on every request would quietly break links already sent, which
    is the opposite of what pressing "share" again means.
    """
    chart = await _by_owner(token, session)
    if chart.share_token is None:
        chart.share_token = _token()
        chart.shared_at = _now()
        await session.commit()
    return {"shareToken": chart.share_token}


@router.delete("/o/{token}/share", status_code=204)
async def stop_sharing(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Take the link back.

    The link stops working. It does not un-send the link, and it does not
    un-see what has been seen — but it is the difference between a share that
    is permanent by accident and one that is a decision.
    """
    chart = await _by_owner(token, session)
    chart.share_token = None
    chart.shared_at = None
    await session.commit()
    return Response(status_code=204)


@router.post("/o/{token}/claim")
async def claim(
    token: str,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Attach a chart kept without an account to the account just made.

    This is what stops "sign up to keep your chart" from being a lie: the chart
    they already have follows them in, rather than being cast again. Claiming
    also clears the expiry, because there is now somebody to ask.
    """
    if user is None:
        raise HTTPException(401, "not signed in")
    chart = await _by_owner(token, session)
    if chart.user_id is not None and chart.user_id != user.id:
        # Somebody else's, and holding the token does not change that.
        raise HTTPException(409, "that chart already belongs to an account")
    chart.user_id = user.id
    chart.expires_at = None
    await session.commit()
    return _owner_view(chart)


@router.delete("/o/{token}", status_code=204)
async def forget(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    Delete it, now, without asking anybody.

    Here because this table holds special-category data for people who may
    never have made an account, and a right to erasure that requires writing
    an email is not much of a right.
    """
    chart = await _by_owner(token, session)
    await session.delete(chart)
    await session.commit()
    return Response(status_code=204)


@router.get("/s/{token}")
async def open_shared(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """What a friend sees. See `_shared_view` for what is left out, and why."""
    chart = (
        await session.execute(select(SavedChart).where(SavedChart.share_token == token))
    ).scalar_one_or_none()
    if chart is None:
        raise HTTPException(404, "no such chart")
    if chart.expires_at and chart.expires_at < _now():
        raise HTTPException(410, "this chart has expired")
    return _shared_view(chart)


# ── two charts, read against each other ─────────────────────────────────────
#
# The arithmetic is the easy half and the site already does it. What somebody
# MAKES here is the paragraph they write underneath, which is why the reading
# is a column rather than an afterthought and why a share link usually exists
# to show it.
#
# Both sides are references to kept charts, never copies of birth data.
# Deleting a chart cascades, so a moment somebody asked to be forgotten does
# not survive inside a comparison built on it.


class CompareIn(BaseModel):
    """`right` may be an owner token or a SHARE token — see `_chart_by_any`."""

    left: str = Field(max_length=120)
    right: str = Field(max_length=120)
    label: str = Field(default="", max_length=80)
    tradition: str = "hellenistic"
    orb: float = Field(default=6.0, ge=1.0, le=10.0)
    consent: bool = False


async def _chart_by_any(token: str, session: AsyncSession) -> SavedChart | None:
    """
    A chart by either of its tokens.

    Comparing against a chart somebody shared with you is the whole point of
    the feature, and they handed you a SHARE token — so that has to work here
    without turning it into an owner token anywhere else. This returns the row;
    it never lets the caller act as its owner.
    """
    for column in (SavedChart.owner_token, SavedChart.share_token):
        row = (
            await session.execute(select(SavedChart).where(column == token))
        ).scalar_one_or_none()
        if row is not None:
            return row
    return None


def _comparison_view(row: Comparison, left: SavedChart, right: SavedChart,
                     *, owner: bool) -> dict:
    """
    What a comparison is, to whoever is looking.

    A viewer gets the two moments because the aspects cannot be drawn without
    them — the same honest compromise a shared chart makes — but not the place
    names, which are the one part no reader can recover from the figure.
    """
    def side(c: SavedChart) -> dict:
        out = {
            "label": c.label,
            "birthDate": c.birth_date,
            "birthTime": c.birth_time,
            "timeUnknown": c.time_unknown,
            "lat": c.lat,
            "lon": c.lon,
            "tradition": c.tradition,
            "figure": c.figure,
        }
        if owner:
            out["placeName"] = c.place_name
        return out

    return {
        "label": row.label,
        "readingMd": row.reading_md,
        "tradition": row.tradition,
        "orb": row.orb,
        "cardTheme": row.card_theme,
        "left": side(left),
        "right": side(right),
        "shared": row.share_token is not None,
        "shareToken": row.share_token if owner else None,
        "mine": row.user_id is not None,
    }


@router.post("/compare", status_code=201)
async def compare(
    body: CompareIn,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Keep a comparison of two charts.

    Consent is asked for exactly as it is for a chart, and for the same reason:
    this row is a durable pointer at two birth moments.
    """
    left = await _chart_by_any(body.left, session)
    right = await _chart_by_any(body.right, session)
    if left is None or right is None:
        raise HTTPException(404, "one of those charts could not be found")
    if left.id == right.id:
        raise HTTPException(400, "that is the same chart twice")
    if body.tradition not in TRADITIONS:
        raise HTTPException(400, "unknown tradition")

    row = Comparison(
        owner_token=_token(),
        user_id=user.id if user else None,
        left_id=left.id,
        right_id=right.id,
        label=body.label.strip(),
        tradition=body.tradition,
        orb=body.orb,
    )

    if user is None:
        if not body.consent:
            raise HTTPException(
                400, "keeping a comparison means keeping a pointer at two birth"
                     " moments, which needs consent",
            )
        row.expires_at = _now() + timedelta(days=ORPHAN_DAYS)

    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"ownerToken": row.owner_token,
            "comparison": _comparison_view(row, left, right, owner=True)}


async def _load_comparison(row: Comparison, session: AsyncSession):
    left = await session.get(SavedChart, row.left_id)
    right = await session.get(SavedChart, row.right_id)
    if left is None or right is None:
        # One side was deleted. Say so rather than rendering half a reading.
        raise HTTPException(410, "one of these charts has been deleted")
    return left, right


@router.get("/compare/o/{token}")
async def open_comparison(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")
    if row.expires_at and row.expires_at < _now():
        raise HTTPException(410, "this comparison has expired")
    if row.user_id is None:
        row.expires_at = _now() + timedelta(days=ORPHAN_DAYS)
        await session.commit()
    left, right = await _load_comparison(row, session)
    return _comparison_view(row, left, right, owner=True)


class ReadingIn(BaseModel):
    label: str = Field(default="", max_length=80)
    reading_md: str = Field(default="", max_length=20000)


@router.put("/compare/o/{token}")
async def write_reading(
    token: str, body: ReadingIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """What they wrote about it. Editable, unlike a sent letter — nobody has
    been handed a copy that must keep matching."""
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")
    row.label = body.label.strip()
    row.reading_md = body.reading_md
    await session.commit()
    left, right = await _load_comparison(row, session)
    return _comparison_view(row, left, right, owner=True)


async def _backdrop_for(design: CardDesign, session: AsyncSession) -> bytes | None:
    """
    The art behind a card, from wherever this design keeps it.

    Two sources on purpose. `media_id` is anything she uploads. `backdrop_asset`
    names a file that SHIPS with the application — the Rose horizon sky is part
    of the design rather than content, and a fresh install has to have it
    without somebody remembering to upload a PNG.

    Never raises. A card without its backdrop is still a card; a 500 here would
    take out the page embedding it.
    """
    if design.media_id:
        art = await session.get(Media, design.media_id)
        if art is not None:
            try:
                from shruti.core.storage import fetch

                got = await fetch(art.filename)
                if got and got[0]:
                    return got[0]
            except Exception:                          # noqa: BLE001
                pass

    if design.backdrop_asset:
        from pathlib import Path as _Path

        # Basename only: this is a database field, and a row reading
        # "../../etc/passwd" must not be able to reach it.
        safe = _Path(design.backdrop_asset).name
        candidate = _Path(__file__).resolve().parents[2] / "assets" / safe
        try:
            if candidate.is_file():
                return candidate.read_bytes()
        except Exception:                              # noqa: BLE001
            pass

    return None


@router.get("/card-sample.png")
async def card_sample(
    design: str = "light", session: AsyncSession = Depends(get_session)
) -> Response:
    """
    A card with invented people on it, for the page that explains the feature.

    Fixed names and a fixed tally, so the example is the same every time
    somebody looks and nobody's real chart is used to advertise anything.
    """
    from shruti.core.sharecard import comparison_card

    chosen = (
        await session.execute(
            select(CardDesign).where(CardDesign.key == design,
                                     CardDesign.visible.is_(True))
        )
    ).scalar_one_or_none()
    if chosen is None:
        chosen = (
            await session.execute(
                select(CardDesign).where(CardDesign.visible.is_(True))
                .order_by(CardDesign.position, CardDesign.id)
            )
        ).scalars().first()
    if chosen is None:
        raise HTTPException(404, "no design is available")

    backdrop = await _backdrop_for(chosen, session)

    png = comparison_card(
        left_name="Someone", right_name="Someone else",
        headline="Luminaries in contact", band="Written in the same sky",
        harmonious=14, hard=3,
        design={"background": chosen.background, "ink": chosen.ink,
                "soft": chosen.soft, "faint": chosen.faint,
                "line": chosen.line, "accent": chosen.accent,
                "scrim": chosen.scrim},
        backdrop=backdrop,
    )
    return Response(content=png, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})


class StartIn(BaseModel):
    """Everything needed to be ready to invite somebody, in one submit."""

    birth_date: str = Field(max_length=10)
    birth_time: Optional[str] = Field(default=None, max_length=5)
    time_unknown: bool = False
    place_name: str = Field(default="", max_length=160)
    lat: float = 0.0
    lon: float = 0.0
    label: str = Field(default="", max_length=80)
    consent: bool = False


@router.post("/start", status_code=201)
async def start(
    body: StartIn,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Cast, keep and make an invitation in one step.

    The long way round — cast on the instrument, scroll, keep, find the invite
    panel, press it — is four pages for somebody who arrived wanting to do one
    thing. This is the front door, and it hands back the invitation ready to
    send.
    """
    if not body.birth_date:
        raise HTTPException(400, "a chart needs a date")
    if user is None and not body.consent:
        raise HTTPException(
            400, "keeping a chart means storing birth data, which needs consent"
        )

    chart = SavedChart(
        owner_token=_token(),
        share_token=_token(),
        user_id=user.id if user else None,
        label=body.label.strip() or "Mine",
        birth_date=body.birth_date,
        birth_time=None if body.time_unknown else (body.birth_time or None),
        time_unknown=body.time_unknown,
        place_name=body.place_name.strip(),
        lat=body.lat,
        lon=body.lon,
        last_seen_at=_now(),
        shared_at=_now(),
    )
    if user is None:
        from shruti.core.consents import CONSENT_VERSION, NATIVITY

        chart.consent_version = CONSENT_VERSION
        chart.consent_wording = NATIVITY.wording
        chart.consent_source = "compare-start"
        chart.consent_at = _now()
        chart.expires_at = _now() + timedelta(days=ORPHAN_DAYS)

    session.add(chart)
    await session.commit()
    await session.refresh(chart)
    return {"ownerToken": chart.owner_token, "shareToken": chart.share_token}


@router.get("/card-designs")
async def card_designs(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """The designs somebody may pick between when sharing."""
    rows = (
        await session.execute(
            select(CardDesign).where(CardDesign.visible.is_(True))
            .order_by(CardDesign.position, CardDesign.id)
        )
    ).scalars().all()
    return [{"key": d.key, "name": d.name or d.key,
             "background": d.background, "ink": d.ink,
             "blurb": d.blurb,
             # The showcase labels a design by what it IS, and "backdrop" is
             # the one distinction a visitor can see before clicking.
             "backdrop": bool(d.media_id or d.backdrop_asset)} for d in rows]


class DesignIn(BaseModel):
    design: str = Field(max_length=60)


@router.put("/compare/o/{token}/design")
async def choose_design(
    token: str, body: DesignIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Which design the card is drawn in.

    Stored on the comparison rather than passed in the card's URL, because
    that URL goes into og:image and a social scraper fetches exactly what it
    says — the choice has to be part of the page, not of the request.
    """
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")
    exists = (
        await session.execute(
            select(CardDesign).where(CardDesign.key == body.design,
                                     CardDesign.visible.is_(True))
        )
    ).scalar_one_or_none()
    if exists is None:
        raise HTTPException(400, "no such design")
    row.card_theme = body.design
    await session.commit()
    return {"design": row.card_theme}


@router.post("/compare/o/{token}/share")
async def share_comparison(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")
    if row.share_token is None:
        row.share_token = _token()
        row.shared_at = _now()
        await session.commit()
    return {"shareToken": row.share_token}


@router.delete("/compare/o/{token}/share", status_code=204)
async def unshare_comparison(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is not None:
        row.share_token = None
        row.shared_at = None
        await session.commit()
    return Response(status_code=204)


@router.delete("/compare/o/{token}", status_code=204)
async def forget_comparison(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    row = (
        await session.execute(select(Comparison).where(Comparison.owner_token == token))
    ).scalar_one_or_none()
    if row is not None:
        await session.delete(row)
        await session.commit()
    return Response(status_code=204)


@router.get("/compare/s/{token}")
async def open_shared_comparison(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    row = (
        await session.execute(select(Comparison).where(Comparison.share_token == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")
    if row.expires_at and row.expires_at < _now():
        raise HTTPException(410, "this comparison has expired")
    left, right = await _load_comparison(row, session)
    return _comparison_view(row, left, right, owner=False)


# ── the reading, and the image it travels as ────────────────────────────────


async def _cross(left: SavedChart, right: SavedChart, tradition: str, orb: float) -> dict:
    """Ask the ephemeris what the two charts do to each other."""
    import httpx

    def moment(c: SavedChart) -> str:
        clock = "12:00" if c.time_unknown else (c.birth_time or "12:00")
        return f"{c.birth_date}T{clock}:00"

    # The same environment variable the journal reads. One name for one thing.
    base = os.environ.get("SHRUTI_ASTRO_INTERNAL", "http://shruti-astro:8000").rstrip("/")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base}/synastry", params={
            "when_a": moment(left), "lat_a": left.lat, "lon_a": left.lon,
            "when_b": moment(right), "lat_b": right.lat, "lon_b": right.lon,
            "tradition": tradition, "orb": orb,
            "time_unknown_a": str(left.time_unknown).lower(),
            "time_unknown_b": str(right.time_unknown).lower(),
        })
    r.raise_for_status()
    body = r.json()
    return body.get("data", body)


class InviteIn(BaseModel):
    """Their birth details, cast and compared in one step."""

    birth_date: str = Field(max_length=10)
    birth_time: Optional[str] = Field(default=None, max_length=5)
    time_unknown: bool = False
    place_name: str = Field(default="", max_length=160)
    lat: float = 0.0
    lon: float = 0.0
    label: str = Field(default="", max_length=80)
    tradition: str = "hellenistic"
    consent: bool = False


@router.post("/invite/{token}", status_code=201)
async def accept_invite(
    token: str,
    body: InviteIn,
    user: User | None = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Somebody accepts an invitation to compare charts.

    `token` is the INVITER's share token — the thing they posted or sent. This
    keeps the guest's own chart and builds the comparison in one step, because
    asking a person who arrived from a tweet to cast a chart, keep it, copy its
    address and paste it somewhere else is four chances to lose them.

    **The guest owns their own chart.** They get its owner token back, so
    deleting it later is theirs to do and takes the comparison with it. The
    inviter never gains any power over it — they hold a share token, and a
    share token has never been able to act as an owner anywhere in this file.
    """
    theirs = (
        await session.execute(
            select(SavedChart).where(SavedChart.share_token == token)
        )
    ).scalar_one_or_none()
    if theirs is None:
        raise HTTPException(404, "that invitation is not valid any more")
    if theirs.expires_at and theirs.expires_at < _now():
        raise HTTPException(410, "that invitation has expired")
    if not body.birth_date:
        raise HTTPException(400, "a chart needs a date")
    if user is None and not body.consent:
        raise HTTPException(
            400, "keeping your chart means storing birth data, which needs consent"
        )

    mine = SavedChart(
        owner_token=_token(),
        user_id=user.id if user else None,
        label=body.label.strip() or "Mine",
        tradition=body.tradition if body.tradition in TRADITIONS else "hellenistic",
        figure="wheel",
        birth_date=body.birth_date,
        birth_time=None if body.time_unknown else (body.birth_time or None),
        time_unknown=body.time_unknown,
        place_name=body.place_name.strip(),
        lat=body.lat,
        lon=body.lon,
        last_seen_at=_now(),
    )
    if user is None:
        from shruti.core.consents import CONSENT_VERSION, NATIVITY

        mine.consent_version = CONSENT_VERSION
        mine.consent_wording = NATIVITY.wording
        mine.consent_source = "chart-invite"
        mine.consent_at = _now()
        mine.expires_at = _now() + timedelta(days=ORPHAN_DAYS)

    session.add(mine)
    await session.commit()
    await session.refresh(mine)

    both = Comparison(
        owner_token=_token(),
        user_id=user.id if user else None,
        left_id=theirs.id,
        right_id=mine.id,
        label=f"{theirs.label or 'Them'} and {mine.label}",
        tradition=mine.tradition,
    )
    if user is None:
        both.expires_at = _now() + timedelta(days=ORPHAN_DAYS)
    session.add(both)
    await session.commit()
    await session.refresh(both)

    # Shared immediately: an invitation whose result only one person can see
    # is not an invitation.
    both.share_token = _token()
    both.shared_at = _now()
    await session.commit()

    return {
        "chartToken": mine.owner_token,
        "comparisonToken": both.owner_token,
        "shareToken": both.share_token,
    }


@router.get("/invite/{token}")
async def read_invite(
    token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Who is inviting, and nothing else about them."""
    theirs = (
        await session.execute(
            select(SavedChart).where(SavedChart.share_token == token)
        )
    ).scalar_one_or_none()
    if theirs is None:
        raise HTTPException(404, "that invitation is not valid any more")
    if theirs.expires_at and theirs.expires_at < _now():
        raise HTTPException(410, "that invitation has expired")
    # The name they gave their chart, and whether there is a face to show.
    # Not the moment: that is theirs until a comparison exists.
    return {"label": theirs.label or "Someone", "hasAvatar": bool(theirs.avatar_media_id)}


@router.get("/compare/{which}/{token}/reading")
async def reading(
    which: str, token: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """
    What the tradition says about these two charts.

    Generated from the configurations actually present. **Never a score** — see
    `core/synastry.py` for why a percentage would be the dishonest shape.
    """
    if which not in ("o", "s"):
        raise HTTPException(404, "no such comparison")
    column = Comparison.owner_token if which == "o" else Comparison.share_token
    row = (
        await session.execute(select(Comparison).where(column == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")

    left, right = await _load_comparison(row, session)
    try:
        cross = await _cross(left, right, row.tradition, row.orb)
    except Exception:                                  # noqa: BLE001
        raise HTTPException(503, "the ephemeris could not be reached")

    from shruti.core.synastry import read

    return read(cross.get("byDegree", []),
                left.label or "The first", right.label or "The second")


@router.get("/invite/{token}/card.png")
async def invite_card_png(
    token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    The image an invitation unfurls with.

    The invite is the link that gets posted publicly, tagging somebody — so it
    is the most-seen image in the whole compatibility loop and it was the only
    one that did not exist. It rendered with the site's default card, which says
    nothing about who is asking or what is being asked.

    Never raises for a missing avatar or a bad design: a plain card is a card,
    and a 500 here would take out the page that embeds it.
    """
    theirs = (
        await session.execute(
            select(SavedChart).where(SavedChart.share_token == token)
        )
    ).scalar_one_or_none()
    if theirs is None:
        raise HTTPException(404, "that invitation is not valid any more")
    if theirs.expires_at and theirs.expires_at < _now():
        raise HTTPException(410, "that invitation has expired")

    avatar: bytes | None = None
    if theirs.avatar_media_id:
        media = await session.get(Media, theirs.avatar_media_id)
        if media is not None:
            try:
                from shruti.core.storage import fetch

                got = await fetch(media.filename)
                avatar = got[0] if got else None
            except Exception:                          # noqa: BLE001
                avatar = None

    from shruti.core.sharecard import invite_card

    png = invite_card(name=theirs.label or "Someone", avatar=avatar)
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/compare/{which}/{token}/card.png")
async def card(
    which: str, token: str, session: AsyncSession = Depends(get_session)
) -> Response:
    """
    The image a share turns into on a timeline.

    Generated rather than screenshotted, so it is right every time and does not
    depend on whose browser made it. Cached hard: the inputs are two birth
    moments and neither changes.
    """
    if which not in ("o", "s"):
        raise HTTPException(404, "no such comparison")
    column = Comparison.owner_token if which == "o" else Comparison.share_token
    row = (
        await session.execute(select(Comparison).where(column == token))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "no such comparison")

    left, right = await _load_comparison(row, session)
    try:
        cross = await _cross(left, right, row.tradition, row.orb)
        from shruti.core.synastry import read

        said = read(cross.get("byDegree", []),
                    left.label or "The first", right.label or "The second")
    except Exception:                                  # noqa: BLE001
        said = {"tally": {"harmonious": 0, "hard": 0},
                "band": {"name": "Mixed testimony"},
                "cardHeadline": "Two charts"}

    async def avatar(chart: SavedChart) -> bytes | None:
        if not chart.avatar_media_id:
            return None
        media = await session.get(Media, chart.avatar_media_id)
        if media is None:
            return None
        try:
            from shruti.core.storage import fetch

            got = await fetch(media.filename)
            return got[0] if got else None
        except Exception:                              # noqa: BLE001
            # A card without an avatar is a card. A 500 here would take out
            # the page that embeds it.
            return None

    # Whichever design the owner chose, falling back to the first visible one
    # so a card renders even if the chosen design was hidden or deleted.
    chosen = (
        await session.execute(
            select(CardDesign).where(CardDesign.key == (row.card_theme or "light"))
        )
    ).scalar_one_or_none()
    if chosen is None or not chosen.visible:
        chosen = (
            await session.execute(
                select(CardDesign).where(CardDesign.visible.is_(True))
                .order_by(CardDesign.position, CardDesign.id)
            )
        ).scalars().first()

    design = {
        "background": chosen.background, "ink": chosen.ink, "soft": chosen.soft,
        "faint": chosen.faint, "line": chosen.line, "accent": chosen.accent,
        "scrim": chosen.scrim,
    } if chosen else {}

    backdrop = await _backdrop_for(chosen, session) if chosen else None

    from shruti.core.sharecard import comparison_card

    png = comparison_card(
        left_name=left.label or "—",
        right_name=right.label or "—",
        headline=said.get("cardHeadline", ""),
        band=said.get("band", {}).get("name", ""),
        harmonious=said["tally"]["harmonious"],
        hard=said["tally"]["hard"],
        left_avatar=await avatar(left),
        right_avatar=await avatar(right),
        design=design,
        backdrop=backdrop,
    )
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )
