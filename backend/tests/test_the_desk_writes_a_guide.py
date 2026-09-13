# SPDX-License-Identifier: AGPL-3.0-only
"""
The desk: where an author writes a guide, as forms.

Source-level guards, as everywhere in this suite.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from shruti.api.routes import guides

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "site" / "src"
DESK = (SRC / "pages" / "guides" / "write.astro").read_text(encoding="utf-8")
EDITOR = (SRC / "pages" / "guides" / "write" / "[version].astro").read_text(encoding="utf-8")


def without_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def test_a_new_guide_is_a_saved_skeleton_not_a_create_endpoint() -> None:
    """The server has one rule for filing a draft; the desk uses it."""
    desk = without_comments(DESK)
    assert '"/api/guides/draft"' in desk and "version_id: null" in desk
    assert "/api/guides/new" not in desk and "/api/guides/create" not in desk


def test_the_editor_never_publishes() -> None:
    for page in (DESK, EDITOR):
        assert "/publish" not in without_comments(page)


def test_the_editors_words_come_from_the_page() -> None:
    """Every label an author reads is editable from the admin; the script carries none."""
    assert "data-words={JSON.stringify(WORDS)}" in EDITOR
    # The LAST script block is the editor; a comment above it once named a
    # script tag literally and the first match began there.
    script = EDITOR[EDITOR.rindex("<script>"):]
    assert "W = JSON.parse(root.dataset.words" in script
    # No braced say() inside the script — it would render as its own source.
    assert not re.search(r"\{\s*say\(", script)


def test_the_document_rides_in_an_attribute_not_a_script_block() -> None:
    """
    ⚠ A self-closing JSON <script /> made the copy sweep read the whole page
    as client code. An attribute is escaped by Astro and closes nothing.
    """
    assert "data-doc={JSON.stringify(doc)}" in EDITOR
    assert 'type="application/json"' not in EDITOR
    assert "JSON.parse(root.dataset.doc" in EDITOR


def test_the_editor_is_for_the_author_only() -> None:
    assert "return Astro.redirect(`/signin?next=/guides/write/${id}`)" in EDITOR
    assert 'if (!/^\\d+$/.test(id)) return Astro.rewrite("/404")' in EDITOR
    assert "asReader(Astro, `/api/guides/mine/by-id/${id}`)" in EDITOR
    body = inspect.getsource(guides.my_version)
    body = re.sub(r'"""..*?"""', " ", body, flags=re.S)         # the docstring SAYS "never 403"
    assert "guide.created_by != user.id" in body and "403" not in body


def test_submitting_saves_first_and_refuses_problems() -> None:
    script = without_comments(EDITOR)
    assert "if (!(await save())) return;" in script
    assert "if (problems.length) { tell(W.status.submitFailed" in script


def test_a_draft_with_problems_still_saves() -> None:
    """The problems come back beside the save; they do not refuse it."""
    script = without_comments(EDITOR)
    assert "problems = a.problems ?? [];" in script
    assert "savedProblems" in script


def test_typing_never_loses_the_caret() -> None:
    """Inputs bind by path; only structural changes redraw."""
    script = without_comments(EDITOR)
    assert 'sections.addEventListener("input"' in script
    input_handler = script[script.index('sections.addEventListener("input"'):script.index('sections.addEventListener("change"')]
    assert "draw()" not in input_handler


def test_leaving_with_unsaved_work_asks_first() -> None:
    assert 'window.addEventListener("beforeunload"' in EDITOR
    assert "if (dirty && editable)" in EDITOR


def test_the_gate_keys_come_from_the_checkin_fields() -> None:
    script = without_comments(EDITOR)
    for key in ("_min", "_max", "_at_least", "_is", '"variant"', '"steps_done"', '"codex_active"'):
        assert key in script[script.index("const gateKeys"):script.index("const gate = ")]


def test_a_read_only_version_disables_the_desk() -> None:
    assert 'disabled={!version.editable}' in EDITOR
    assert '[data-editable="0"] input' in EDITOR
