# SPDX-License-Identifier: AGPL-3.0-only
"""
Guide overlays: six elements, three skins, one layout — and the four state
colours are a constant a theme may not touch.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import overlay_guides as og

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "site" / "src"
CSS = (SRC / "styles" / "overlay-guides.css").read_text(encoding="utf-8")
PAGES = {k: (SRC / "pages" / "overlay" / f"{k}.astro").read_text(encoding="utf-8") for k in og.GUIDE_KINDS}
LAYOUT = PAGES["guide-layout"]


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def without_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


# ── a theme is a skin; the state vocabulary is a constant ───────────────────

def test_the_state_colours_are_defined_once_outside_every_theme() -> None:
    css = without_comments(CSS)
    assert css.count("--st-done:") == 1 and css.count("--st-now:") == 1
    blocks = re.findall(r'\.gov\[data-theme="[a-z]+"\]\s*\{([^}]*)\}', css)
    assert len(blocks) == 3, "three themes: almanac, grimoire, plain"
    for block in blocks:
        assert "--st-" not in block, "a theme redefined a state colour"
    assert "#E0A4BC" in css and "#8FBEE8" in css        # rose done, blue current — everywhere


def test_the_dots_differ_in_shape_as_well_as_colour() -> None:
    css = without_comments(CSS)
    assert ".dot.done" in css and "height: 6px" in css             # the dash
    assert ".dot.current" in css and ".dot.available" in css and ".dot.locked" in css
    assert "border: 5px solid var(--st-open)" in css                # the ring, 5px at 1080p


def test_the_ignite_is_three_pixels_on_stream() -> None:
    """At 720p a 1.5px rose line disappears; the whole event survives a viewer's bitrate."""
    assert "border: 3px solid var(--st-done)" in CSS


def test_motion_is_the_overlays_own_setting_and_there_is_no_sound() -> None:
    assert '.gov[data-motion="still"] *' in CSS and '.gov[data-motion="reduced"] .swap' in CSS
    for kind, page in PAGES.items():
        assert 'data-motion={motion}' in page, kind
        assert "Audio" not in page and "vibrate" not in page, kind


def test_the_done_moment_keeps_its_timings_on_stream() -> None:
    page = PAGES["guide-now"]
    assert "await wait(260)" in page and "await wait(80)" in page and "await wait(100)" in page
    assert "600ms" in CSS and "300ms" in CSS
    assert "Done · ${prev.id}" in page                              # the reduced-motion twin's one line


# ── never blank, never "connecting" ─────────────────────────────────────────

def test_an_overlay_never_blanks_and_never_says_waiting() -> None:
    for kind, page in PAGES.items():
        assert "No run selected." in page, kind
        assert "if (!r.ok) return;" in page, kind                   # held, not blanked
        low = without_comments(page).lower()
        assert "waiting" not in low and "connecting" not in low, kind


def test_a_token_whose_run_is_gone_answers_an_empty_frame() -> None:
    body = code_of(og.guide)
    assert "if run is None:\n        return base" in body
    assert 'raise HTTPException(404, "no such overlay")' in body     # an unknown token is 404, not 403


# ── the token is the secret ─────────────────────────────────────────────────

def test_the_token_is_readable_once_when_minted() -> None:
    assert '"token": token' in code_of(og.mint_token)
    listed = code_of(og.list_tokens)
    assert '"token"' not in listed and "o.token" not in listed


def test_tokens_belong_to_the_runs_owner() -> None:
    body = code_of(og._mine)
    assert "run.user_id != user.id" in body and "404" in body and "403" not in body
    assert "row.run_id != run.id" in code_of(og.rebind_token)
    assert "await session.delete(row)" in code_of(og.revoke_token)


def test_each_element_carries_only_what_it_draws() -> None:
    """Computed by the shared function, so a self-hosted overlay draws the same thing."""
    from shrutisguides import progress
    assert "progress.element(token.kind, _stored(run), v.body, token.routine_id)" in code_of(og.guide)
    body = code_of(progress.element)
    assert 'if kind == "guide-now":' in body and '"finished"' in body
    assert 'path[max(0, i - 2): i + 4]' in body                      # the six-item window
    assert "engine.sigil_parts" in body


def test_a_layout_is_several_elements_in_one_source_placed_on_the_canvas() -> None:
    """Positions come from the layout; a theme may never move them."""
    from shrutisguides import progress
    assert "guide-layout" in progress.GUIDE_KINDS and "guide-layout" not in progress.ELEMENT_KINDS
    assert set(progress.DEFAULT_PLACES) == set(progress.ELEMENT_KINDS)
    cleaned = progress.clean_layout([{"kind": "guide-now", "x": -50, "y": 5000, "w": 10}, {"kind": "nope"}])
    assert cleaned == [{"kind": "guide-now", "x": 0, "y": 1080, "w": 120, "routine_id": "", "shows": "", "group": "", "counter_id": 0, "text": "", "url": ""}]
    # A picture is loaded from https only: a browser source must never load a file or a script.
    assert progress.clean_layout([{"kind": "image", "url": "file:///etc/passwd"}])[0]["url"] == ""
    assert progress.clean_layout([{"kind": "image", "url": "https://example.org/a.png"}])[0]["url"] == "https://example.org/a.png"
    assert "progress.layout_elements(" in code_of(og.guide)
    assert 'left:${e.x}px;top:${e.y}px;width:${e.w}px' in LAYOUT
