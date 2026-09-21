# SPDX-License-Identifier: AGPL-3.0-only
"""
What a build of each game is made of — the recipe a planner follows.

A recipe lists SECTIONS. Each says what kind of record it draws from, how
many may be chosen, which fields a choice carries (ranks, a level, the
supports on a gem, the aspect on a helm), and how the choice is tracked once
the build exists: a slot to fill, a counter to reach, a thing to tick. The
three games are three recipes over one database, and a fourth game is a
fourth recipe.

Field types:
  id      one record of `kind` (optionally of `sub`), class-checked when the kind carries classes
  ids     a list of those, at most `max`
  int     a number between `min` and `max`, shown with `unit`
  choice  one of `options`
  text    the person's own words, at most 120 characters
  within  ids drawn from a list INSIDE the chosen record (a skill's upgrades)

Section types:
  pick     one id                         → one check
  picks    a list of {id, …fields}        → a check per pick, or a counter when `track` names an int field
  gear     {slot_id: {…fields}}           → the grid: one slot per chosen slot, the choice written as its target
  targets  {entry_id: int}                → one counter per entry set

The names here are defaults: the site shows them through its copy editor.
"""
from __future__ import annotations

from copy import deepcopy

D4 = {
    "game": "diablo-iv",
    "sections": [
        {"id": "spec", "name": "Specialization", "type": "picks", "kind": "specialization", "by_class": True, "max": 16, "track": "check",
         "fields": {"note": {"type": "text"}}},
        {"id": "skills", "name": "Skills", "type": "picks", "kind": "skill", "by_class": True, "max": 24, "track": "check",
         "sub": ["active", "ultimate"],        # the class-mechanic passives are the Specialization section's
         "fields": {"ranks": {"type": "int", "min": 1, "max": 5, "unit": "ranks"}, "upgrades": {"type": "within", "list": "upgrades", "max": 3}},
         "points": {"id": "skill-points", "name": "Skill points", "field": "ranks", "unit": "points"}},
        {"id": "gear", "name": "Gear", "type": "gear", "grid": True, "exclude": ["socket-gem", "charm", "seal"],
         "fields": {"unique": {"type": "id", "kind": "unique"}, "base": {"type": "id", "kind": "base"}, "aspect": {"type": "id", "kind": "aspect"},
                    "affixes": {"type": "ids", "kind": "affix", "sub": "affix", "max": 4}, "greater": {"type": "ids", "kind": "affix", "sub": "affix", "max": 3},
                    "tempers": {"type": "ids", "kind": "affix", "sub": "tempering", "max": 2}, "gems": {"type": "ids", "kind": "gem", "max": 2},
                    "runes": {"type": "ids", "kind": "rune", "max": 2}, "runeword": {"type": "id", "kind": "runeword"},
                    "masterwork": {"type": "int", "min": 0, "max": 12, "unit": "masterwork"},
                    # ⚠ A weapon's damage is an item-power band in this game, so a
                    # plan that wants a damage number has to say which power it means
                    "item_power": {"type": "int", "min": 1, "max": 1000, "unit": "item power"},
                    "note": {"type": "text"}}},
        {"id": "charms", "name": "Charms", "type": "picks", "kind": "charm", "by_class": True, "max": 12, "track": "check",
         "fields": {"note": {"type": "text"}}},
        {"id": "paragon", "name": "Paragon", "type": "picks", "kind": "board", "by_class": True, "max": 8, "track": "check",
         "fields": {"glyph": {"type": "id", "kind": "glyph"}, "note": {"type": "text"}}},
        {"id": "glyphs", "name": "Glyphs", "type": "picks", "kind": "glyph", "by_class": True, "max": 8, "track": "level",
         "fields": {"level": {"type": "int", "min": 1, "max": 100, "unit": "level"}}},
        {"id": "mercenary", "name": "Mercenary", "type": "picks", "kind": "mercenary", "max": 2, "track": "check",
         "fields": {"role": {"type": "choice", "options": ["hired", "reinforcement"]}, "skill": {"type": "within", "list": "skills", "max": 3}}},
        {"id": "targets", "name": "Numbers", "type": "targets",
         "entries": [{"id": "level", "name": "Level", "max": 70, "unit": "levels"},
                     {"id": "paragon-points", "name": "Paragon points", "max": 342, "unit": "points"},
                     {"id": "renown", "name": "Renown skill points", "max": 10, "unit": "points"}]},
    ],
}

POE2 = {
    "game": "path-of-exile-2",
    "sections": [
        {"id": "ascendancy", "name": "Ascendancy", "type": "pick", "kind": "specialization", "by_class": True},
        {"id": "skills", "name": "Skill gems", "type": "picks", "kind": "skill", "by_class": False, "max": 12, "track": "check",
         "sub": ["active", "meta", "buff", "persistent", "spirit"],
         "fields": {"supports": {"type": "ids", "kind": "skill", "sub": "support", "max": 5},
                    "level": {"type": "int", "min": 1, "max": 20, "unit": "gem level"}, "quality": {"type": "int", "min": 0, "max": 20, "unit": "quality"}}},
        {"id": "passives", "name": "Passives", "type": "picks", "kind": "node", "by_class": False, "max": 60, "track": "check",
         "sub": ["notable", "keystone", "mastery", "ascendancy"],
         "fields": {"note": {"type": "text"}},
         "points": {"id": "passive-points", "name": "Passive points", "unit": "points"}},
        {"id": "gear", "name": "Gear", "type": "gear", "grid": True, # flasks, charms and jewels have their own sections; the socket "slots" are
         # not places on the body; the transcendent limbs are a temporary device's
         "exclude": ["flask", "charm", "jewel-socket", "rune-socket", "transcendent-arm", "transcendent-leg"],
         "fields": {"unique": {"type": "id", "kind": "unique"}, "base": {"type": "id", "kind": "base"},
                    "affixes": {"type": "ids", "kind": "affix", "sub": ["prefix", "suffix", "exclusive"], "max": 6},
                    "runes": {"type": "ids", "kind": "rune", "max": 3},
                    "quality": {"type": "int", "min": 0, "max": 30, "unit": "quality"}, "note": {"type": "text"}}},
        {"id": "flasks", "name": "Flasks", "type": "picks", "kind": "flask", "max": 2, "track": "check", "fields": {"note": {"type": "text"}}},
        {"id": "charms", "name": "Charms", "type": "picks", "kind": "charm", "max": 3, "track": "check", "fields": {"note": {"type": "text"}}},
        {"id": "jewels", "name": "Jewels", "type": "picks", "kind": "jewel", "max": 8, "track": "check", "fields": {"note": {"type": "text"}}},
        {"id": "targets", "name": "Numbers", "type": "targets",
         "entries": [{"id": "level", "name": "Level", "max": 100, "unit": "levels"},
                     {"id": "spirit", "name": "Spirit", "max": 400, "unit": "spirit"},
                     {"id": "resist-fire", "name": "Fire resistance", "max": 75, "unit": "%"},
                     {"id": "resist-cold", "name": "Cold resistance", "max": 75, "unit": "%"},
                     {"id": "resist-lightning", "name": "Lightning resistance", "max": 75, "unit": "%"},
                     {"id": "resist-chaos", "name": "Chaos resistance", "max": 75, "unit": "%"}]},
    ],
}

D2R = {
    "game": "diablo-ii-resurrected",
    "sections": [
        {"id": "skills", "name": "Skills", "type": "picks", "kind": "skill", "by_class": True, "max": 30, "track": "points",
         "fields": {"points": {"type": "int", "min": 1, "max": 20, "unit": "points"}},
         "points": {"id": "skill-points", "name": "Skill points", "field": "points", "unit": "points"}},
        {"id": "gear", "name": "Gear", "type": "gear", "grid": True,
         "exclude": ["socket", "inventory-charms", "mercenary-head", "mercenary-torso", "mercenary-weapon", "mercenary-off-hand"],
         "fields": {"runeword": {"type": "id", "kind": "runeword"}, "unique": {"type": "id", "kind": "unique"}, "base": {"type": "id", "kind": "base"},
                    "affixes": {"type": "ids", "kind": "affix", "sub": ["prefix", "suffix", "craft"], "max": 6},
                    "sockets": {"type": "ids", "kind": "rune", "max": 6}, "gems": {"type": "ids", "kind": "gem", "max": 6},
                    "jewels": {"type": "ids", "kind": "jewel", "max": 6}, "ethereal": {"type": "choice", "options": ["", "ethereal"]},
                    "note": {"type": "text"}}},
        {"id": "charms", "name": "Charms", "type": "picks", "kind": "charm", "max": 12, "track": "check", "fields": {"note": {"type": "text"}}},
        {"id": "mercenary", "name": "Mercenary", "type": "pick", "kind": "mercenary"},
        # the places are the mercenary's, the items are the ones a person wears
        {"id": "merc-gear", "name": "Mercenary gear", "type": "gear",
         "slots": {"mercenary-head": "head", "mercenary-torso": "torso", "mercenary-weapon": "weapon", "mercenary-off-hand": "off-hand"},
         "fields": {"runeword": {"type": "id", "kind": "runeword"}, "unique": {"type": "id", "kind": "unique"}, "base": {"type": "id", "kind": "base"},
                    "note": {"type": "text"}}},
        {"id": "targets", "name": "Numbers", "type": "targets",
         "entries": [{"id": "level", "name": "Level", "max": 99, "unit": "levels"},
                     {"id": "strength", "name": "Strength", "max": 500, "unit": "points"},
                     {"id": "dexterity", "name": "Dexterity", "max": 500, "unit": "points"},
                     {"id": "vitality", "name": "Vitality", "max": 500, "unit": "points"},
                     {"id": "energy", "name": "Energy", "max": 500, "unit": "points"},
                     {"id": "fcr", "name": "Faster cast rate", "max": 200, "unit": "%"},
                     {"id": "fhr", "name": "Faster hit recovery", "max": 200, "unit": "%"},
                     {"id": "ias", "name": "Increased attack speed", "max": 200, "unit": "%"},
                     {"id": "resist-all", "name": "Resistances in Hell", "max": 75, "unit": "%"}]},
    ],
}

RECIPES: dict[str, dict] = {r["game"]: r for r in (D4, POE2, D2R)}


def recipe_for(game: str) -> dict | None:
    r = RECIPES.get(game)
    return deepcopy(r) if r else None
