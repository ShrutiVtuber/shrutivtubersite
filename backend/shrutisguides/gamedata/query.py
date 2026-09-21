# SPDX-License-Identifier: AGPL-3.0-only
"""
Read the game database.

One class, opened read-only per call so nothing holds a handle across
requests. Records come back as their whole JSON with the filed columns laid
over it; lists can be `brief` — the columns only — because a passive tree
has thousands of nodes and a chooser needs names, not everything.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

BRIEF = ("kind", "id", "name", "sub", "group", "class_ids", "slot_id", "tags", "level_req", "summary")
MAX_LIMIT = 5000


def _row(r: sqlite3.Row, brief: bool = False) -> dict:
    cols = {"kind": r["kind"], "id": r["id"], "name": r["name"], "sub": r["sub"], "group": r["grp"],
            "class_ids": json.loads(r["class_ids"] or "[]"), "slot_id": r["slot_id"], "tags": json.loads(r["tags"] or "[]"),
            "level_req": r["level_req"], "summary": r["summary"]}
    if brief:
        return cols
    data = json.loads(r["data"] or "{}")
    data.pop("kind", None)
    return {**data, **cols}


def fts_query(q: str) -> str:
    """A person's words as a prefix match on each, safe for FTS5."""
    words = [w for w in re.findall(r"[^\W_]+", str(q or "").lower()) if w]
    return " ".join(f'"{w}"*' for w in words[:8])


class GameData:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def exists(self) -> bool:
        """There, and readable by this process — an unreadable file is "not loaded", not a crash."""
        return self.path.is_file() and os.access(self.path, os.R_OK)

    # ⚠ Every reader guards on `exists` first. A game whose data is not loaded
    # is a working state — the planner still records a plan — and the promise
    # only holds if asking for a record answers with nothing rather than
    # throwing on a file that is not there.
    def _con(self) -> sqlite3.Connection:
        con = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        return con

    # ── packs ────────────────────────────────────────────────────────────

    def games(self) -> list[dict]:
        if not self.exists():
            return []
        with self._con() as con:
            rows = con.execute("SELECT * FROM pack ORDER BY name").fetchall()
        return [self._pack(r) for r in rows]

    def game(self, game: str) -> dict | None:
        if not self.exists():
            return None
        with self._con() as con:
            r = con.execute("SELECT * FROM pack WHERE game = ?", (game,)).fetchone()
        return self._pack(r) if r else None

    @staticmethod
    def _pack(r: sqlite3.Row) -> dict:
        return {"id": r["game"], "name": r["name"], "patch": r["patch"], "season": r["season"], "researched_at": r["researched_at"],
                "level_cap": r["level_cap"], "notes": r["notes"], "loaded_at": r["loaded_at"],
                "counts": json.loads(r["counts"] or "{}"), "problems": json.loads(r["problems"] or "[]")}

    def kinds(self, game: str) -> dict[str, int]:
        if not self.exists():
            return {}
        with self._con() as con:
            return dict(con.execute("SELECT kind, COUNT(*) FROM entity WHERE game = ? GROUP BY kind", (game,)).fetchall())

    # ── entities ─────────────────────────────────────────────────────────

    def list(self, game: str, kind: str, *, sub: str | list[str] | None = None, class_id: str | None = None, slot_id: str | None = None,
             group: str | None = None, tag: str | None = None, ids: list[str] | None = None, q: str | None = None,
             limit: int = 500, offset: int = 0, brief: bool = False) -> list[dict]:
        """
        The records of one kind, filtered. `class_id` keeps records for that
        class AND records for any class; `q` is a prefix search on names.
        """
        if not self.exists():
            return []
        where = ["e.game = ?", "e.kind = ?"]
        args: list[Any] = [game, kind]
        if sub:
            subs = [sub] if isinstance(sub, str) else list(sub)
            where.append("e.sub IN (%s)" % ",".join("?" * len(subs)))
            args.extend(subs)
        if class_id:
            where.append("(e.class_ids = '[]' OR EXISTS (SELECT 1 FROM json_each(e.class_ids) WHERE value = ?))")
            args.append(class_id)
        if slot_id:
            # In the slot itself, or linked to it by name. Failing that — and ONLY
            # failing that — through an item type the slot accepts, which is how a
            # record that names a kind of item rather than a place on the body
            # ("rolls on a bow", "any armour") finds its slots.
            #
            # ⚠ The hop is a fallback because item types group broadly: a helm and
            # a chest piece are both "armor", so reaching through the type as well
            # as the slot would offer a helm for the chest. A record that states
            # its own slot has said all there is to say.
            direct = ("e.slot_id = ? OR EXISTS (SELECT 1 FROM link l WHERE l.game = e.game AND l.from_kind = e.kind AND l.from_id = e.id "
                      "AND l.rel IN ('fits', 'rolls-on') AND l.to_kind = 'slot' AND l.to_id = ?)")
            through = ("e.slot_id = '' AND EXISTS (SELECT 1 FROM link l WHERE l.game = e.game AND l.from_kind = e.kind AND l.from_id = e.id "
                       "AND l.rel IN ('fits', 'rolls-on', 'is-a') AND l.to_kind = 'itemtype' AND EXISTS ("
                       "SELECT 1 FROM link t WHERE t.game = l.game AND t.from_kind = 'itemtype' AND t.from_id = l.to_id AND t.rel = 'fits' AND t.to_id = ?))")
            where.append(f"(({direct}) OR ({through}))")
            args.extend([slot_id, slot_id, slot_id])
        if group:
            where.append("e.grp = ?")
            args.append(group)
        if tag:
            where.append("EXISTS (SELECT 1 FROM json_each(e.tags) WHERE value = ?)")
            args.append(tag)
        if ids is not None:
            if not ids:
                return []
            where.append("e.id IN (%s)" % ",".join("?" * len(ids[:MAX_LIMIT])))
            args.extend(ids[:MAX_LIMIT])
        join = ""
        order = "e.position, e.n"
        if q and fts_query(q):
            join = "JOIN entity_fts f ON f.rowid = e.n"
            where.append("entity_fts MATCH ?")
            args.append(fts_query(q))
            order = "bm25(entity_fts), e.position"
        sql = f"SELECT e.* FROM entity e {join} WHERE {' AND '.join(where)} ORDER BY {order} LIMIT ? OFFSET ?"
        args.extend([max(1, min(MAX_LIMIT, int(limit))), max(0, int(offset))])
        with self._con() as con:
            return [_row(r, brief) for r in con.execute(sql, args).fetchall()]

    def get(self, game: str, kind: str, id: str) -> dict | None:
        if not self.exists():
            return None
        with self._con() as con:
            r = con.execute("SELECT * FROM entity WHERE game = ? AND kind = ? AND id = ?", (game, kind, id)).fetchone()
        return _row(r) if r else None

    def names(self, game: str, kind: str, ids: list[str]) -> dict[str, str]:
        if not ids or not self.exists():
            return {}
        with self._con() as con:
            rows = con.execute("SELECT id, name FROM entity WHERE game = ? AND kind = ? AND id IN (%s)" % ",".join("?" * len(ids[:MAX_LIMIT])),
                               (game, kind, *ids[:MAX_LIMIT])).fetchall()
        return {r["id"]: r["name"] for r in rows}

    def exists_id(self, game: str, kind: str, id: str, sub: str | list[str] | None = None, class_id: str | None = None,
                  slot_id: str | None = None) -> bool:
        return bool(self.list(game, kind, ids=[id], sub=sub, class_id=class_id, slot_id=slot_id, limit=1, brief=True))

    def search(self, game: str, q: str, kinds: list[str] | None = None, class_id: str | None = None, limit: int = 40) -> list[dict]:
        match = fts_query(q)
        if not match or not self.exists():
            return []
        where = ["e.game = ?", "entity_fts MATCH ?"]
        args: list[Any] = [game, match]
        if kinds:
            where.append("e.kind IN (%s)" % ",".join("?" * len(kinds)))
            args.extend(kinds)
        if class_id:
            where.append("(e.class_ids = '[]' OR EXISTS (SELECT 1 FROM json_each(e.class_ids) WHERE value = ?))")
            args.append(class_id)
        args.append(max(1, min(200, int(limit))))
        with self._con() as con:
            rows = con.execute(f"SELECT e.* FROM entity e JOIN entity_fts f ON f.rowid = e.n WHERE {' AND '.join(where)} "
                               "ORDER BY bm25(entity_fts) LIMIT ?", args).fetchall()
        return [_row(r, brief=True) for r in rows]

    def links(self, game: str, kind: str, id: str, rel: str | None = None, direction: str = "out") -> list[dict]:
        """What this record points at (out), or what points at it (in), with the other end's name."""
        if not self.exists():
            return []
        if direction == "in":
            sql = ("SELECT l.rel, l.from_kind AS kind, l.from_id AS id, l.note, e.name FROM link l LEFT JOIN entity e "
                   "ON e.game = l.game AND e.kind = l.from_kind AND e.id = l.from_id WHERE l.game = ? AND l.to_kind = ? AND l.to_id = ?")
        else:
            sql = ("SELECT l.rel, l.to_kind AS kind, l.to_id AS id, l.note, e.name FROM link l LEFT JOIN entity e "
                   "ON e.game = l.game AND e.kind = l.to_kind AND e.id = l.to_id WHERE l.game = ? AND l.from_kind = ? AND l.from_id = ?")
        args: list[Any] = [game, kind, id]
        if rel:
            sql += " AND l.rel = ?"
            args.append(rel)
        with self._con() as con:
            rows = con.execute(sql + " ORDER BY l.rowid", args).fetchall()
        return [{"rel": r["rel"], "kind": r["kind"], "id": r["id"], "name": r["name"], "note": r["note"]} for r in rows]

    def groups(self, game: str, kind: str, class_id: str | None = None) -> list[dict]:
        """The clusters a kind falls into (skill groups, boards, item classes), with counts."""
        if not self.exists():
            return []
        where, args = ["game = ?", "kind = ?", "grp != ''"], [game, kind]
        if class_id:
            where.append("(class_ids = '[]' OR EXISTS (SELECT 1 FROM json_each(entity.class_ids) WHERE value = ?))")
            args.append(class_id)
        with self._con() as con:
            rows = con.execute(f"SELECT grp, COUNT(*) AS n FROM entity WHERE {' AND '.join(where)} GROUP BY grp ORDER BY MIN(position)", args).fetchall()
        return [{"group": r["grp"], "count": r["n"]} for r in rows]

    def sources(self, game: str) -> dict[str, str]:
        if not self.exists():
            return {}
        with self._con() as con:
            return {r["facet"]: r["body"] for r in con.execute("SELECT facet, body FROM source WHERE game = ? ORDER BY facet", (game,)).fetchall()}
