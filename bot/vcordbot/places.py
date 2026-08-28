# SPDX-License-Identifier: AGPL-3.0-only
"""
A city, turned into an observer.

**Same gazetteer as the website and as theourgia**: Open-Meteo over GeoNames.
Reusing it rather than picking a third source means a chart cast in Discord and
the same chart cast on the site agree about where Athens is, instead of two
products quietly disagreeing by a few kilometres. No API key and no account, so
the bot gains nothing it must be trusted with.

**The bot resolves the offset itself.** The gazetteer gives an IANA zone NAME,
never an offset, and the name is the only thing that survives the question the
nativity actually asks: not "what is the offset in Greece" but "what was the
offset in Greece on the fourteenth of May 1996". Those differ by an hour for
half the year and by more than that across a century of rule changes.

Why that matters more here than anywhere else in this codebase: the ascendant
moves a degree every four minutes. An hour of error is fifteen degrees, which
is half a sign — and every planet is still very nearly right, so the chart does
not look wrong. It looks like somebody else's.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

GEOCODER = "https://geocoding-api.open-meteo.com/v1/search"

# Long enough for a cold gazetteer, short enough to fail while somebody still
# believes it is trying. The interaction is deferred before this runs, so this
# is not competing with Discord's three-second deadline.
TIMEOUT = 8.0

# Asked for generously and filtered here, because "Springfield" needs a country
# to disambiguate and the gazetteer will not do that filtering for us.
CANDIDATES = 20


class PlaceError(RuntimeError):
    """No place could be resolved. The message is safe to show a user."""


# Names people type for countries whose gazetteer name is something else. The
# gazetteer's own `country` and `country_code` are matched first and this is
# only the fallback, so it needs to cover habits, not the world.
COUNTRY_ALIASES = {
    "usa": "US", "us": "US", "u.s.": "US", "u.s.a.": "US",
    "united states": "US", "united states of america": "US", "america": "US",
    "uk": "GB", "u.k.": "GB", "britain": "GB", "great britain": "GB",
    "united kingdom": "GB", "england": "GB", "scotland": "GB",
    "wales": "GB", "northern ireland": "GB",
    "uae": "AE", "united arab emirates": "AE",
    "south korea": "KR", "north korea": "KP",
    "russia": "RU", "czechia": "CZ", "czech republic": "CZ",
    "holland": "NL", "netherlands": "NL",
    "ivory coast": "CI", "burma": "MM",
}

# US states by postal code, because an American will type "CA" and the
# gazetteer answers "California". Nowhere else in the world does this hold
# strongly enough to be worth a table, which is why there is only one.
US_STATES = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas",
    "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware",
    "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho",
    "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas",
    "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota",
    "ms": "mississippi", "mo": "missouri", "mt": "montana", "ne": "nebraska",
    "nv": "nevada", "nh": "new hampshire", "nj": "new jersey",
    "nm": "new mexico", "ny": "new york", "nc": "north carolina",
    "nd": "north dakota", "oh": "ohio", "ok": "oklahoma", "or": "oregon",
    "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina",
    "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah",
    "vt": "vermont", "va": "virginia", "wa": "washington",
    "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming",
    "dc": "district of columbia", "pr": "puerto rico",
}


@dataclass(frozen=True)
class Place:
    """One resolved observer. Everything a chart needs about where."""

    name: str
    region: str          # admin1 — the state, province or periphery
    country: str
    country_code: str
    lat: float
    lon: float
    elevation: float
    timezone: str        # IANA zone NAME, never an offset
    population: int

    @property
    def label(self) -> str:
        """How the place is shown back. Region only where it disambiguates."""
        parts = [self.name]
        if self.region and self.region.lower() != self.name.lower():
            parts.append(self.region)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().replace(".", "").split())


def _country_matches(entry: dict, wanted: str) -> bool:
    """Whether a gazetteer row is in the country somebody named."""
    if not wanted:
        return True
    want = _norm(wanted)
    code = (entry.get("country_code") or "").lower()
    name = _norm(entry.get("country") or "")
    if want == name or want == code:
        return True
    alias = COUNTRY_ALIASES.get(want, "")
    return bool(alias) and alias.lower() == code


def _region_matches(entry: dict, wanted: str) -> bool:
    """Whether a row is in the state or province somebody named."""
    if not wanted:
        return True
    want = _norm(wanted)
    region = _norm(entry.get("admin1") or "")
    if want == region:
        return True
    # "CA" for California, and the reverse so "California" still matches a row
    # the gazetteer happens to have abbreviated.
    return US_STATES.get(want, "") == region or US_STATES.get(region, "") == want


async def find(city: str, country: str = "", region: str = "",
               client: httpx.AsyncClient | None = None) -> tuple[Place, list[Place]]:
    """
    Resolve a city to an observer, and say what else it could have been.

    Returns the best match and the OTHER candidates that also fit. Both halves
    matter: the site's place control shows the resolution back with a "Not this
    place?" escape for exactly this reason, and a chat message has no such
    control — so the alternatives are named in the answer instead. A chart cast
    for the wrong Springfield is indistinguishable from a right one.

    "Best" is by population, which is a heuristic and is why the runners-up are
    returned rather than discarded.
    """
    city = (city or "").strip()
    if len(city) < 2:
        raise PlaceError("Give me a city name.")

    params = {"name": city, "count": CANDIDATES, "language": "en", "format": "json"}
    try:
        if client is not None:
            response = await client.get(GEOCODER, params=params, timeout=TIMEOUT)
        else:
            async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                response = await c.get(GEOCODER, params=params)
    except httpx.HTTPError as exc:
        # A gazetteer that cannot be reached is not a place that does not
        # exist, and the person asking must be able to tell those apart.
        raise PlaceError("The place index could not be reached. Try again shortly.") from exc

    if response.status_code != 200:
        raise PlaceError("The place index could not be reached. Try again shortly.")

    rows = (response.json() or {}).get("results") or []
    kept = [r for r in rows
            if r.get("latitude") is not None and r.get("longitude") is not None
            and r.get("name")
            and _country_matches(r, country) and _region_matches(r, region)]

    if not kept:
        where = ", ".join(p for p in (region, country) if p)
        raise PlaceError(
            f"I could not find **{city}**{' in ' + where if where else ''}. "
            "Check the spelling, or try the country's own name for it."
        )

    kept.sort(key=lambda r: int(r.get("population") or 0), reverse=True)

    def build(r: dict) -> Place:
        return Place(
            name=r.get("name") or "",
            region=r.get("admin1") or "",
            country=r.get("country") or "",
            country_code=r.get("country_code") or "",
            lat=round(float(r["latitude"]), 6),
            lon=round(float(r["longitude"]), 6),
            # Sea level where the gazetteer gives none: the honest default,
            # being the elevation of most of the planet and wrong by less than
            # any guess.
            elevation=float(r.get("elevation") or 0.0),
            # The zone NAME. An offset here would be today's, and today's is
            # not the one a birth in 1996 was under.
            timezone=r.get("timezone") or "",
            population=int(r.get("population") or 0),
        )

    return build(kept[0]), [build(r) for r in kept[1:4]]


@dataclass(frozen=True)
class Moment:
    """A local wall clock, and the instant it turns out to be."""

    when: str            # ISO-8601 WITH offset — what the ephemeris is sent
    offset: str          # +03:00
    abbreviation: str    # EEST
    note: str            # empty unless the clock did something that night


def at(place: Place, date: str, time: str) -> Moment:
    """
    The instant a local wall clock names, in that place, on that date.

    **This is the half a gazetteer cannot give.** Greece's offset in 1996 is
    not a lookup of today's rules, and sending a bare `1996-05-14T09:30:00` to
    the ephemeris does not mean "half past nine in Athens" — it means half past
    nine UTC, which is half past twelve in Athens and a different chart.

    Two clock oddities are reported rather than silently resolved, because a
    person born in one of them deserves to be told:

      - a time the clock SKIPPED, when it went forward over that hour. A birth
        certificate showing it needs checking.
      - a time the clock lived TWICE, when it went back. There are two real
        instants an hour apart and nothing here can choose between them.

    A gap and a fold both make the two `fold` readings disagree, so that test
    alone cannot tell them apart. The round trip separates them: normalise to
    UTC and back, and a fold returns the same wall clock while a gap does not.
    """
    try:
        zone = ZoneInfo(place.timezone) if place.timezone else ZoneInfo("UTC")
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise PlaceError(
            f"I do not know the timezone **{place.timezone}**, so I cannot place "
            "that moment in time."
        ) from exc

    try:
        naive = datetime.fromisoformat(f"{date}T{time}")
    except ValueError as exc:
        raise PlaceError("That date and time do not parse. Use `YYYY-MM-DD` and `HH:MM`.") from exc

    local = naive.replace(tzinfo=zone)
    offset = local.utcoffset() or timedelta(0)

    other = naive.replace(tzinfo=zone, fold=1)
    folds_differ = other.utcoffset() != offset
    imaginary = local.astimezone(ZoneInfo("UTC")).astimezone(zone).replace(tzinfo=None) != naive
    ambiguous = folds_differ and not imaginary

    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    stamp = f"{sign}{abs(minutes) // 60:02d}:{abs(minutes) % 60:02d}"

    return Moment(
        when=f"{naive.isoformat(timespec='seconds')}{stamp}",
        offset=stamp,
        abbreviation=local.tzname() or "",
        note=(
            "That local time never occurred there — the clock went forward over "
            "it. A birth certificate showing it is worth checking."
            if imaginary else
            "That local time happened twice that night — the clock went back, "
            "and the two instants are an hour apart. This is the first of them."
            if ambiguous else ""
        ),
    )
