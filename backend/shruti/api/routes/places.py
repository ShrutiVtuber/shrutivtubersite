# Place search, so nobody has to type coordinates.
"""
Resolving a city to an observer.

**Same source as theourgia**: Open-Meteo's geocoding API over the GeoNames
gazetteer. Reusing it rather than picking a second gazetteer means a place
resolved on the phone and the same place resolved here are the same place —
same coordinates, same elevation, same timezone name — instead of two products
quietly disagreeing about where Athens is.

Why that provider, from theourgia's own notes: no API key and no account, so
there is nothing to leak and nothing to expire; and it returns **elevation**,
which Nominatim does not. Altitude shifts a sunrise by about a minute per five
hundred metres, and the alternative was a second call to a second service or
asking a practitioner to guess how high up they live.

**One difference from the mobile app, deliberate.** There the device calls
Open-Meteo directly, because there is no server in between. Here there is, so
the call is made server-side and the visitor's IP never reaches the gazetteer.
The site already fetches everything this way; a place search is the one query
where the alternative would tell a third party what someone is looking up.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["places"])

GEOCODER = "https://geocoding-api.open-meteo.com/v1/search"

# Long enough to be worth waiting for, short enough to give up while the person
# still believes it is trying.
TIMEOUT = 8.0


@router.get("/places")
async def search_places(
    q: str = Query(..., min_length=2, max_length=120, description="City name"),
    limit: int = Query(8, ge=1, le=20),
) -> dict:
    """
    Cities matching a name, with everything an observer needs.

    Elevation defaults to sea level where the gazetteer does not give one —
    the honest default, being the elevation of most of the planet's surface and
    wrong by less than any guess.
    """
    params = {"name": q, "count": limit, "language": "en", "format": "json"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(GEOCODER, params=params)
    except httpx.HTTPError:
        # A gazetteer that cannot be reached is not a place that does not
        # exist, and the caller must be able to tell those apart.
        raise HTTPException(503, "the place index could not be reached")

    if response.status_code != 200:
        raise HTTPException(503, "the place index could not be reached")

    results = (response.json() or {}).get("results") or []
    places = []
    for entry in results:
        lat, lon = entry.get("latitude"), entry.get("longitude")
        name = entry.get("name")
        if lat is None or lon is None or not name:
            continue
        places.append({
            "name": name,
            "region": entry.get("admin1") or "",
            "country": entry.get("country") or "",
            "countryCode": entry.get("country_code") or "",
            "lat": round(float(lat), 6),
            "lon": round(float(lon), 6),
            "elevation": float(entry.get("elevation") or 0.0),
            # The IANA zone NAME, not an offset. The offset depends on the date
            # — Greece in 1996 is not Greece today — and only the name survives
            # that.
            "timezone": entry.get("timezone") or "",
            "population": int(entry.get("population") or 0),
        })

    return {"query": q, "count": len(places), "places": places}


@router.get("/places/offset")
async def timezone_offset(
    tz: str = Query(..., max_length=64, description="IANA zone name, e.g. Europe/Athens"),
    when: str = Query(..., description="Local date or datetime, e.g. 1996-05-14T09:30"),
) -> dict:
    """
    The offset that applied in a zone **on that date**, not today.

    This is the half of place-resolution that a gazetteer alone cannot give,
    and the one that matters for a nativity. Greece's offset in 1996 is not a
    lookup of today's rules, and a chart cast an hour out is wrong in a way
    that looks right: every planet is nearly correct and the ascendant is
    fifteen degrees off.

    Returns the offset and the zone abbreviation, plus whether the local time
    given is one that the clock skipped or repeated — a spring-forward gap, or
    an autumn hour lived twice. Both are real and both are the sort of thing
    someone born at 02:30 deserves to be told rather than have silently
    resolved.
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        raise HTTPException(400, f"unknown timezone {tz!r}")

    try:
        naive = datetime.fromisoformat(when)
    except ValueError:
        raise HTTPException(400, "when must be an ISO-8601 local date or datetime")
    if naive.tzinfo is not None:
        naive = naive.replace(tzinfo=None)

    local = naive.replace(tzinfo=zone)
    offset = local.utcoffset() or timedelta(0)

    # BOTH a spring-forward gap and an autumn fold make the two folds disagree,
    # so that comparison alone cannot tell them apart — it labelled 01:30 on 29
    # March 1981 in London as "occurred twice" when in fact the UK clock went
    # forward at 01:00 GMT and that minute never existed.
    #
    # The round trip is what separates them. Normalise to UTC and back: a fold
    # returns the same wall clock (it happened, twice), a gap does not (it never
    # showed).
    other = naive.replace(tzinfo=zone, fold=1)
    folds_differ = other.utcoffset() != offset
    imaginary = local.astimezone(ZoneInfo("UTC")).astimezone(zone).replace(tzinfo=None) != naive
    ambiguous = folds_differ and not imaginary

    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    return {
        "timezone": tz,
        "when": when,
        "offsetMinutes": minutes,
        "offset": f"{sign}{abs(minutes) // 60:02d}:{abs(minutes) % 60:02d}",
        "abbreviation": local.tzname() or "",
        "isDst": bool(local.dst()),
        "ambiguous": ambiguous,
        "imaginary": imaginary,
        "note": (
            "this local time never occurred — the clock went forward over it, "
            "so a birth certificate showing it needs checking"
            if imaginary else
            "this local time occurred twice that night — the clock went back, "
            "and the two are an hour apart"
            if ambiguous else ""
        ),
    }
