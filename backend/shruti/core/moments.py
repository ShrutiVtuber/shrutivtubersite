# SPDX-License-Identifier: AGPL-3.0-only
"""
Turning birth data into an instant.

**One function, because there used to be seven.** The natal tool, the chart
figure, the print page, both comparison pages and the synastry route each built
`f"{date}T{time}:00"` for themselves, and every one of them was wrong in the
same way: the ephemeris reads a datetime with no offset as UTC. A birth at half
past nine in Athens was cast for half past twelve there.

What makes it hard to catch is that it does not look wrong. The planets move
slowly enough that all of them stay very nearly right; only the angles move.
Athens comes out 37° off, Mumbai 76°, Los Angeles 127° — a chart with the wrong
rising sign, the wrong houses and the right Sun, which is indistinguishable
from a correct chart unless you already know the answer.

So the arithmetic lives here, once, and every caller asks for it.

**The zone NAME is the thing worth storing, never the offset.** Greece was
+02:00 in January 1996 and +03:00 in May, and the rules themselves have been
rewritten repeatedly across the span of dates a nativity can name. Only
`Europe/Athens` survives that; `+03:00` is an answer to one question about one
date and is silently wrong about every other.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Noon when the birth time is unknown: the least-wrong instant for the planets.
# Everything that depends on the ascendant is withheld by the caller rather
# than computed from this, because with no time those are undefined and not
# merely imprecise.
NOON = "12:00"


class UnknownZone(ValueError):
    """The IANA zone name is not one this system knows."""


@dataclass(frozen=True)
class Offset:
    """What a wall clock in one zone meant on one date."""

    minutes: int
    label: str                 # +03:00
    abbreviation: str          # EEST
    is_dst: bool
    ambiguous: bool            # the clock lived this hour twice
    imaginary: bool            # the clock skipped this hour entirely
    note: str


def offset_at(tz: str, when_local: str) -> Offset:
    """
    The offset that applied in a zone ON THAT DATE, not today.

    Two clock oddities are reported rather than silently resolved, because a
    person born inside one of them deserves to be told:

      - a local time the clock SKIPPED, going forward over it. A birth
        certificate showing it needs checking against something else.
      - a local time the clock lived TWICE, going back. There are two real
        instants an hour apart and nothing here can choose between them.

    A gap and a fold BOTH make the two `fold` readings disagree, so that
    comparison alone cannot tell them apart — it once labelled 01:30 on 29
    March 1981 in London as "occurred twice" when in fact the clock went
    forward at 01:00 GMT and that minute never existed. The round trip is what
    separates them: normalise to UTC and back, and a fold returns the same wall
    clock while a gap does not.
    """
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise UnknownZone(f"unknown timezone {tz!r}") from exc

    naive = datetime.fromisoformat(when_local)
    if naive.tzinfo is not None:
        naive = naive.replace(tzinfo=None)

    local = naive.replace(tzinfo=zone)
    offset = local.utcoffset() or timedelta(0)

    other = naive.replace(tzinfo=zone, fold=1)
    folds_differ = other.utcoffset() != offset
    imaginary = local.astimezone(ZoneInfo("UTC")).astimezone(zone).replace(tzinfo=None) != naive
    ambiguous = folds_differ and not imaginary

    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    return Offset(
        minutes=minutes,
        label=f"{sign}{abs(minutes) // 60:02d}:{abs(minutes) % 60:02d}",
        abbreviation=local.tzname() or "",
        is_dst=bool(local.dst()),
        ambiguous=ambiguous,
        imaginary=imaginary,
        note=(
            "this local time never occurred — the clock went forward over it, "
            "so a birth certificate showing it needs checking"
            if imaginary else
            "this local time occurred twice that night — the clock went back, "
            "and the two are an hour apart"
            if ambiguous else ""
        ),
    )


def birth_moment(birth_date: str, birth_time: str | None,
                 time_unknown: bool, timezone: str) -> str:
    """
    The instant to send the ephemeris, offset and all.

    **Never returns a naive string.** A datetime with no offset is the bug this
    module exists to prevent, and one that leaves here without an offset would
    be read as UTC by the daemon and produce a plausible chart for the wrong
    moment.

    With no zone recorded it says `+00:00` explicitly rather than staying
    silent about it. That is the same instant a naive string would have
    produced, so nothing changes for a chart saved before zones were kept — but
    it is now visible in the URL and in this return value, instead of being an
    assumption nobody could see. `timezone_known()` is what callers use to warn
    about those, and it is why the field is exposed to the pages.
    """
    clock = NOON if time_unknown or not birth_time else birth_time
    if len(clock) == 5:                                   # HH:MM
        clock = f"{clock}:00"

    if not timezone:
        return f"{birth_date}T{clock}+00:00"

    try:
        offset = offset_at(timezone, f"{birth_date}T{clock}")
    except (UnknownZone, ValueError):
        # A zone we cannot resolve is not a reason to fall back to a naive
        # string; it is a reason to be explicit about what was assumed.
        return f"{birth_date}T{clock}+00:00"
    return f"{birth_date}T{clock}{offset.label}"


def timezone_known(timezone: str) -> bool:
    """Whether a chart carries a birthplace zone, so a page can say if not."""
    if not timezone:
        return False
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        return False
    return True
