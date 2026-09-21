# SPDX-License-Identifier: AGPL-3.0-only
"""
A build as a file: yours to keep, or to move to a server you run.

A run already leaves as one JSON document; a build should too. This is that
document — the name, the game, the plan in the game's own terms, the goals
with your own words in them, and enough about where it came from to read it
back somewhere else.

⚠ This is YOUR copy, so it keeps the note you wrote to yourself. That is the
difference between a file and a share: a share is given to somebody else and
`builds.public_goals` strips the private words out of it; a file is carried
by the person who wrote it and keeps everything.

⚠ Read a file as though a stranger wrote it, because one might have. Every
field is bounded, the categories go through the same cleaner the admin's
templates do, and anything unrecognised is REPORTED rather than trusted or
silently dropped.
"""
from __future__ import annotations

from typing import Any

from . import builds

FORMAT = "squirrel-guides-build"
VERSION = 1
MAX_NAME = 80
MAX_TEXT = 400


def _text(value: Any, limit: int) -> str:
    return "" if value is None or isinstance(value, (dict, list)) else str(value).strip()[:limit]


def to_file(*, name: str, variant: str = "", game: dict | None = None, plan: dict | None = None,
            categories: list | None = None, goals: dict | None = None, template: str = "",
            source: str = "") -> dict:
    """The document. Everything needed to read this build back, and nothing derived."""
    return {
        "format": FORMAT,
        "version": VERSION,
        "name": _text(name, MAX_NAME),
        "variant": _text(variant, MAX_NAME),
        "game": {"slug": _text((game or {}).get("slug"), MAX_NAME),
                 "name": _text((game or {}).get("name"), MAX_NAME)},
        "template": _text(template, MAX_NAME),
        "plan": dict(plan or {}),
        "categories": builds.clean_categories(categories),
        "goals": {k: dict(v) for k, v in (goals or {}).items() if isinstance(v, dict)},
        "source": _text(source, MAX_TEXT),
    }


def read_file(doc: Any) -> tuple[dict, list[str]]:
    """
    A document as fields a server can store, and every reason a part of it was
    refused. Returns ({}, problems) when there is nothing usable.
    """
    problems: list[str] = []
    if not isinstance(doc, dict):
        return {}, ["that is not a build file"]
    if doc.get("format") != FORMAT:
        return {}, [f"that file says it is '{_text(doc.get('format'), 40) or 'nothing in particular'}', not a build"]
    try:
        version = int(doc.get("version") or 0)
    except (TypeError, ValueError):
        version = 0
    if version > VERSION:
        problems.append(f"the file is version {version} and this server reads {VERSION}; anything newer in it is ignored")
    elif version < 1:
        problems.append("the file states no version; it is read as version 1")

    name = _text(doc.get("name"), MAX_NAME)
    if not name:
        return {}, problems + ["a build needs a name"]

    categories = builds.clean_categories(doc.get("categories"))
    plan = doc.get("plan") if isinstance(doc.get("plan"), dict) else {}
    if not categories and not plan:
        return {}, problems + ["that file has neither goals nor a plan in it"]

    known = builds.known_items(categories)
    goals: dict = {}
    unknown = 0
    for item_id, g in (doc.get("goals") or {}).items() if isinstance(doc.get("goals"), dict) else ():
        if item_id not in known:
            unknown += 1
            continue
        cleaned = builds.clean_goal(g)
        if cleaned:
            goals[item_id] = cleaned
    if unknown:
        problems.append(f"{unknown} goal(s) in the file are for items this build does not have, and were left out")

    game = doc.get("game") if isinstance(doc.get("game"), dict) else {}
    return {
        "name": name,
        "variant": _text(doc.get("variant"), MAX_NAME),
        "game_slug": builds.ident(game.get("slug") or game.get("name"), "") if game else "",
        "game_name": _text(game.get("name"), MAX_NAME),
        "plan": plan,
        "categories": categories,
        "goals": goals,
    }, problems
