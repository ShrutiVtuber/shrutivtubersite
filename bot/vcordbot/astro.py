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

    async def attic(self, when: str, reckoning: str = "conjunction") -> dict:
        """
        The Athenian calendar for one day, under one reckoning.

        Conjunction is the astronomical new moon; visibility is the first
        crescent somebody could actually see, a day or two later. They open
        half the months of a year on different days, so which one was used is
        part of the answer rather than a setting.
        """
        return await self._get("/attic-calendar",
                               {"when": when, "reckoning": reckoning})

    async def hindu(self, when: str, lat: float, lon: float,
                    reckoning: str = "amanta") -> dict:
        """
        The Hindu calendar date under one reckoning.

        `reckoning` is not cosmetic: amānta and pūrṇimānta name the month
        differently for half of every month — Śrāvaṇa against Bhādrapada for
        the same day — and neither is the other's correction. Defaulting
        silently would answer a question nobody asked.
        """
        return await self._get("/hindu-calendar", {
            "when": when, "lat": lat, "lon": lon, "reckoning": reckoning})

    async def isopsephy(self, text: str, cipher: str = "greek-iso") -> dict:
        """
        Sum a word under one table.

        The parameter is `cipher` and it takes a SLUG — not `language` taking
        a language name. Sending the wrong one is not an error: the daemon
        ignores it, falls back to Greek, and returns a confident total with
        every Hebrew letter listed as unmatched. That is the worst shape a bug
        can take on this site, so the mapping lives in one place and is tested.
        """
        return await self._get("/isopsephy", {"text": text, "cipher": cipher})

    async def sigil(self, statement: str) -> dict:
        """
        The reduction of a statement of intent, step by step.

        The parameter is `statement`. It was `intent` here, which the daemon
        does not know: the call came back 422 every time, and nothing noticed
        because no command had ever been pointed at it.
        """
        return await self._get("/sigil", {"statement": statement})

    async def stations(self, body: str, when: str, lat: float, lon: float) -> dict:
        return await self._get("/stations", {"body": body, "when": when, "lat": lat, "lon": lon, "days": 1})

    async def events(self, start: str, end: str) -> dict:
        """
        What the sky does between two moments — ingresses, stations, lunations,
        eclipses. The material a horoscope is written FROM.

        Half-open at neither end: the desk on the site asks for the same span,
        and two answers to "what happens this week" would be one too many.
        """
        return await self._get("/events", {"start": start, "end": end})

    async def chart(self, when: str, lat: float, lon: float, *,
                    tradition: str = "hellenistic",
                    house_system: str = "whole_sign") -> dict:
        """
        A chart for one instant, seen from one place.

        `when` MUST carry its UTC offset. The daemon reads a bare
        `1996-05-14T09:30:00` as UTC, so a naive local wall clock silently
        becomes a different moment — right to the minute for somebody in
        London, three hours out for somebody in Athens, and eight for somebody
        in California. Every planet stays very nearly correct and only the
        ascendant moves, which is what makes it hard to see: the chart does not
        look wrong, it looks like somebody else's.

        `places.at()` is what produces an offset-bearing string, and it is the
        only thing that should be feeding this.
        """
        if not _has_offset(when):
            # Refused rather than corrected. Guessing UTC here is precisely the
            # bug this method exists to prevent, and a loud failure in a test
            # is worth more than a plausible chart.
            raise AstroError("I could not work out the timezone for that birth place.")
        return await self._get("/chart", {
            "when": when, "lat": lat, "lon": lon,
            "tradition": tradition, "house_system": house_system,
        })


def _has_offset(when: str) -> bool:
    """Whether an ISO-8601 string names its own offset, `Z` included."""
    tail = (when or "")[10:]                     # skip the date's own hyphens
    return tail.endswith("Z") or "+" in tail or "-" in tail
