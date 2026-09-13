# SPDX-License-Identifier: AGPL-3.0-only
"""
Her side of Shruti's Guides: the queue, the reports, the switches, and the
channel being told.

Source-level guards, as everywhere in this suite.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import guides

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "site" / "src"
QUEUE = (SRC / "pages" / "admin" / "guides.astro").read_text(encoding="utf-8")
REVIEW = (SRC / "pages" / "admin" / "guides" / "[version].astro").read_text(encoding="utf-8")


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def without_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


# ── the channel is told ──────────────────────────────────────────────────────

def test_publishing_tells_the_channel_after_the_commit() -> None:
    """A Discord outage must not fail her publish."""
    body = code_of(guides.publish)
    assert body.index("await session.commit()") < body.index("await _tell_discord(")


def test_the_channel_hears_fields_not_rows() -> None:
    """Built field by field so nothing about a reader ever reaches the bot."""
    body = code_of(guides.publish)
    window = body[body.index("await _tell_discord("):]
    for field in ('"id"', '"title"', '"game"', '"author"', '"steps"', '"isUpdate"'):
        assert field in window
    assert "model_dump" not in window and "__dict__" not in window


def test_the_bridge_is_optional_and_never_raises() -> None:
    body = code_of(guides._tell_discord)
    assert "VCORDBOT_INTERNAL_URL" in body and "SHRUTI_INTERNAL_SECRET" in body
    assert "return" in body.split("try:")[0]          # unconfigured is a working state
    assert "except Exception" in body
    assert "/internal/guides" in body


def test_an_update_is_known_before_the_pointer_moves() -> None:
    body = code_of(guides.publish)
    assert body.index("was_update = ") < body.index("g.published_version_id = v.id")


# ── her decisions settle the reports ─────────────────────────────────────────

def test_hiding_or_restoring_settles_the_open_reports() -> None:
    body = code_of(guides.hide)
    assert '"upheld" if body.hidden else "dismissed"' in body
    # Both branches, not only the restore.
    assert "if not body.hidden:" not in body


def test_the_admin_list_groups_reports_by_the_guide() -> None:
    body = code_of(guides.admin_guides)
    assert "by_guide" in body
    assert '"reasons": reasons' in body
    assert "GuideReport.reviewed_at.is_(None)" in body


# ── the pages ────────────────────────────────────────────────────────────────

def test_publishing_happens_on_the_reading_page_not_the_list() -> None:
    """Publishing is reading: the problems and the diff are in front of her."""
    queue = without_comments(QUEUE)
    assert 'value="publish"' not in queue
    assert 'value="publish"' in REVIEW
    assert "/api/guides/admin/by-id/${id}/publish" in REVIEW


def test_sending_back_needs_a_note_on_the_page_too() -> None:
    assert "if (!note)" in REVIEW
    assert 'name="note"' in REVIEW and "required" in REVIEW


def test_the_review_page_diffs_by_step_id() -> None:
    assert "const added = " in REVIEW and "const removed = " in REVIEW and "const changed = " in REVIEW
    assert "never deletes anybody's progress" in REVIEW


def test_a_version_with_problems_cannot_be_published_from_the_page() -> None:
    assert "disabled={problems.length > 0}" in REVIEW


def test_every_admin_form_carries_the_csrf_field() -> None:
    for page in (QUEUE, REVIEW):
        forms = re.findall(r"<form[^>]*method=\"POST\"[^>]*>.*?</form>", page, flags=re.S)
        assert forms, "no forms found"
        for form in forms:
            assert "<CsrfField />" in form


def test_the_admin_nav_has_the_page() -> None:
    layout = (SRC / "layouts" / "AdminLayout.astro").read_text(encoding="utf-8")
    assert '["/admin/guides", "Guides"]' in layout
