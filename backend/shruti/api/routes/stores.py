# SPDX-License-Identifier: AGPL-3.0-only
"""Where the app can be got, if it can be got yet."""
from __future__ import annotations

from fastapi import APIRouter

from shruti.core.stores import android, ios

router = APIRouter(prefix="/api/app", tags=["app"])


@router.get("/stores")
async def stores() -> dict:
    """
    The stores that currently carry the app.

    ⚠ A dict of platforms, and each one is asked rather than declared. Nobody
    has to come back and switch a badge on: Android answers None until Play
    actually carries the package, and starts answering the moment it does.

    Android waits on a Play organisation account, which waits on a company
    being registered — so it will answer None for a while, which is correct
    and costs one request every half hour.
    """
    return {"ios": await ios(), "android": await android()}
