# SPDX-License-Identifier: AGPL-3.0-only
"""
A build is a set of goals for one character. The logic is tested where it
lives (shrutisgametracker/server/tests/test_builds.py); these hold the
site's half: that the routes DELEGATE to the shared functions rather than
keeping a copy, and the rules a route could quietly break.
"""
from __future__ import annotations

import inspect
import re

from shrutisguides import builds as shared

from shruti.api.routes import builds
from shruti.models.guides import Build, BuildTemplate

SOURCE = inspect.getsource(builds)


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def prose_free(text: str) -> str:
    text = re.sub(r'"""..*?"""', " ", text, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", text)


# ── one implementation, shared with the self-hosted tracker ─────────────────

def test_the_site_delegates_to_the_shared_functions() -> None:
    assert "shared.progress(" in code_of(builds.progress_of)
    assert "shared.element(" in code_of(builds.build_element)
    assert "shared.apply_goal(" in code_of(builds.set_goal) and "shared.known_items(" in code_of(builds.set_goal)
    assert "shared.clean_categories(" in code_of(builds.create_template) and "shared.clean_categories(" in code_of(builds.update_template)
    for name in ("_progress", "_item_state", "_element", "_apply_goal", "_clean_categories"):
        assert not hasattr(builds, name), f"{name} is a local copy"


def test_progress_reaches_the_site_unchanged() -> None:
    t = BuildTemplate(game_id=1, name="t", categories=shared.clean_categories([
        {"name": "Gear", "grid": True, "items": [{"label": "Helm", "kind": "slot"}, {"label": "Chest", "kind": "slot"}]},
        {"name": "Paragon", "items": [{"label": "Points", "kind": "counter", "max": 300}]},
    ]))
    b = Build(user_id=1, template_id=1, name="b", goals={"helm": {"met": True}, "chest": {"partial": True}, "points": {"have": 150}})
    p = builds.progress_of(t, b)
    assert (p["met"], p["partly"], p["total"]) == (1, 2, 3) and p["next"][0]["id"] == "chest"
    el = builds.build_element({"name": "b", "variant": "", "template": {"game": {"name": "Diablo IV"}}, "progress": p})
    assert el["gridName"] == "Gear" and el["eyebrow"] == "Build · Diablo IV"


# ── the rules a route could quietly break ────────────────────────────────────

def test_nothing_measures_absence() -> None:
    body = prose_free(SOURCE).lower()
    for word in ("streak", "days since", "since", "percent", "inactive", "remind"):
        assert word not in body


def test_a_goal_outside_the_template_is_refused() -> None:
    assert 'raise HTTPException(404, "no such goal in this build")' in code_of(builds.set_goal)


def test_a_template_with_builds_on_it_is_hidden_not_deleted() -> None:
    assert "t.visible = False" in code_of(builds.delete_template)


def test_a_build_token_is_read_once_and_counts_against_fair_use() -> None:
    body = code_of(builds.mint_build_token)
    assert "secrets.token_urlsafe(24)" in body and "refuse_if_out_of_allowance" in body
    assert '"token"' not in code_of(builds.build_tokens), "a listing never repeats the token"


def test_a_persons_notes_stay_off_the_stream() -> None:
    assert '"note"' not in prose_free(inspect.getsource(shared.element))


def test_a_build_overlay_switches_only_between_the_same_persons_builds() -> None:
    body = code_of(builds.rebind_build_token)
    assert "target.user_id != user.id" in body and "row.build_id = target.id" in body
