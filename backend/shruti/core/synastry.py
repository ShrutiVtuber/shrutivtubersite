# SPDX-License-Identifier: AGPL-3.0-only
"""
What the tradition says about two charts, said as a reading.

**This is not a prediction and the site must never let it read as one.** Every
sentence here describes what classical practice attaches to a configuration
that is actually present — it does not say what will happen, and /terms says
plainly that nothing on this site claims predictive validity. The reading is
generated from arithmetic; the meaning is somebody's tradition, and the
authorities within it disagree with each other constantly.

So the design rule is: **report, attribute, and count. Never score.**

A percentage would be the dishonest thing. It looks like a measurement, it
compresses a dozen incompatible judgments into one number, and it invites the
reader to believe a machine has weighed their relationship. A TALLY is honest —
"the tradition counts six harmonious and three hard configurations here" is
simply true, is fun, and survives being screenshotted.
"""
from __future__ import annotations

# Classical natures. Sect changes which malefic is worse and which benefic is
# better, and this deliberately does not model that: doing it properly needs a
# day/night judgment for BOTH charts, and doing it badly would be worse than
# leaving it out and saying so.
BENEFIC = {"Venus", "Jupiter"}
MALEFIC = {"Mars", "Saturn"}
LUMINARY = {"Sun", "Moon"}

HARMONIOUS = {"trine", "sextile"}
HARD = {"square", "opposition"}

# The contacts practice actually looks at first, in the order it looks at them.
# Each is a pair of bodies and what the tradition attaches to it — phrased as
# what the tradition says, never as what is true of the people.
MARKERS: list[tuple[frozenset[str], str, str]] = [
    (frozenset({"Sun", "Moon"}), "Luminaries in contact",
     "The oldest marker in the book. Where one chart's Sun meets the other's "
     "Moon, the tradition reads a natural legibility — each recognising "
     "something the other lives by."),
    (frozenset({"Venus", "Mars"}), "Venus and Mars",
     "Classically the marker of attraction rather than of ease. The tradition "
     "is clear that it says nothing about whether a thing lasts."),
    (frozenset({"Moon", "Venus"}), "Moon and Venus",
     "Read as comfort — the pair the tradition associates with liking someone's "
     "company rather than being struck by them."),
    (frozenset({"Sun", "Saturn"}), "Sun and Saturn",
     "Weight. The tradition reads duty, seniority and the sense of being "
     "measured — difficult in the hard aspects, steadying in the soft ones."),
    (frozenset({"Moon", "Saturn"}), "Moon and Saturn",
     "The tradition's classic marker of a relationship that asks something of "
     "you. Not a bad one; a heavy one."),
    (frozenset({"Sun", "Jupiter"}), "Sun and Jupiter",
     "Read as generosity and enlargement — the pair most authorities treat as "
     "straightforwardly fortunate."),
    (frozenset({"Moon", "Mars"}), "Moon and Mars",
     "Friction, in the hard aspects especially. The tradition reads a quickness "
     "to feeling that can be warmth or can be temper."),
    (frozenset({"Mercury", "Mercury"}), "Mercury to Mercury",
     "Whether you think alike. The tradition treats this as the marker for "
     "conversation rather than for feeling."),
]

ANGLES = {"Ascendant", "Midheaven"}


def _body(raw: str) -> str:
    """`A Sun` -> `Sun`."""
    return raw[2:] if raw[:2] in ("A ", "B ") else raw


def _tone(aspect: str, a: str, b: str) -> str:
    """
    Harmonious, hard, or neither — by the classical rule.

    A conjunction is neither in itself: it takes the nature of what is
    conjunct. Venus conjunct anything is read kindly; Saturn conjunct anything
    is not. Treating every conjunction as good is the commonest way software
    gets this wrong.
    """
    if aspect in HARMONIOUS:
        return "harmonious"
    if aspect in HARD:
        return "hard"
    if aspect == "conjunction":
        bodies = {a, b}
        if bodies & MALEFIC and not bodies & BENEFIC:
            return "hard"
        if bodies & BENEFIC and not bodies & MALEFIC:
            return "harmonious"
    return "neither"


def read(by_degree: list[dict], left: str, right: str) -> dict:
    """
    A reading of the degree-based configurations.

    Degree-based rather than whole-sign: a reading built on the sign list would
    name eighty contacts and mean nothing. The tighter list is what an
    astrologer would actually talk about.
    """
    tally = {"harmonious": 0, "hard": 0, "neither": 0}
    found: list[dict] = []
    seen: set[frozenset[str]] = set()

    for cross in by_degree:
        a, b = _body(cross["from"]), _body(cross["to"])
        aspect = cross.get("aspect", "")
        tone = _tone(aspect, a, b)
        tally[tone] += 1

        pair = frozenset({a, b})
        for marker, title, says in MARKERS:
            if pair != marker or pair in seen:
                continue
            seen.add(pair)
            # Which chart contributed which body, so the sentence can name
            # people rather than letters.
            first = left if cross["from"].startswith("A ") else right
            second = right if cross["from"].startswith("A ") else left
            found.append({
                "title": title,
                "says": says,
                "aspect": aspect,
                "tone": tone,
                "detail": f"{first}'s {a} {aspect} {second}'s {b}",
                "orb": cross.get("orb"),
            })

    angles = [
        c for c in by_degree
        if _body(c["from"]) in ANGLES or _body(c["to"]) in ANGLES
    ]

    return {
        "tally": tally,
        "markers": found,
        "angleContacts": len(angles),
        # The one-line thing somebody screenshots. A count, never a score.
        "headline": _headline(tally, found),
        # Shorter, for the share card — where the tally is already drawn large
        # and repeating it in the headline both truncates and says it twice.
        "cardHeadline": found[0]["title"] if found else "Almost nothing in contact",
        "caveats": [
            "This describes what classical practice attaches to configurations "
            "that are present. It is not a prediction, and no claim of "
            "predictive validity is made for any of it.",
            "Sect — whether each chart is a day or a night birth — changes "
            "which benefic and which malefic the tradition reads as stronger. "
            "It is not modelled here, and a practitioner would want it.",
            "The authorities disagree with each other about most of this, and "
            "always have.",
        ],
    }


def _headline(tally: dict, markers: list[dict]) -> str:
    h, x = tally["harmonious"], tally["hard"]
    total = h + x
    if total == 0:
        return "Almost nothing in contact — which is its own answer."
    if markers:
        return f"{markers[0]['title'].lower()}, and {h} harmonious to {x} hard"
    return f"{h} harmonious to {x} hard"
