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
