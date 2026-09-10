# SPDX-License-Identifier: AGPL-3.0-only
"""
A comment can be about one reading of a set, or about the set.

Her words: readers need to pick "which of the multiple readings they are
reading and commenting on, or they can do so on the whole collection".

⚠ **Empty means the whole set, and that is a VALUE, not a missing one.** "This
hangs together as a series" is a real thing to say about twelve signs and is
not a thing to say about Aries. Which is why a reader looking at one sign is
shown that sign's remarks AND the set's: filtering the set's out would bury the
most useful thing anybody says about a series behind a tab nobody presses.

⚠ **Discord cannot nest threads.** A thread hangs off a message in a channel; a
message inside a thread cannot have one of its own. So the per-reading
conversation is made of REPLIES inside one thread, and `practice_bridge.sign`
is the only thing that says which reading a reply answers. Everything about the
shape of this feature follows from that limit — see the migration.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from conftest import ROOT, SITE

from shruti.api.routes import practice
from shruti.models.practice import PracticeBridge, PracticeComment


PAGE = SITE / "src" / "pages" / "practice" / "[id].astro"


def test_a_comment_and_a_bridge_message_can_both_name_a_reading() -> None:
    assert "sign" in PracticeComment.model_fields, (
        "a comment cannot say which reading it is about"
    )
    assert "sign" in PracticeBridge.model_fields, (
        "a Discord message cannot say which reading it carries, so every reply "
        "in the thread lands on the whole set"
    )


def test_the_sign_is_checked_against_the_work() -> None:
    """
    ⚠ It is free text arriving from outside.

    A remark filed under "aeries" is one nothing will ever show: it is not the
    set, and it is not any sign the reader can select. It would sit in the
    database looking like it worked.
    """
    source = inspect.getsource(practice._sign_of)
    assert "PracticeReading" in source, (
        "the sign is not checked against the readings the work actually has"
    )
    assert 'return ""' in source, (
        "an unrecognised sign should fall back to the whole set — losing the "
        "label is survivable, losing the remark is not"
    )


def test_both_doors_check_it() -> None:
    """The site's comment box and the Discord bridge are two ways in."""
    for name in ("comment", "bridge_message"):
        source = inspect.getsource(getattr(practice, name))
        assert "_sign_of(" in source, f"{name} takes a sign without checking it"


def test_a_bridged_reply_takes_the_sign_of_what_it_answered() -> None:
    """
    ⚠ From the MESSAGE, never from the reply's text.

    Somebody answering the Taurus message in the thread is talking about
    Taurus whatever they typed. Reading a sign out of the reply would mean
    asking them to repeat what Discord already knows, and getting it wrong
    whenever they did not.
    """
    source = inspect.getsource(practice.bridge_comment)
    assert "sign=link.sign" in source, (
        "a reply from Discord does not inherit the sign of the message it "
        "answered, so every reply lands on the whole set"
    )


def test_the_work_json_says_which_reading_each_remark_answers() -> None:
    source = inspect.getsource(practice)
    assert '"sign": c.sign or ""' in source, (
        "the app and the site are never told which reading a remark is about"
    )


def test_the_page_shows_the_set_s_remarks_under_every_sign() -> None:
    """
    ⚠ The one rule that is easy to get backwards.

    Filtering strictly by the chosen sign hides every remark about the series,
    on every tab, with nothing to show it happened.
    """
    page = PAGE.read_text(encoding="utf-8")
    assert re.search(r'!==\s*sign\s*&&\s*\S+\.dataset\.said\s*!==\s*"all"', page), (
        "remarks about the whole set are hidden when a sign is chosen"
    )


def test_the_page_can_still_answer_the_whole_set() -> None:
    """A tab for every sign and no way to answer the series is a dead end."""
    page = PAGE.read_text(encoding="utf-8")
    assert 'data-about' in page, "no control for choosing what a remark answers"
    assert re.search(r'<option value=""', page), (
        "the whole set is not offered, so a remark about the series has "
        "nowhere to go"
    )


def test_arriving_at_a_practice_link_does_not_scroll_past_the_title() -> None:
    """
    ⚠ Discord links straight here.

    Writing the fragment during the first paint sends the browser to that
    anchor, and somebody opening the link landed three hundred pixels down,
    past the title and the writer's name. The fragment is still written when a
    tab is pressed, so a sign stays linkable.
    """
    page = PAGE.read_text(encoding="utf-8")
    assert "if (remember) history.replaceState" in page, (
        "the fragment is written unconditionally, so arriving at the page "
        "scrolls past its own title"
    )
