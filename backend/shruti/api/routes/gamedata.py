# SPDX-License-Identifier: AGPL-3.0-only
"""
The game data, read: what a game is made of, for the planner to offer.

Everything here is a read of one SQLite file built from the research packs
by `shrutisguides.gamedata` and mounted into the container — like the
language packs, served at runtime and never in this repository. The file's
absence is a working state: the planner says the game is not loaded yet.

⚠ Facts about games, nothing about people. No route here reads a session.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from shrutisguides.gamedata import GameData, KINDS, recipe_for

router = APIRouter(prefix="/api/gamedata", tags=["gamedata"])

GAMEDATA_DIR = Path(os.environ.get("SHRUTI_GAMEDATA_DIR", "/app/gamedata"))


def data() -> GameData:
    return GameData(GAMEDATA_DIR / "gamedata.sqlite3")


def _loaded(game: str) -> GameData:
    d = data()
    if not d.exists() or d.game(game) is None:
        raise HTTPException(404, "that game's data is not loaded")
    return d


@router.get("/games")
def games() -> list[dict]:
    """Every loaded game with its patch, season and record counts — and whether a planner exists for it."""
    return [{**g, "problems": len(g["problems"]), "planner": recipe_for(g["id"]) is not None} for g in data().games()]


@router.get("/manifest")
def manifest() -> dict:
    """What a self-hosted tracker pulls: the file's name, size and digest, beside the games it holds."""
    path = GAMEDATA_DIR / "manifest.json"
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        raise HTTPException(404, "no game data is published")


@router.get("/{game}")
def game(game: str) -> dict:
    d = _loaded(game)
    g = d.game(game)
    return {**g, "problems": len(g["problems"]), "recipe": recipe_for(game)}


@router.get("/{game}/recipe")
def recipe(game: str) -> dict:
    _loaded(game)
    r = recipe_for(game)
    if r is None:
        raise HTTPException(404, "no planner for that game yet")
    return r


@router.get("/{game}/search")
def search(game: str, q: str = Query(min_length=1, max_length=80), kinds: str = "", class_id: str = "", limit: int = Query(40, ge=1, le=200)) -> list[dict]:
    d = _loaded(game)
    wanted = [k for k in kinds.split(",") if k in KINDS]
    return d.search(game, q, kinds=wanted or None, class_id=class_id or None, limit=limit)


@router.get("/{game}/sources")
def sources(game: str) -> dict:
    """Where the facts came from, in the researchers' own notes."""
    return _loaded(game).sources(game)


@router.get("/{game}/{kind}")
def records(game: str, kind: str, sub: str = "", class_id: str = "", slot_id: str = "", group: str = "", tag: str = "", q: str = "",
            ids: str = "", brief: bool = True, limit: int = Query(500, ge=1, le=5000), offset: int = Query(0, ge=0)) -> list[dict]:
    """The records of one kind, filtered. Brief by default: a chooser needs names; one record's whole is a step below."""
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    d = _loaded(game)
    return d.list(game, kind, sub=[s for s in sub.split(",") if s] or None, class_id=class_id or None, slot_id=slot_id or None,
                  group=group or None, tag=tag or None, q=q or None, ids=[i for i in ids.split(",") if i] or None,
                  limit=limit, offset=offset, brief=brief)


@router.get("/{game}/{kind}/groups")
def groups(game: str, kind: str, class_id: str = "") -> list[dict]:
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    return _loaded(game).groups(game, kind, class_id=class_id or None)


@router.get("/{game}/{kind}/{id}")
def record(game: str, kind: str, id: str) -> dict:
    """One record whole, with what it points at and what points at it."""
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    d = _loaded(game)
    r = d.get(game, kind, id)
    if r is None:
        raise HTTPException(404, "no such record")
    return {**r, "links": d.links(game, kind, id), "linked_from": d.links(game, kind, id, direction="in")}
