# SPDX-License-Identifier: AGPL-3.0-only
"""Shared dependencies."""

from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shruti.core.auth import read_claims
from shruti.core.db import get_session


async def require_admin(
    request: Request, session: AsyncSession = Depends(get_session)
) -> str:
    """
    Gate an admin route.

    Reads a bearer token or the session cookie. Returns 401 with no detail
    about *why* — an error that distinguishes "expired" from "forged" tells an
    attacker which half of the problem to work on.

    **A valid signature is not enough.** The token also has to match the
    operator as they are right now. Checking only the signature meant a token
    outlived everything it was issued against: changing the password after a
    compromise left the attacker signed in for another twelve hours, unclaiming
    the site left every old session working, and a token naming an address that
    had never been the operator was accepted, because nothing ever compared it
    to anything. The stamp is a fingerprint of the current email and password
    hash, so any change to either ends every session that predates it.
    """
    from shruti.core.operator import operator_email, session_stamp

    token = ""
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        token = header[7:].strip()
    if not token:
        token = request.cookies.get("shruti_session", "")

    claims = read_claims(token) if token else None
    if not claims:
        raise HTTPException(401, "not authenticated")

    subject = (claims.get("sub") or "").strip().lower()
    current = (await operator_email(session)).strip().lower()
    # No operator means no admin. An unclaimed site has nobody to be.
    if not current or not hmac.compare_digest(subject, current):
        raise HTTPException(401, "not authenticated")

    expected = await session_stamp(session)
    if not hmac.compare_digest(claims.get("stm") or "", expected):
        raise HTTPException(401, "not authenticated")

    return subject
