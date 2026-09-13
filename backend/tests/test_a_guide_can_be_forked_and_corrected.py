# SPDX-License-Identifier: AGPL-3.0-only
"""
Forking a guide, and a contribution that is a difference against a
published version — never a silent edit, and never a publish.
"""
from __future__ import annotations

import inspect
import re

from shruti.api.routes import guides
from shruti.core import guide_diff


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


BEFORE = {
    "guide": {"id": "g", "title": "A", "version": "1"},
    "phases": [{"id": "p1", "name": "One"}, {"id": "p2", "name": "Two"}],
    "steps": [{"id": "s1", "phase": "p1", "title": "First", "do": "Go"}, {"id": "s2", "phase": "p1", "title": "Second", "do": "Stay"}],
    "routines": [{"id": "r1", "name": "Daily", "items": [{"id": "i1", "text": "x"}]}],
}
AFTER = {
    "guide": {"id": "g", "title": "A, revised", "version": "2"},
    "phases": [{"id": "p1", "name": "One"}, {"id": "p3", "name": "Three"}],
    "steps": [{"id": "s1", "phase": "p1", "title": "First", "do": "Go now"}, {"id": "s2", "phase": "p1", "title": "Second", "do": "Stay"}, {"id": "s3", "phase": "p3", "title": "Third", "do": "Run"}],
    "routines": [{"id": "r1", "name": "Daily", "items": [{"id": "i1", "text": "x"}]}],
}


# ── the difference is in the guide's own terms ───────────────────────────────

def test_the_changes_name_steps_and_phases_not_json_lines() -> None:
    items = guide_diff.changes(BEFORE, AFTER)
    by = {(i["kind"], i["id"], i["change"]) for i in items}
    assert ("phase", "p3", "added") in by and ("phase", "p2", "removed") in by
    assert ("step", "s3", "added") in by and ("step", "s1", "changed") in by
    assert ("step", "s2", "changed") not in by, "an untouched step is not a change"
    changed = next(i for i in items if i["kind"] == "step" and i["id"] == "s1")
    assert changed["fields"] == [{"name": "do", "before": "Go", "after": "Go now"}]
    meta = next(i for i in items if i["kind"] == "the guide")
    assert {f["name"] for f in meta["fields"]} == {"title", "version"}
    assert guide_diff.summary(items) == {"added": 2, "removed": 1, "changed": 2}


def test_identical_bodies_have_no_changes() -> None:
    assert guide_diff.changes(BEFORE, BEFORE) == []
    assert guide_diff.summary([]) == {"added": 0, "removed": 0, "changed": 0}


def test_long_text_is_shortened_not_dumped() -> None:
    a = {"steps": [{"id": "s", "do": "x" * 2000}]}
    b = {"steps": [{"id": "s", "do": "y" * 2000}]}
    field = guide_diff.changes(a, b)[0]["fields"][0]
    assert len(field["before"]) <= guide_diff.LIMIT + 1 and field["before"].endswith("…")


# ── nothing anybody proposes publishes ───────────────────────────────────────

def test_a_proposal_goes_to_the_author_not_her_queue() -> None:
    body = code_of(guides.submit)
    assert 'version.state = "proposed" if proposal else "submitted"' in body
    assert "contributed_by is not None" in body


def test_accepting_never_publishes() -> None:
    body = code_of(guides.accept_contribution)
    assert 'version.state = "draft"' in body and "published" not in body
    assert "version.accepted_at = _now()" in body


def test_declining_needs_a_note() -> None:
    assert guides.DeclineIn.model_fields["note"].metadata, "a bare decline is the practice room's lesson again"
    assert 'version.note = body.note.strip()' in code_of(guides.decline_contribution)


def test_the_author_cannot_edit_an_open_proposal_and_the_contributor_cannot_edit_after_acceptance() -> None:
    body = code_of(guides._may_edit)
    assert "version.accepted_at is not None" in body and "version.contributed_by == user.id" in body
    assert "_may_edit(user, guide, version)" in code_of(guides.save_draft)


def test_a_proposal_is_not_the_authors_open_draft() -> None:
    assert "GuideVersion.contributed_by.is_(None)" in code_of(guides._open_draft)
    assert "GuideVersion.contributed_by.is_(None)" in code_of(guides.mine)


# ── forks ────────────────────────────────────────────────────────────────────

def test_a_fork_needs_a_licence_that_allows_it() -> None:
    assert set(guides.FORKABLE) == {"CC-BY-SA-4.0", "CC-BY-4.0", "CC0-1.0"}
    body = code_of(guides.fork)
    assert 'raise HTTPException(409, "this guide\'s licence does not allow forks")' in body


def test_a_fork_keeps_the_original_authors_and_remembers_its_origin() -> None:
    body = code_of(guides.fork)
    assert "authors.append(_name(user))" in body and "forked_from_id=guide.id" in body
    assert "copy.deepcopy(version.body)" in body


def test_a_stranger_learns_nothing() -> None:
    for fn in (guides.my_version, guides.version_changes, guides.accept_contribution, guides.decline_contribution):
        assert "403" not in code_of(fn), f"{fn.__name__} answers 403"
