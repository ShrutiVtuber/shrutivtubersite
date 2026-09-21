# SPDX-License-Identifier: AGPL-3.0-only
"""
A build can be planned in a game's own terms: class, skills, the item wanted
in each slot, boards, glyphs. The planning logic lives in the shared package
(shrutisgametracker/server/shrutisguides/gamedata) and is tested there;
these hold the site's half — that the routes delegate to it, that the game
data is read and never written here, and that a planned build reaches the
phone and the overlay in the shape they already know.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest
from fastapi import HTTPException

from shruti.api.routes import builds, gamedata
from shruti.models.guides import Build

HERE = Path(__file__).resolve().parents[1]
FIXTURES = Path.home() / "Documents/development/shrutisgametracker/server/tests/fixtures/gamedata"


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def test_the_site_delegates_planning_to_the_shared_package() -> None:
    assert "clean_plan(" in code_of(builds._planned) and "plan_to_categories(" in code_of(builds._planned)
    assert "plan_goals(" in code_of(builds.create_planned_build) and "plan_goals(" in code_of(builds.replan)
    assert "categories_of(" in code_of(builds.set_goal), "a goal is checked against the build's own categories"
    assert "plan_summary(" in code_of(builds._build_view)
    for name in ("_clean_plan", "_plan_to_categories", "_recipe"):
        assert not hasattr(builds, name), f"{name} is a local copy"


def test_the_plan_routes_come_before_the_build_id_route() -> None:
    source = inspect.getsource(builds)
    for path in ('@router.post("/plan"', '@router.post("/sheet"'):
        assert source.index(path) < source.index('@router.get("/{build_id}")'), f"{path} would otherwise be read as a build id"


def test_a_sheet_is_computed_by_the_shared_package_and_kept_off_the_list() -> None:
    assert "compute_sheet(" in code_of(builds.plan_sheet) and "compute_sheet(" in code_of(builds._build_view)
    assert "with_sheet" in code_of(builds.one) and "with_sheet=True" in code_of(builds.create_planned_build)
    assert "with_sheet" not in code_of(builds.my_builds), "a page of twenty builds does not walk twenty pools"


def test_a_planned_build_stands_on_no_template() -> None:
    b = Build(user_id=1, template_id=None, game_id=3, name="b", plan={"game": "x"}, categories=[{"id": "gear", "name": "Gear", "grid": True, "items": []}])
    assert b.template_id is None and b.categories[0]["grid"]
    view = builds._planned_template(b, None)
    assert view["name"] == "Planned" and view["categories"] == b.categories and view["id"] is None
    migration = (HERE / "alembic/versions/i7g4d0e5f632_planned_builds.py").read_text()
    assert 'op.alter_column("build", "template_id", existing_type=sa.Integer(), nullable=True)' in migration
    for column in ("plan", "categories", "game_id"):
        assert f'sa.Column("{column}"' in migration


def test_the_game_data_is_read_and_never_written() -> None:
    source = inspect.getsource(gamedata)
    for word in ("@router.post", "@router.put", "@router.delete", "get_session", "_reader", "request.cookies"):
        assert word not in source, f"{word}: the game data routes read facts about games and nothing about people"
    assert "SHRUTI_GAMEDATA_DIR" in source and '"/app/gamedata"' in source
    compose = (HERE.parent / "docker-compose.yml").read_text()
    assert "gamedata:/app/gamedata" in compose and "gamedata:/srv/gamedata:ro" in compose
    caddy = (HERE.parent / "Caddyfile.internal").read_text()
    assert "handle /gamedata/*" in caddy and "handle /gamedata/manifest.json" in caddy
    assert (HERE.parent / "scripts/sync-gamedata.sh").exists()


def test_the_routes_answer_from_a_built_database(tmp_path, monkeypatch) -> None:
    if not FIXTURES.exists():
        pytest.skip("the guides repository is not checked out beside this one")
    from shrutisguides.gamedata import build_database
    build_database(FIXTURES, tmp_path / "gamedata.sqlite3")
    monkeypatch.setattr(gamedata, "GAMEDATA_DIR", tmp_path)
    games = gamedata.games()
    assert games[0]["id"] == "squirrel-quest" and games[0]["planner"] is False and isinstance(games[0]["problems"], int)
    # called as functions, so the Query defaults are given by hand
    listed = lambda **kw: gamedata.records("squirrel-quest", "skill", limit=500, offset=0, **kw)     # noqa: E731
    assert [s["id"] for s in listed(class_id="forager", sub="active")] == ["acorn-toss", "great-leap", "shared-shout"]
    assert "cost" not in listed()[0], "lists are brief"
    one = gamedata.record("squirrel-quest", "skill", "acorn-toss")
    assert one["cost"] == "10 acorns" and any(l["rel"] == "requires" and l["kind"] == "skill" for l in one["linked_from"])
    assert [r["id"] for r in gamedata.search("squirrel-quest", q="golden", limit=40)] == ["the-golden-acorn"]
    assert gamedata.groups("squirrel-quest", "skill")[0]["group"] == "basic"
    assert "sources-items" in gamedata.sources("squirrel-quest")
    with pytest.raises(HTTPException) as refused:
        gamedata.records("chess", "skill", limit=500, offset=0)
    assert refused.value.status_code == 404
    with pytest.raises(HTTPException):
        gamedata.recipe("squirrel-quest")
    with pytest.raises(HTTPException):
        gamedata.manifest()
    monkeypatch.setattr(gamedata, "GAMEDATA_DIR", tmp_path / "none")
    assert gamedata.games() == [], "no database is a working state"


def test_nothing_about_a_person_and_nothing_red() -> None:
    body = re.sub(r'"""..*?"""', " ", inspect.getsource(gamedata), flags=re.S).lower()
    for word in ("streak", "days since", "percent", "inactive", "remind", "red"):
        assert word not in body


# ── a build somebody else can read, and start their own from ────────────────

def test_a_share_code_is_a_code_and_not_a_token() -> None:
    """
    ⚠ An overlay token is shown once and never listed. A share code is meant
    to be said out loud and is listed to its owner for as long as it stands.
    Confusing the two would either leak a token or make a code unusable.
    """
    source = inspect.getsource(builds)
    assert "ALPHABET = " in source and '"I"' not in source, "no I or O: they read as digits on stream"
    assert "shareCode" in code_of(builds._build_view), "the owner can read their own code back"
    assert "secrets.choice" in code_of(builds._share_code)
    assert "if not b.share_code:" in code_of(builds.share_build), "asking twice gives the same code"


def test_a_persons_note_to_themselves_never_travels() -> None:
    goals = {"helm": {"target": "Shroud of False Death", "met": True, "note": "the one I keep missing"},
             "chest": {"partial": True, "note": "private"}, "junk": "not a mapping"}
    out = builds.public_goals(goals)
    assert out["helm"] == {"target": "Shroud of False Death", "met": True}
    assert out["chest"] == {"partial": True}
    assert "note" not in str(out) and "junk" not in out
    assert builds.public_goals(None) == {}
    assert "public_goals(" in code_of(builds._shared_view), "the shared page goes through it"
    assert "shared.public_progress(" in code_of(builds._shared_view), "and so does the progress computed from them"
    assert builds.public_goals is __import__("shrutisguides.builds", fromlist=["x"]).public_goals, \
        "the rule lives in the shared package, so the tracker cannot disagree about what is private"
    assert "public_goals(" in code_of(builds.copy_shared_build), "and so does a copy"


def test_a_copy_takes_the_targets_and_none_of_the_progress() -> None:
    body = code_of(builds.copy_shared_build)
    assert '{"target": target}' in body, "what to aim for, and nothing about how far they got"
    for word in ("met", "partial", "have"):
        assert f'"{word}"' not in body, f"a copy must not inherit {word}"
    assert "forked_from_id=src.id" in body and "run_id=None" in body
    assert "share_code" not in body, "a copy is private until its owner shares it"


def test_the_shared_routes_come_before_the_build_id_route() -> None:
    source = inspect.getsource(builds)
    assert source.index('@router.get("/shared/{code}")') < source.index('@router.get("/{build_id}")')
    assert source.index('@router.post("/shared/{code}/copy"') < source.index('@router.get("/{build_id}")')


def test_reading_a_shared_build_needs_no_account_but_copying_does() -> None:
    assert "_reader(" not in code_of(builds.shared_build), "a code is given out to be used"
    assert "_reader(" in code_of(builds.copy_shared_build) and "_refuse_if_suspended(" in code_of(builds.copy_shared_build)
    assert "user_id" not in code_of(builds._shared_view), "nothing about the person who owns it"


def test_the_columns_and_their_migration_exist() -> None:
    b = Build(user_id=1, name="b", share_code="HEKATE", forked_from_id=3)
    assert b.share_code == "HEKATE" and b.forked_from_id == 3
    assert Build(user_id=1, name="b").share_code is None, "private is the default"
    migration = (HERE / "alembic/versions/j8h5e1f6g743_shared_builds.py").read_text()
    for column in ("share_code", "shared_at", "forked_from_id"):
        assert f'sa.Column("{column}"' in migration
    assert 'unique=True' in migration, "two builds cannot hold one code"
