# SPDX-License-Identifier: AGPL-3.0-only
"""
The track view (board W4): one step is the page, Done is the largest thing
on it, Too much replaces the whole page, and nothing measures absence.

Source-level guards over the page and its client module.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "site" / "src"
PAGE = (SRC / "pages" / "guides" / "[game]" / "[slug]" / "track.astro").read_text(encoding="utf-8")
APP = (SRC / "lib" / "track.ts").read_text(encoding="utf-8")


def without_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def test_the_page_is_for_the_signed_in_person_only() -> None:
    assert "return Astro.redirect(`/signin?next=" in PAGE
    assert "noindex" in PAGE
    assert re.search(r"/\^\[a-z0-9-\]\{1,80\}\$/\.test\(game\)", PAGE)


def test_the_words_come_from_the_page_not_the_script() -> None:
    assert "data-words={JSON.stringify(WORDS)}" in PAGE
    app = without_comments(APP)
    assert 'JSON.parse(root.dataset.words' in app
    assert not re.search(r"\{\s*say\(", app)
    # No English literal a reader sees is built in the module: labels are W.*
    for phrase in ("Done", "Later", "Check in", "Too much", "Skip nothing"):
        assert f'"{phrase}"' not in app, phrase


def test_the_path_beside_now_is_the_persons_choice() -> None:
    """Her decision: let them decide for themselves whether it is collapsed."""
    app = without_comments(APP)
    assert 'localStorage.getItem(collapsedKey)' in app and 'localStorage.setItem(collapsedKey' in app
    assert 'W.path.show' in app and 'W.path.hide' in app


def test_the_done_moment_is_the_one_motion_and_collapses_to_nothing() -> None:
    app = without_comments(APP)
    assert 'card.classList.add("ignite")' in app and 'card.classList.add("collapse")' in app and 'classList.add("unfold")' in app
    assert 'window.matchMedia("(prefers-reduced-motion: reduce)")' in app
    assert "W.now.doneWord" in app                       # the twin's one line: Done · P2.7
    assert "prefers-reduced-motion: reduce" in PAGE      # and the CSS honours it
    assert "600ms" in PAGE and "300ms" in PAGE and "80ms" in PAGE and "100ms" in PAGE


def test_nothing_measures_absence() -> None:
    # ⚠ Whole words: "dismissed" contains "missed", and the re-entry block IS dismissed.
    for text in (without_comments(PAGE).lower(), without_comments(APP).lower()):
        for word in (r"\bstreaks?\b", r"\bdays ago\b", r"\bmissed\b", r"% done", r"\bpercent\b"):
            assert not re.search(word, text), word


def test_nothing_is_applied_silently() -> None:
    app = without_comments(APP)
    assert "openProposal(proposals)" in app               # a check-in that produces proposals asks
    assert 'name="step" value=' in app and "checked" in app
    assert "W.proposal.nothing" in app and "W.proposal.mark" in app
    assert "/accept" in app


def test_the_checkin_shows_only_declared_fields_and_names_the_hidden_ones() -> None:
    app = without_comments(APP)
    assert "view.checkinShown?.[f.id]" in app
    assert "W.checkin.appears" in app


def test_too_much_replaces_the_page_and_counts_nothing() -> None:
    app = without_comments(APP)
    assert 'much.hidden = false' in app and "W.much.playing" in app and "W.much.finished" in app
    assert "Audio" not in app and "vibrate" not in app


def test_a_new_run_starts_with_a_proposal_not_a_skip() -> None:
    app = without_comments(APP)
    assert "/api/runs/skip-proposal?guide=" in app
    assert "W.newRun.skipN" in app and "W.proposal.nothing" in app
    assert 'say("new.promise", "Your answer becomes a proposal on the next screen. Nothing is skipped without you seeing the list.")' in PAGE


def test_the_state_dots_differ_in_shape_not_only_colour() -> None:
    for cls in ("dot.dash", "dot.disc", "dot.ring", "dot.hollow"):
        assert cls in PAGE
