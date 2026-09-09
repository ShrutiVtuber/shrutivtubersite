# SPDX-License-Identifier: AGPL-3.0-only
"""
Correcting something already published.

Her ask: fix a spelling in a reading that is already on the site, and have the
fix "subtly marked so people can see and track the edit history".

Both halves are load-bearing. A reading nobody may correct grows typos. A
reading that can be silently rewritten is not a record of what she said that
week — it is whatever she thinks now, wearing that week's date. So the old words
are kept, and the reading says it was edited and links to them.

The decision about WHAT gets filed is tested here directly. Filing too much is
as bad as filing too little: the desk autosaves, and a history full of identical
versions hides the one correction somebody came to see.
"""
from __future__ import annotations

import pytest

from shruti.api.routes.horoscopes import is_a_correction


def test_editing_a_draft_files_nothing() -> None:
    """Writing is not correcting, and nobody has been misled yet."""
    assert is_a_correction(False, "first words", "second words") is False


def test_fixing_a_published_reading_is_filed() -> None:
    assert is_a_correction(True, "with a teh typo", "with the typo fixed") is True


def test_the_autosave_does_not_fill_the_history() -> None:
    """
    The desk saves as she thinks, so the same words arrive over and over. Each
    one filed would be a version identical to the last, and the real correction
    would be somewhere in the middle of them.
    """
    assert is_a_correction(True, "the same words", "the same words") is False
    assert is_a_correction(False, "the same words", "the same words") is False


@pytest.mark.parametrize("was,now", [
    ("", "the first published words"),      # published empty, then written
    ("something", ""),                       # emptied after publishing
    ("a", "b"),
])
def test_any_real_change_after_publishing_is_filed(was: str, now: str) -> None:
    assert is_a_correction(True, was, now) is True


def test_the_route_uses_the_decision_rather_than_its_own_condition() -> None:
    """
    The rule lived inline before it was named, and an inline condition is one
    somebody edits without noticing what it decides.
    """
    import inspect

    from shruti.api.routes import horoscopes

    source = inspect.getsource(horoscopes.save_draft)
    assert "is_a_correction(" in source, (
        "save_draft no longer asks is_a_correction — the rule has been inlined "
        "again and these tests now prove nothing about what the route does"
    )
