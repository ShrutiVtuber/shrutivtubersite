# SPDX-License-Identifier: AGPL-3.0-only
"""
What a plan comes to.

    from shrutisguides.gamedata.calc import sheet
    panel = sheet(plan, data)          # groups of rows, each with its working

The pool and its totals are in `model`; the canonical stat names are in
`vocabulary`; each game's own words are mapped in `games/`. A game without a
mapper answers with an empty panel and `supported: False`, which is a
working state — the planner still records the plan.
"""
from __future__ import annotations

from .collect import chosen, pool_for, raw_lines, sheet  # noqa: F401
from .damage import Hit, between, hits  # noqa: F401
from .games import module_for  # noqa: F401
from .model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution, Pool, Total, worst  # noqa: F401
from .vocabulary import GROUPS, STATS, Stat, grouped, stat  # noqa: F401

__all__ = ["sheet", "hits", "Hit", "between", "pool_for", "chosen", "raw_lines", "module_for", "Pool", "Total", "Contribution",
           "COUNTED", "APPROXIMATE", "NOT_COUNTED", "worst", "STATS", "Stat", "stat", "grouped", "GROUPS"]
