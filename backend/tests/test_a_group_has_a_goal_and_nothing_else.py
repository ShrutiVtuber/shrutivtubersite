# SPDX-License-Identifier: AGPL-3.0-only
"""
A group has a goal and nothing else — no path, no steps, no schedule.

Nobody is ranked and nobody is reminded: the crew is listed by size with
"and N others", so a small contribution is never the bottom of a
leaderboard, and nothing about a group measures anyone's absence.
"""
from __future__ import annotations

import inspect
import re

from shruti.api.routes import groups
from shruti.models.guides import Group, GroupContribution, GroupMember

SOURCE = inspect.getsource(groups)


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def test_a_group_has_no_path() -> None:
    fields = set(Group.model_fields) | set(GroupMember.model_fields) | set(GroupContribution.model_fields)
    for word in ("steps", "phases", "routines", "checkin", "path", "schedule", "streak", "last_seen_at"):
        assert word not in fields, f"a group carries {word}"


def test_nobody_is_ranked() -> None:
    view = code_of(groups._view)
    assert "rows[:3]" in view and '"others"' in view, "the crew is the largest three and 'and N others'"
    for word in ("rank", "medal", "leaderboard", "position", "place"):
        assert word not in view.lower(), f"{word} in the group view"
    element = code_of(groups.goal_element)
    assert "rank" not in element and "contributors" in element


def prose_free(text: str) -> str:
    text = re.sub(r'"""..*?"""', " ", text, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", text)


def test_nobody_is_reminded() -> None:
    body = prose_free(SOURCE).lower()
    for word in ("remind", "streak", "missed", "days since", "inactive", "last_seen_at"):
        assert word not in body, f"{word} in the groups routes"


def test_a_contribution_is_one_number_given_once() -> None:
    body = code_of(groups.contribute)
    assert "GroupContribution(" in body and "amount=amount" in body
    assert "PUT" not in SOURCE and "def edit_contribution" not in SOURCE, "a contribution is never edited"
    assert 'raise HTTPException(403, "join the group first")' in body


def test_the_join_code_reads_aloud_on_stream() -> None:
    assert "I" not in groups.ALPHABET and "O" not in groups.ALPHABET and "0" not in groups.ALPHABET and "1" not in groups.ALPHABET
    assert len(groups._code()) == 6 and groups._code().isupper()


def test_the_goal_is_the_sigils_parts() -> None:
    view = {"name": "Squirrel stream crew", "goal": "Empire to tier 5", "total": 934, "target": 1200, "tier": 3, "tiers": 5,
            "sigil": [{"pct": 1.0, "state": "done"}] * 3 + [{"pct": 0.89, "state": "now"}, {"pct": 0.0, "state": "todo"}],
            "contributions": [{"who": "nyx_vt", "amount": 310}, {"who": "hesperos", "amount": 228}, {"who": "Shruti", "amount": 40}],
            "others": {"count": 9, "amount": 356}, "members": 12}
    el = groups.goal_element(view)
    assert el["count"] == "934 of 1,200" and el["parts"] == view["sigil"] and el["tier"] == 3 and el["tiers"] == 5
    assert el["contributors"] == ["nyx_vt", "hesperos", "Shruti"] and el["others"] == 9
    assert "amount" not in str(el["contributors"]), "the overlay names the crew, not their numbers"


def test_a_goal_overlay_is_a_members_and_its_token_is_read_once() -> None:
    body = code_of(groups.mint_goal_token)
    assert 'raise HTTPException(403, "join the group first")' in body
    assert "secrets.token_urlsafe(24)" in body and '"token": token' in body
    listing = code_of(groups.goal_tokens)
    assert '"token"' not in listing, "a listing never repeats the token"


def test_reading_a_group_needs_no_account() -> None:
    body = code_of(groups.one)
    assert "current_user(" in body and "_reader(" not in body
