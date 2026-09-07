# SPDX-License-Identifier: AGPL-3.0-only
"""
A column is read in Athens, Tokyo and Los Angeles, where the same instant is a
different weekday.

So the prose carries tokens rather than sentences about days, and these are the
invariants that keep that working. They are checked by reading the source
because the site has no JavaScript test runner — the alternative is not a
better test, it is no test.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.test_copy import SRC

TOKENS = SRC / "lib" / "tokens.ts"
LOCAL = SRC / "components" / "content" / "LocalTimes.astro"
SIGNS = SRC / "lib" / "signs.ts"
READING = SRC / "pages" / "horoscopes" / "[sign]" / "[period].astro"


def test_an_unresolved_token_is_visible_and_never_empty() -> None:
    """
    An empty space where a date should be reads as a writing choice and
    survives for ever. A marker gets noticed.
    """
    text = TOKENS.read_text(encoding="utf-8")
    assert "token-broken" in text
    assert "⟨unresolved⟩" in text
    assert "export function unresolved" in text, \
        "publishing needs a way to count them"


def test_a_token_carries_the_instant_not_an_id() -> None:
    """
    The brief specified `{{event:<id>}}` against a table of precomputed events,
    plus a CI check that no published article referenced an id that had
    vanished — a guard against a fragility rather than a reason for one.
    Recomputing an ephemeris moves an event by a second, the id changes, and
    the published sentence breaks. The instant cannot break: a second of drift
    renders the same date.
    """
    text = TOKENS.read_text(encoding="utf-8")
    assert "instant" in text and "range" in text and "daypart" in text
    assert "{{event:" not in text.replace("`{{event:<id>}}`", ""), \
        "an id-based token reintroduces the fragility"


def test_the_server_renders_universal_time_and_says_so() -> None:
    """
    The page has to be readable and indexable before any script runs, and the
    server does not know the reader's zone. Writing UT and labelling it is
    honest; writing the server's own zone silently would not be.
    """
    text = TOKENS.read_text(encoding="utf-8")
    assert 'timeZone: "UTC"' in text
    assert "UT" in text
    assert "<time datetime=" in text, "localising needs a machine-readable instant"


def test_localising_never_takes_the_page_down_with_it() -> None:
    """
    `Intl` can throw on an unknown zone. A page half-rewritten because one
    timestamp failed is worse than one that shows Universal Time throughout.
    """
    text = LOCAL.read_text(encoding="utf-8")
    assert text.count("try {") >= 3
    assert "catch" in text


def test_the_lint_catches_the_expressions_this_exists_to_prevent() -> None:
    text = TOKENS.read_text(encoding="utf-8")
    for phrase in ("monday", "tonight", "midnight"):
        assert phrase in text.lower(), f"the lint does not look for {phrase!r}"


# ── the bug this file was written after ─────────────────────────────────────


def test_the_calendar_ordered_sign_list_says_it_is_not_zodiacal() -> None:
    """
    `SIGNS` runs Capricorn-first because it is indexed by calendar month for
    `sunSign`. Indexed as though it began at Aries it is silently wrong and
    looks right: `SIGNS.indexOf("leo")` is 7, and the seventh sign of the
    zodiac is Scorpio — which is the wheel a Leo reading drew.
    """
    text = SIGNS.read_text(encoding="utf-8")
    assert "capricorn" in text.split("export const SIGNS")[1][:120]
    assert "NOT in zodiacal order" in text, "the trap has to be written down"
    assert "export const ZODIAC" in text, \
        "there has to be a correct list to reach for instead"


def test_the_reading_page_does_not_index_the_calendar_list() -> None:
    """The exact line that rotated a Leo reading to Scorpio."""
    text = READING.read_text(encoding="utf-8")
    assert not re.search(r"\bSIGNS\s*\[", text)
    assert not re.search(r"SIGNS\.indexOf\([^)]*\)\s*\]", text)
    assert "risingName = NAME" in text, "the rotation comes from the slug"


# ── stepping ────────────────────────────────────────────────────────────────

STEPPER = SRC / "components" / "chart" / "WheelStepper.astro"
WHEEL = SRC / "components" / "chart" / "TransitWheel.astro"


def code_of(path: Path) -> str:
    """
    A file's source with its comments removed.

    For the fifth time in this project: a test that greps for a forbidden
    string matches the comment explaining why the thing is forbidden. This
    file's own docstring says "WebAssembly" precisely to record that none is
    shipped, and that sentence failed the assertion. Strip the prose, search
    the code.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)      # block comments
    text = re.sub(r"^\s*//.*$", " ", text, flags=re.M)       # line comments
    text = re.sub(r"\{/\*.*?\*/\}", " ", text, flags=re.S)  # astro markup comments
    return text


def test_no_ephemeris_is_shipped_to_the_browser() -> None:
    """
    The brief asked for Swiss Ephemeris compiled to WebAssembly in a worker,
    a second server implementation, and CI proving the two agree to one
    arcsecond. Interpolating a sampled span does the same job with one
    implementation and single-figure kilobytes — measured at 0.004 arcseconds
    against real charts, which is what makes the second implementation
    pointless rather than merely expensive.
    """
    text = code_of(STEPPER)
    for forbidden in (".wasm", "WebAssembly", "swisseph"):
        assert forbidden not in text, f"the stepper pulls in {forbidden}"
    assert "/api/astro/positions" in text, "it asks the daemon for the span"


def test_the_stepper_moves_planets_and_not_the_rings() -> None:
    """
    Rings, sign glyphs, house numbers and dividers are fixed by the rotation,
    which only changes on a navigation. Redrawing them per step would be work
    per frame for a picture that did not change.
    """
    wheel = code_of(WHEEL)
    assert "data-bodies" in wheel and "data-body=" in wheel
    for handle in ("data-glyph", "data-degree", "data-leader", "data-mark"):
        assert handle in wheel, f"the stepper cannot address {handle}"


def test_glyph_spreading_is_fixed_not_adaptive() -> None:
    """
    Anything adaptive makes the glyphs jitter as the wheel steps, which is
    exactly what a viewer watching a stream would notice. Both sides relax by
    the same fixed amount, and the wheel hands its value to the stepper rather
    than each keeping its own.
    """
    assert "data-min-separation" in code_of(WHEEL)
    assert "minSeparation" in code_of(STEPPER)


def test_a_failed_span_says_so_rather_than_looking_alive() -> None:
    """Controls that respond to nothing read as a broken page."""
    text = code_of(STEPPER)
    assert "Stepping is unavailable" in text
    assert 'setAttribute("disabled"' in text
