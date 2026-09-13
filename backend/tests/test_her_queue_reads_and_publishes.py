# SPDX-License-Identifier: AGPL-3.0-only
"""
Her side of Shruti's Guides: the review queue (board W6), the reports, the
switches, and the channel being told.

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
    body = code_of(guides.publish)
    window = body[body.index("await _tell_discord("):]
    for field in ('"id"', '"title"', '"game"', '"author"', '"steps"', '"isUpdate"'):
        assert field in window
    assert "model_dump" not in window and "__dict__" not in window


def test_the_bridge_is_optional_and_never_raises() -> None:
    body = code_of(guides._tell_discord)
    assert "VCORDBOT_INTERNAL_URL" in body and "SHRUTI_INTERNAL_SECRET" in body
    assert "return" in body.split("try:")[0]
    assert "except Exception" in body
    assert "/internal/guides" in body


def test_an_update_is_known_before_the_pointer_moves() -> None:
    body = code_of(guides.publish)
    assert body.index("was_update = ") < body.index("g.published_version_id = v.id")


# ── her decisions settle the reports ─────────────────────────────────────────

def test_hiding_or_restoring_settles_the_open_reports() -> None:
    body = code_of(guides.hide)
    assert '"upheld" if body.hidden else "dismissed"' in body
    assert "if not body.hidden:" not in body


def test_the_admin_list_groups_reports_by_the_guide() -> None:
    body = code_of(guides.admin_guides)
    assert "by_guide" in body
    assert '"reasons": reasons' in body
    assert "GuideReport.reviewed_at.is_(None)" in body


# ── a version knows which tool wrote it ──────────────────────────────────────

def test_a_versions_source_is_kept_and_shown() -> None:
    """"drafted by an agent" is a fact she wants in front of her when she reads."""
    assert '"source": v.source' in code_of(guides.queue)
    body = code_of(guides.save_draft)
    assert 'version.source = body.source if body.source in SOURCES else "desk"' in body
    assert guides.SOURCES == ("desk", "agent", "file")
    migration = next((ROOT / "backend" / "alembic" / "versions").glob("*_version_source.py")).read_text(encoding="utf-8")
    assert 'server_default="desk"' in migration
    page = without_comments(QUEUE)
    assert 'v.source === "agent"' in page and "drafted by an agent" in page
    assert "Nothing an agent does publishes" in page


# ── the page ─────────────────────────────────────────────────────────────────

def test_publishing_happens_beside_the_diff() -> None:
    """Publishing is reading: the problems and the changes are in front of her."""
    page = without_comments(QUEUE)
    assert page.count('value="publish"') == 1
    assert "disabled={problems.length > 0}" in page
    assert "/api/guides/admin/by-id/${id}/publish" in page


def test_sending_back_needs_a_note_on_the_page_too() -> None:
    page = without_comments(QUEUE)
    assert "if (!note)" in page
    assert 'name="note"' in page and "required" in page


def test_the_diff_is_by_step_id_with_marks_not_colour() -> None:
    page = without_comments(QUEUE)
    assert "const changes: Change[]" in page
    for mark in ('"+"', '"~"', '"−"'):
        assert mark in page
    assert "does not delete anybody's progress" in page
    assert "green" not in page.lower().replace("greyed", "")


def test_every_admin_form_carries_the_csrf_field() -> None:
    forms = re.findall(r"<form[^>]*method=\"POST\"[^>]*>.*?</form>", QUEUE, flags=re.S)
    assert forms, "no forms found"
    for form in forms:
        assert "<CsrfField />" in form


def test_the_admin_nav_has_the_page() -> None:
    layout = (SRC / "layouts" / "AdminLayout.astro").read_text(encoding="utf-8")
    assert '["/admin/guides", "Guides"]' in layout
