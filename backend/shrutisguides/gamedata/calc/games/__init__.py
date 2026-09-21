# SPDX-License-Identifier: AGPL-3.0-only
"""One module per game: its own words, mapped into the vocabulary."""
from __future__ import annotations

from . import diablo_ii_resurrected

MODULES = {m.GAME: m for m in (diablo_ii_resurrected,)}


def module_for(game: str):
    """The mapper for a game, or nothing — a game without one has no numbers yet, which is a working state."""
    return MODULES.get(game)
