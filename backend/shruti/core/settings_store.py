# SPDX-License-Identifier: AGPL-3.0-only
"""
Global key/value settings, read and written from the admin.

Things that belong here rather than in `.env`: values the site owner changes
without a deploy, and values that should be *absent* until they are real. The
imprint is both — it must not ship with invented registry numbers, and it must
go up the moment the company exists, without waiting for someone with SSH.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models import SiteSetting

# The imprint. Empty by default and hidden until turned on — see the note on
# `IMPRINT_VISIBLE`.
IMPRINT_KEYS = (
    "imprint.entity",
    "imprint.street",
    "imprint.postcode",
    "imprint.city",
    "imprint.country",
    "imprint.email",
    "imprint.registry",
    "imprint.vat",
)

IMPRINT_VISIBLE = "imprint.visible"


async def get_many(session: AsyncSession, keys: tuple[str, ...] | list[str]) -> dict[str, str]:
    rows = (
        await session.execute(select(SiteSetting).where(SiteSetting.key.in_(list(keys))))
    ).scalars().all()
    return {r.key: r.value for r in rows}


async def get_all(session: AsyncSession, prefix: str = "") -> dict[str, str]:
    rows = (await session.execute(select(SiteSetting))).scalars().all()
    return {r.key: r.value for r in rows if not prefix or r.key.startswith(prefix)}


async def put_many(session: AsyncSession, values: dict[str, str]) -> None:
    for key, value in values.items():
        row = (
            await session.execute(select(SiteSetting).where(SiteSetting.key == key))
        ).scalar_one_or_none()
        if row is None:
            session.add(SiteSetting(key=key, value=value))
        else:
            row.value = value
    await session.commit()


async def imprint(session: AsyncSession) -> dict:
    """
    The imprint as the footer should render it, or nothing.

    **Hidden until switched on, and switched on means someone filled it in.**
    The design ships bracketed placeholders — `GEMI [000000000000]` — which is
    the right convention for a mock-up and the wrong thing to publish: a
    registry number that looks like a registry number and is not one is worse
    than no imprint at all.

    So the rule here is: visible only when the flag is on AND the entity and
    email are actually present. A half-filled imprint stays down.
    """
    values = await get_many(session, IMPRINT_KEYS + (IMPRINT_VISIBLE,))
    on = values.get(IMPRINT_VISIBLE, "") == "1"
    entity = values.get("imprint.entity", "").strip()
    email = values.get("imprint.email", "").strip()

    if not (on and entity and email):
        return {"visible": False}

    return {
        "visible": True,
        "entity": entity,
        "street": values.get("imprint.street", ""),
        "postcode": values.get("imprint.postcode", ""),
        "city": values.get("imprint.city", ""),
        "country": values.get("imprint.country", ""),
        "email": email,
        "registry": values.get("imprint.registry", ""),
        "vat": values.get("imprint.vat", ""),
    }
