# SPDX-License-Identifier: AGPL-3.0-only
"""
The page editor: /admin/preview.

Three faults were reported together, and they turned out to be one fault and
two gaps.

The fault: clicking anything in the preview navigated the iframe. That alone
would be annoying; what made it look broken was the second-order effect. Every
navigation fires `load`, `load` re-runs the panel reorder, and the reorder only
ever APPENDED its "N not visible on this page" heading — so the panel filled up
with the notice, over and over, with different counts because each one had been
counted against a different page. Her screenshot shows eight of them.

It also meant "Sign out" was a live link inside the preview.

The gaps: a button's label could not be reached, because the click that would
select it activated it instead; and a block's image could not be set at all,
because the panel edited four text fields and `media_id` was not among them.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[2] / "frontend" / "site" / "src"


SRC = _src()
PREVIEW = SRC / "pages" / "admin" / "preview.astro"


def code_of(path: Path) -> str:
    """Source without comments — this file's own prose names the very strings
    it checks for, and so does the page's."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)//.*$", " ", text)


def test_the_editor_is_there():
    assert PREVIEW.is_file(), "the preview editor is missing"


# ── the notice that multiplied ───────────────────────────────────────────────

def test_the_not_visible_heading_is_cleared_before_it_is_written():
    """
    Otherwise every iframe load leaves another copy behind.

    The reorder runs on `load`, and `load` happens more than once — a page
    change, a save that reloads the frame, and (until it was stopped) every
    link click.
    """
    code = code_of(PREVIEW)
    assert re.search(r'querySelectorAll\("\.not-here"\)', code), (
        "the previous heading must be removed before a new one is appended"
    )
    remove_at = code.index("not-here")
    create_at = code.index("not-here", remove_at + 1)
    assert remove_at < create_at, (
        "the removal has to come before the append, or it clears the new one"
    )


# ── nothing in the preview navigates ─────────────────────────────────────────

def test_clicks_are_stopped_before_a_field_is_looked_for():
    """
    The old handler called preventDefault only AFTER finding a panel entry, so
    every link the panel did not know about still worked — the nav, a card, and
    Sign out.
    """
    code = code_of(PREVIEW)
    handler = code[code.index("function wireFrame"):]
    guard = handler.index('closest?.("a,button')
    matching = handler.index("for (const box of panel.querySelectorAll")
    assert guard < matching, (
        "navigation must be prevented before the panel is searched, not after"
    )


def test_form_submission_and_middle_click_are_stopped_too():
    """A form posts and a middle click opens a tab; neither is a plain click."""
    code = code_of(PREVIEW)
    assert '"submit"' in code and '"auxclick"' in code


def test_a_wrapper_around_an_image_counts_as_the_image():
    """
    Every picture on this site is a <picture>, whose box is bigger than the
    <img> in it — so a click aimed at a photograph often lands on the wrapper.
    Matching only `img` made those clicks do nothing at all, silently.
    """
    assert 'closest?.("img,picture,figure")' in code_of(PREVIEW)


def test_a_click_with_nowhere_to_go_says_so():
    """Silence reads as breakage: the link visibly did not fire, so something
    happened, and nothing moved."""
    code = code_of(PREVIEW)
    assert "not editable from this panel" in code


# ── pictures ─────────────────────────────────────────────────────────────────

def test_a_block_can_be_given_a_picture():
    code = code_of(PREVIEW)
    assert 'class="pic"' in code, "every block needs the image control"
    assert 'type="file"' in code, "including one with no image yet"


def test_uploading_writes_the_file_before_pointing_the_block_at_it():
    """
    Two writes, in this order. Reversed, a failed upload leaves a block
    referring to a media row that does not exist.
    """
    code = code_of(PREVIEW)
    up = code.index('"/api/admin/media"')
    assign = code.index("/api/admin/sections/${pic.dataset.block}")
    assert up < assign


def test_alt_text_is_saved_to_the_image_not_the_block():
    """The same picture used on two pages describes itself the same way."""
    code = code_of(PREVIEW)
    assert "/api/admin/media/${t.dataset.media}" in code
    assert "alt_text" in code


def test_removing_a_picture_sends_null():
    code = code_of(PREVIEW)
    assert "media_id: m ? m.id : null" in code


def test_the_panel_says_when_a_picture_has_nowhere_to_render():
    """
    Not every template shows a block's image — the home page hands its blocks
    to SupportBand, which has no picture in it. Without this the image saves,
    nothing changes on the page, and there is no way to tell whether the upload
    failed, the page is cached, or the template simply has no place for it.
    """
    code = code_of(PREVIEW)
    assert "pic-unused" in code
    # The note used to say "block image". Blocks were the only pictures the
    # panel could set; it now sets a content row's picture and a copy string
    # that holds one, so the wording covers all three.
    assert "does not show this picture" in code
