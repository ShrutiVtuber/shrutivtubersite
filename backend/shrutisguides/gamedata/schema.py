# SPDX-License-Identifier: AGPL-3.0-only
"""
The shape of the game database.

One table of ENTITIES holds every kind of thing — a skill, a unique, a
paragon node — with the handful of columns a planner filters on pulled out
(game, kind, class, slot, group, level) and the whole record kept as JSON
beside them, so a game with a shape the others lack loses nothing. One table
of LINKS holds what points at what (a skill's prerequisite, a node's
neighbours, a set's pieces, a runeword's runes, an affix's slots). A full-text
index answers "find me the thing called…". A PACK row per game says which
patch and season the facts describe and when they were gathered.

Three games with three different systems fit one schema because the schema
describes relationships, not rules: the rules live in each game's recipe.
"""
from __future__ import annotations

DDL = """
CREATE TABLE IF NOT EXISTS pack (
    game TEXT PRIMARY KEY, name TEXT NOT NULL, patch TEXT NOT NULL DEFAULT '', season TEXT NOT NULL DEFAULT '',
    researched_at TEXT NOT NULL DEFAULT '', level_cap INTEGER, notes TEXT NOT NULL DEFAULT '',
    loaded_at TEXT NOT NULL, counts TEXT NOT NULL DEFAULT '{}', problems TEXT NOT NULL DEFAULT '[]');

CREATE TABLE IF NOT EXISTS entity (
    n INTEGER PRIMARY KEY,
    game TEXT NOT NULL, kind TEXT NOT NULL, id TEXT NOT NULL, name TEXT NOT NULL,
    sub TEXT NOT NULL DEFAULT '',            -- the kind's own kind: active/passive, prefix/suffix, unique/mythic, notable/keystone
    grp TEXT NOT NULL DEFAULT '',            -- the cluster, tab, board, manual, item class, tier
    class_ids TEXT NOT NULL DEFAULT '[]',    -- JSON array; empty means any class
    slot_id TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',         -- JSON array
    level_req INTEGER,
    summary TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL DEFAULT 0,     -- the order the pack listed it in
    data TEXT NOT NULL,                      -- the whole record, JSON
    UNIQUE (game, kind, id));
CREATE INDEX IF NOT EXISTS entity_kind ON entity (game, kind, sub, slot_id);
CREATE INDEX IF NOT EXISTS entity_grp ON entity (game, kind, grp);

CREATE VIRTUAL TABLE IF NOT EXISTS entity_fts USING fts5 (name, summary, tags, content='entity', content_rowid='n', tokenize='unicode61');

CREATE TABLE IF NOT EXISTS link (
    game TEXT NOT NULL, from_kind TEXT NOT NULL, from_id TEXT NOT NULL, rel TEXT NOT NULL,
    to_kind TEXT NOT NULL, to_id TEXT NOT NULL, note TEXT NOT NULL DEFAULT '');
CREATE INDEX IF NOT EXISTS link_out ON link (game, from_kind, from_id, rel);
CREATE INDEX IF NOT EXISTS link_in ON link (game, to_kind, to_id, rel);

CREATE TABLE IF NOT EXISTS source (game TEXT NOT NULL, facet TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY (game, facet));
"""

# Every kind an entity can be. A file's records become one kind; some files
# hold several (a class carries its specializations, a tree its boards and
# glyphs), and those are split out on load.
KINDS = (
    "class", "specialization", "skill", "tree", "board", "tab", "node", "glyph",
    "slot", "base", "affix", "unique", "set", "runeword", "rune", "gem", "jewel", "charm", "flask",
    "aspect", "tempering", "mercenary", "progression",
)

# pack file → the kind its top-level records are. Nested records are handled
# by `load.py`'s splitters (see NESTED there).
FILES = {
    "classes.json": "class",
    "skills.json": "skill",
    "tree.json": "tree",
    "tree-nodes.json": "node",
    "slots.json": "slot",
    "bases.json": "base",
    "affixes.json": "affix",
    "uniques.json": "unique",
    "sets.json": "set",
    "runewords.json": "runeword",
    "runes.json": "rune",
    "gems.json": "gem",
    "jewels.json": "jewel",
    "charms.json": "charm",
    "flasks.json": "flask",
    "aspects.json": "aspect",
    "tempering.json": "tempering",
    "mercenaries.json": "mercenary",
    "progression.json": "progression",
}

# The relationships derived from a record's own fields: (field, rel, to_kind).
# A field may hold one id or a list of ids; a missing field is nothing.
LINKS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "specialization": (("class_ids", "of", "class"),),
    "skill": (("prerequisites", "requires", "skill"), ("synergy_ids", "synergy", "skill"), ("upgrade_ids", "upgrade", "skill"),
              ("class_ids", "of", "class")),
    "node": (("connections", "connects", "node"), ("board_id", "on", "board"), ("tree_id", "on", "tree"),
             ("ascendancy_id", "of", "specialization")),
    "glyph": (("class_ids", "of", "class"),),
    "board": (("class_ids", "of", "class"),),
    "base": (("slot_id", "fits", "slot"), ("slot_ids", "fits", "slot"), ("class_ids", "of", "class"),
             ("exceptional_id", "becomes", "base"), ("elite_id", "becomes", "base")),
    "affix": (("slot_ids", "rolls-on", "slot"), ("applies_to", "rolls-on", "slot"), ("class_ids", "of", "class"), ("manual_id", "from", "tempering")),
    "unique": (("base_id", "on", "base"), ("slot_id", "fits", "slot"), ("set_id", "in", "set"), ("class_ids", "of", "class")),
    "set": (("piece_ids", "piece", "unique"), ("pieces", "piece", "unique"), ("class_ids", "of", "class")),
    "runeword": (("rune_ids", "rune", "rune"), ("runes", "rune", "rune"), ("slot_ids", "fits", "slot"), ("base_types", "fits", "slot")),
    "aspect": (("slot_ids", "fits", "slot"), ("class_ids", "of", "class")),
    "tempering": (("affix_ids", "offers", "affix"), ("slot_ids", "fits", "slot"), ("class_ids", "of", "class")),
    "charm": (("class_ids", "of", "class"),),
    "mercenary": (("skill_ids", "has", "skill"),),
}
