# SPDX-License-Identifier: AGPL-3.0-only
"""
Addresses that may not register again.

The list holds hashes. A ban follows a deletion and the deletion was the whole
point — keeping the just-deleted addresses in readable form would quietly
rebuild the thing that was meant to go. A hash answers the only question ever
asked of it and cannot be read back into a mailing list.
"""
from __future__ import annotations

import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models import BannedEmail


def normalise(email: str) -> str:
    """Lowercased and trimmed, so the same address hashes the same way."""
    return (email or "").strip().lower()


def fingerprint(email: str) -> str:
    return hashlib.sha256(normalise(email).encode("utf-8")).hexdigest()


def hint(email: str) -> str:
    """
    Enough to recognise a ban you are looking for; not enough to write to.

    "sophia@example.org" becomes "s…a@example.org". The domain is kept because
    it is what makes one entry distinguishable from the next in a list, and it
    identifies nobody on its own.
    """
    address = normalise(email)
    local, _, domain = address.partition("@")
    if not domain:
        return "…"
    shown = local[0] + "…" + local[-1] if len(local) > 2 else local[:1] + "…"
    return f"{shown}@{domain}"


async def is_banned(email: str, session: AsyncSession) -> bool:
    row = (
        await session.execute(
            select(BannedEmail).where(BannedEmail.email_hash == fingerprint(email))
        )
    ).scalar_one_or_none()
    return row is not None
