# SPDX-License-Identifier: AGPL-3.0-only
"""
Game data: what a game is made of, as facts a planner can offer.

Every class, skill, passive, board, node, glyph, slot, base, affix, unique,
set, runeword, rune, gem, jewel, charm, flask, aspect, tempering manual and
mercenary of a supported game, in one SQLite file both shrutivtuber.com and
the self-hosted tracker open read-only. The file is BUILT from the research
packs (`research/<game>/*.json` in the guides repository) by `load.py`, and
READ by `query.py`; the planner in `planner.py` turns a person's choices into
the goals the build tracker already knows how to follow.

⚠ The data is not this package. The code is AGPL and public; the packs are
facts gathered with their sources recorded and are served at runtime, like
the language packs — never committed to the public repository. See the
guides repository's `research/LICENSE-DATA.md`.

⚠ Nothing here measures a person. The database describes games.
"""
from __future__ import annotations

from .load import build_database, Report  # noqa: F401
from .planner import clean_plan, plan_to_categories, plan_summary, plan_goals, stream_sheet  # noqa: F401
from .query import GameData  # noqa: F401
from .recipes import RECIPES, recipe_for  # noqa: F401
from .schema import KINDS, FILES  # noqa: F401

__all__ = ["build_database", "Report", "GameData", "clean_plan", "plan_to_categories", "plan_summary", "plan_goals", "stream_sheet",
           "RECIPES", "recipe_for", "KINDS", "FILES"]
