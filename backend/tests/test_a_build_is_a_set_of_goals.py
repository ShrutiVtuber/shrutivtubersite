# SPDX-License-Identifier: AGPL-3.0-only
"""
A build is a set of goals for one character: slots to fill, counters to
reach, things to tick. The template is hers and generic; the build is one
person's, precise. Nothing measures absence.
"""
from __future__ import annotations

import inspect
import re

from shruti.api.routes import builds
from shruti.models.guides import Build, BuildTemplate

SOURCE = inspect.getsource(builds)


def prose_free(text: str) -> str:
    text = re.sub(r'"""..*?"""', " ", text, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", text)


def test_a_template_is_cleaned_into_known_kinds() -> None:
    cats = builds.clean_categories([
        {"name": "Gear", "items": [{"label": "Helm", "kind": "slot"}, {"label": "Masterwork", "kind": "counter", "max": 12}, {"label": "Nope", "kind": "weird"}]},
        {"name": "Gear", "items": []},
        "junk",
    ])
    assert [c["id"] for c in cats] == ["gear", "gear-2"]
    kinds = [it["kind"] for it in cats[0]["items"]]
    assert kinds == ["slot", "counter", "check"], "an unknown kind becomes a check, not an error"
    assert cats[0]["items"][1]["max"] == 12


def test_progress_is_met_partial_or_open_and_never_a_rate() -> None:
    t = BuildTemplate(game_id=1, name="t", categories=builds.clean_categories([
        {"name": "Gear", "items": [{"label": "Helm", "kind": "slot"}, {"label": "Chest", "kind": "slot"}]},
        {"name": "Paragon", "items": [{"label": "Points", "kind": "counter", "max": 300}]},
    ]))
    b = Build(user_id=1, template_id=1, name="b", goals={"helm": {"met": True, "target": "Shroud"}, "chest": {"partial": True}, "points": {"have": 150}})
    p = builds.progress_of(t, b)
    states = {it["id"]: it["state"] for c in p["categories"] for it in c["items"]}
    assert states == {"helm": "met", "chest": "partial", "points": "partial"}
    assert p["met"] == 1 and p["total"] == 3 and p["complete"] is False
    assert [c["ratio"] for c in p["categories"]] == [0.75, 0.5]
    assert p["next"][0]["label"] == "Chest"
    for word in ("streak", "days", "since", "percent"):
        assert word not in prose_free(SOURCE).lower()


def test_the_overlay_element_carries_only_what_it_draws() -> None:
    body = prose_free(inspect.getsource(builds.build_element))
    assert '"parts"' in body and '"next"' in body and '"count"' in body
    assert '"goals"' not in body and '"note"' not in body, "a person's own notes stay off the stream"


def test_a_goal_outside_the_template_is_refused_and_met_clears_partial() -> None:
    body = prose_free(inspect.getsource(builds.set_goal))
    assert 'raise HTTPException(404, "no such goal in this build")' in body
    assert 'g["partial"] = False' in body


def test_a_template_with_builds_on_it_is_hidden_not_deleted() -> None:
    body = prose_free(inspect.getsource(builds.delete_template))
    assert "t.visible = False" in body


def test_a_build_token_is_read_once_and_counts_against_fair_use() -> None:
    body = prose_free(inspect.getsource(builds.mint_build_token))
    assert "secrets.token_urlsafe(24)" in body and "refuse_if_out_of_allowance" in body
    assert '"token"' not in prose_free(inspect.getsource(builds.build_tokens))
