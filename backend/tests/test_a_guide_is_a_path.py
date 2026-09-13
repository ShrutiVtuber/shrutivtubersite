# SPDX-License-Identifier: AGPL-3.0-only
"""
Shruti's Guides on the site: the catalogue, the desk, and her queue.

Source-level guards, as everywhere in this suite. The format itself is tested
where it lives (shrutisgametracker/server/tests); these hold the site's half:
who may do what, in what order the routes are declared, and that the practice
room's rules were reused rather than re-invented slightly differently.
"""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

from shruti.api.routes import guides
from shruti.models import guides as models

SOURCE = inspect.getsource(guides)


def code_of(function) -> str:
    """Source with comments and docstring stripped — the trap this suite knows well."""
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


# ── the shape of the API ─────────────────────────────────────────────────────

def test_literal_paths_come_before_the_reader() -> None:
    """
    ⚠ FastAPI matches in declaration order. `/{game}/{slug}` declared above
    `/games` would read "games" as a game and answer 404 for the list.
    """
    reader = SOURCE.index('@router.get("/{game}/{slug}")')
    # ⚠ Substrings of the path, not whole decorators: the admin ones carry a
    # dependencies= argument and a whole-decorator match silently misses them.
    for literal in ('"/games"', '"/mine"', '"/draft"', '"/admin/queue"', '/by-id/{guide_id}/download'):
        assert SOURCE.index(literal) < reader, f"{literal} is declared after the reader"


def test_ids_and_slugs_cannot_be_confused() -> None:
    """A guide by id lives under /by-id/, so a slug is never read as a number."""
    assert "/by-id/{guide_id}" in SOURCE and "/by-id/{version_id}" in SOURCE
    assert '@router.get("/{guide_id}")' not in SOURCE
    assert '@router.post("/{guide_id}/' not in SOURCE


# ── drafts and submission ────────────────────────────────────────────────────

def test_a_draft_may_be_saved_with_problems() -> None:
    body = code_of(guides.save_draft)
    assert "problems = _problems(doc)" in body
    # ⚠ Saved regardless: the problems come back beside it, they do not refuse
    # it. The only 422 is for a draft with nowhere to be filed.
    assert "to be filed under" in body
    assert body.count("422") == 1
    assert '"problems": problems' in body


def test_only_a_clean_draft_may_be_submitted() -> None:
    body = code_of(guides.submit)
    assert "_problems(version.body)" in body
    assert "status_code=422" in body
    assert 'version.state = "submitted"' in body


def test_publishing_refuses_problems_even_from_her() -> None:
    """A published guide that fails its own validator is one the tracker cannot run."""
    body = code_of(guides.publish)
    assert "_problems(v.body)" in body
    assert "status_code=422" in body


def test_publishing_supersedes_rather_than_deletes() -> None:
    """The old version is kept, so a publish can be rolled back to it."""
    body = code_of(guides.publish)
    assert 'old.state = "superseded"' in body
    assert "session.delete" not in body


def test_sending_back_needs_a_reason() -> None:
    """⚠ 'Rejected' with no reason is the practice room's lesson again."""
    body = code_of(guides.send_back)
    assert "not body.note.strip()" in body
    assert "422" in body


def test_an_author_cannot_edit_a_published_version() -> None:
    body = code_of(guides.save_draft)
    assert 'version.state not in ("draft", "sent_back")' in body


# ── the practice room's rules, reused ────────────────────────────────────────

def test_reports_use_the_rooms_reasons_and_threshold() -> None:
    """
    ⚠ Two slips this file has already made, both caught at import: the wrong
    list was aliased as REASONS, and the right one was unpacked as pairs when
    it is a flat list of strings.
    """
    assert "REPORT_REASONS as REASONS" in SOURCE
    assert "REPORTS_TO_HIDE" in code_of(guides.report)
    assert "for r, _ in REASONS" not in SOURCE, "REPORT_REASONS is a flat list"
    assert "body.reason in REASONS" in code_of(guides.report)


def test_the_catalogue_filters_blocked_authors_before_the_limit() -> None:
    body = code_of(guides.catalogue)
    assert "_hidden_from" in body
    assert body.index("not_in(hidden)") < body.index(".limit(")


def test_hidden_is_404_except_for_the_author() -> None:
    body = code_of(guides.one)
    assert "g.hidden and not mine_" in body
    assert "403" not in body


def test_blocks_are_not_duplicated() -> None:
    """A block is a block whatever they were reading: PracticeBlock, not a new table."""
    src = inspect.getsource(models)
    assert "class GuideBlock" not in src
    assert "_hidden_from" in SOURCE


def test_a_vote_and_a_report_are_unique_in_the_database() -> None:
    src = inspect.getsource(models)
    assert 'UniqueConstraint("guide_id", "user_id", name="uq_guide_vote")' in src
    assert 'UniqueConstraint("guide_id", "user_id", name="uq_guide_report")' in src
    migration = next((Path(__file__).resolve().parents[1] / "alembic" / "versions").glob("*_guides.py")).read_text()
    assert "uq_guide_vote" in migration and "uq_guide_report" in migration


def test_a_report_hidden_guide_returns_when_she_publishes() -> None:
    """Publishing IS her looking at it, which is what the reports were waiting for."""
    body = code_of(guides.publish)
    assert 'g.hidden_by == "reports"' in body


# ── the format, on the site ──────────────────────────────────────────────────

def test_versions_carry_the_state_not_guides() -> None:
    src = inspect.getsource(models)
    assert "state: str" in src.split("class GuideVersion")[1].split("class GuideVote")[0]
    assert "published_version_id" in src.split("class Guide(")[1].split("class GuideVersion")[0]


def test_the_body_is_jsonb() -> None:
    """⚠ Plain JSON is text re-parsed on every read; JSONB is what Postgres indexes."""
    src = inspect.getsource(models)
    assert "JSONB" in src
    migration = next((Path(__file__).resolve().parents[1] / "alembic" / "versions").glob("*_guides.py")).read_text()
    assert "postgresql.JSONB()" in migration


def test_the_diablo_guide_is_clean_by_the_sites_validator() -> None:
    """The site validates with the same package the format repository tests with."""
    example = Path.home() / "Documents/development/shrutisgametracker/examples/diablo-iv-squirrel-guide.json"
    if not example.exists():
        pytest.skip("the guides repository is not checked out beside this one")
    assert guides._problems(json.loads(example.read_text())) == []
