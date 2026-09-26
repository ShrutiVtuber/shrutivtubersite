# SPDX-License-Identifier: AGPL-3.0-only
"""
/play, the games wing's front door (design handoff of 26 September 2026).

The hub is a map of rooms that already exist, so the ways it can go wrong are
all disagreements: a planner the hub does not know about, a hub that outlives
the wing it describes, a lockup that still opens the old door. Each is checked
against the thing it has to agree with.
"""
from __future__ import annotations

import re

from shruti.core import settings_store
from shrutisguides.gamedata.recipes import RECIPES
from test_marks_are_type_not_emoji import SRC

PAGE = SRC / "pages" / "play.astro"
LIB = SRC / "lib" / "play.ts"


def test_the_hub_knows_every_planner():
    """
    A planner whose data is not loaded is absent from /api/gamedata/games, so
    the hub keeps its own list in order to say "data not loaded yet" for it.
    That list has to be the backend's.
    """
    ids = re.findall(r'\{\s*id:\s*"([a-z0-9-]+)"', LIB.read_text(encoding="utf-8").split("PLANNER_GAMES", 1)[1].split("];", 1)[0])
    assert sorted(ids) == sorted(RECIPES), "lib/play.ts PLANNER_GAMES and gamedata RECIPES disagree"


def test_the_hub_is_hidden_with_the_wing():
    assert "/play" in settings_store.SECTION_PATHS["guides"]
    middleware = (SRC / "middleware.ts").read_text(encoding="utf-8")
    assert '"/play": "guides"' in middleware


def test_the_lockup_opens_the_hub_and_play_is_the_first_tab():
    nav = (SRC / "components" / "chrome" / "GuidesNav.astro").read_text(encoding="utf-8")
    assert 'class="gd-lockup" href="/play"' in nav
    tabs = re.findall(r'\["(/[^"]*)",\s*say\(', nav)
    assert tabs[0] == "/play"


def test_the_menu_group_heading_opens_the_hub():
    header = (SRC / "components" / "chrome" / "SiteHeader.astro").read_text(encoding="utf-8")
    assert re.search(r'group\.play[^\]]*\["/play", "/guides"', header), "Overview (/play) is the Play group's first item"
    assert 'class="site-menu-eyebrow site-menu-heading" href={overview}' in header


def test_the_hub_sells_nothing_and_counts_nobody():
    """No price, no hosting, no counts; hosting is sold on the account page only."""
    text = PAGE.read_text(encoding="utf-8")
    defaults = " ".join(re.findall(r'say\("[^"]+",\s*"((?:[^"\\]|\\.)*)"', text)).lower()
    for word in ("price", "hosting", "per month", "$", "streak", "badge", "new!"):
        assert word not in defaults, f"/play says {word!r}"
    assert "var(--live" not in text


def test_the_hub_has_one_h1():
    text = PAGE.read_text(encoding="utf-8")
    assert len(re.findall(r"<h1[\s>]", text)) == 1
