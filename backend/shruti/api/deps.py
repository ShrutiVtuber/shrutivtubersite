# SPDX-License-Identifier: AGPL-3.0-only
"""Shared dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from shruti.core.auth import read_token


async def require_admin(request: Request) -> str:
    """
    Gate an admin route.

    Reads a bearer token or the session cookie. Returns 401 with no detail about
    *why* — an error that distinguishes "expired" from "forged" tells an
    attacker which half of the problem to work on.
    """
    token = ""
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        token = header[7:].strip()
    if not token:
        token = request.cookies.get("shruti_session", "")

    subject = read_token(token) if token else None
    if not subject:
        raise HTTPException(401, "not authenticated")
    return subject
