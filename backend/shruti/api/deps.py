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


async def school_open(request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """
    Swara Studio's API while the school is hidden (`page.carnatic` = 0).

    The pages already 404 for everyone but her (the site middleware); without
    this the API behind them answered anybody who knew an address: the raga
    data, the course, posting to Listen. So while the school is unpublished it
    answers only three callers, and everyone else gets the same 404 as the
    pages:

    - the operator, by her session (her own browser, previewing);
    - the site itself, rendering her preview on the server without her cookie,
      by the internal secret (`X-Shruti-Internal`, as the bot bridge uses);
    - nobody else. A missing secret refuses rather than opens.

    Once she publishes the school this costs one settings read and passes.
    """
    import os

    from shruti.core.settings_store import sections_live

    if (await sections_live(session)).get("carnatic", True):
        return
    secret = os.environ.get("SHRUTI_INTERNAL_SECRET", "").strip()
    given = request.headers.get("X-Shruti-Internal", "")
    if secret and hmac.compare_digest(given, secret):
        return
    try:
        await require_admin(request, session)
    except HTTPException:
        raise HTTPException(404, "Not found") from None
