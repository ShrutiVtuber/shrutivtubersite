# SPDX-License-Identifier: AGPL-3.0-only
"""
The ephemeris, asked directly.

The bot does not call the website for arithmetic. Two reasons, and the second
is the one that shaped the design:

1. The website would *store* things — casting a chart writes a chart — and the
   bot is read-only by rule.
2. Birth data must not sit in somebody else's Discord. Nothing here persists
   anything; a computation happens and the answer is returned.

Deliberately free of any Discord import, so every function below can be
exercised in a test without a gateway, a token, or a server.
"""
from __future__ import annotations

import httpx

# Long enough for a cold ephemeris call, short enough that Discord's own
# three-second interaction deadline is not lost waiting on us. Anything slower
# than this is deferred by the caller.
TIMEOUT = 8.0


class AstroError(RuntimeError):
    """The ephemeris could not answer. The message is safe to show a user."""


class Astro:
    def __init__(self, base: str, client: httpx.AsyncClient | None = None) -> None:
        self._base = base.rstrip("/")
        self._client = client

    async def _get(self, path: str, params: dict) -> dict:
        # Drop empties rather than sending `place=`, which some endpoints read
        # as "a place named nothing" instead of "no place given".
        clean = {k: v for k, v in params.items() if v not in (None, "")}
        try:
            if self._client is not None:
                r = await self._client.get(f"{self._base}{path}", params=clean, timeout=TIMEOUT)
            else:
                async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                    r = await c.get(f"{self._base}{path}", params=clean)
        except httpx.TimeoutException as exc:
            raise AstroError("The ephemeris took too long to answer. Try again in a moment.") from exc
        except httpx.HTTPError as exc:
            raise AstroError("The ephemeris could not be reached.") from exc

        if r.status_code == 422:
            raise AstroError("That does not look like something I can compute.")
        if r.status_code >= 500:
            raise AstroError("The ephemeris is having trouble. Try again shortly.")
        if r.status_code >= 400:
            raise AstroError("I could not work that out.")

        body = r.json()
        # The daemon wraps some answers in `data` and returns others bare.
        return body.get("data", body) if isinstance(body, dict) else body

    async def planetary_hours(self, when: str, lat: float, lon: float) -> dict:
        return await self._get("/planetary-hours", {"when": when, "lat": lat, "lon": lon})

    async def panchanga(self, when: str, lat: float, lon: float) -> dict:
        return await self._get("/panchanga", {"when": when, "lat": lat, "lon": lon})

    async def attic(self, when: str) -> dict:
        return await self._get("/attic-calendar", {"when": when})

    async def hindu(self, when: str, lat: float, lon: float) -> dict:
        return await self._get("/hindu-calendar", {"when": when, "lat": lat, "lon": lon})

    async def isopsephy(self, text: str, language: str = "greek") -> dict:
        return await self._get("/isopsephy", {"text": text, "language": language})

    async def sigil(self, intent: str) -> dict:
        return await self._get("/sigil", {"intent": intent})

    async def stations(self, body: str, when: str, lat: float, lon: float) -> dict:
        return await self._get("/stations", {"body": body, "when": when, "lat": lat, "lon": lon, "days": 1})
