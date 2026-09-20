# SPDX-License-Identifier: AGPL-3.0-only
"""
Build the game database from the research packs.

A pack is a folder `research/<game>/` of JSON files in the shapes the brief
asked for, plus `sources-*.md` and `coverage-*.md` saying where the facts
came from and what was not found. Loading is forgiving on purpose: eight
researchers writing to one brief will differ in small ways, and a field
under a slightly different name must land in the right column rather than
fail the whole game. What cannot be placed is REPORTED, never dropped
silently — the report is the loader's second output, and the pack row keeps
it so an admin page can show what the data knows about itself.

The database is built fresh into a temporary file and moved into place, so
a reader never sees a half-built one.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .schema import DDL, FILES, LINKS

SUMMARY_KEYS = ("summary", "effect_summary", "mechanic_summary", "effect", "description")
GROUP_KEYS = ("group", "board_id", "tab_id", "tab", "tree_id", "category", "manual_id", "manual", "item_class", "family", "tier", "act")
LEVEL_KEYS = ("level_req", "required_level", "req_level", "level", "item_level")
SUB_KEYS = ("kind", "rarity", "type", "quality")
MAX_SUMMARY = 400


@dataclass
class Report:
    games: dict[str, dict] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def game(self, game: str) -> dict:
        return self.games.setdefault(game, {"counts": {}, "problems": [], "files": []})

    def problem(self, game: str, text: str) -> None:
        self.game(game)["problems"].append(text)

    def text(self) -> str:
        lines: list[str] = []
        for game, g in self.games.items():
            total = sum(g["counts"].values())
            lines.append(f"{game}: {total} records in {len(g['files'])} files")
            for kind, n in sorted(g["counts"].items()):
                lines.append(f"  {kind:<15} {n:>6}")
            if g["problems"]:
                lines.append(f"  problems: {len(g['problems'])}")
                lines.extend(f"    - {p}" for p in g["problems"][:40])
                if len(g["problems"]) > 40:
                    lines.append(f"    … and {len(g['problems']) - 40} more")
        lines.extend(f"! {p}" for p in self.problems)
        return "\n".join(lines) + "\n"


# ── small readers ────────────────────────────────────────────────────────────

def slug(value: Any, limit: int = 80) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return s[:limit]


def _ids(value: Any) -> list[str]:
    """One id, a list of ids, a list of records with ids, or nothing."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [] if value.strip().lower() in ("any", "all", "none", "*") else [value.strip()]
    if isinstance(value, dict):
        return [str(value["id"])] if value.get("id") else []
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(_ids(v))
        return out
    return [str(value)]


def _first(record: dict, keys: Iterable[str]) -> Any:
    for k in keys:
        v = record.get(k)
        if v not in (None, "", [], {}):
            return v
    return None


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        m = re.search(r"-?\d+", value)
        return int(m.group()) if m else None
    return None


def _text(value: Any, limit: int) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return ""
    return str(value).strip()[:limit]


def _class_ids(record: dict) -> list[str]:
    for k in ("class_ids", "class_id", "classes", "class", "class_restriction", "class_restrictions"):
        if k in record:
            return [slug(c) for c in _ids(record[k]) if slug(c)]
    return []


def _slot(record: dict) -> tuple[str, list[str]]:
    v = _first(record, ("slot_id", "slot", "slot_ids", "slots", "item_slot"))
    ids = [slug(s) for s in _ids(v) if slug(s)]
    return (ids[0] if ids else ""), ids


# ── the nested records a file carries ────────────────────────────────────────

def _records(kind: str, payload: Any, game: str, report: Report) -> list[tuple[str, dict]]:
    """
    Every (kind, record) a file yields, nested ones included:
      classes.json   → class, and each class's specializations
      tree.json      → tree, and its boards / glyphs / tabs / starts
      tempering.json → tempering (manual), and any affix listed inside it
      progression.json → one progression record per top-level section
    """
    out: list[tuple[str, dict]] = []
    if kind == "progression" and isinstance(payload, dict):
        for key, value in payload.items():
            if key in ("id", "name", "game", "notes", "sources"):
                continue
            rec = dict(value) if isinstance(value, dict) else {"value": value}
            rec.setdefault("id", slug(key))
            rec.setdefault("name", key.replace("_", " ").replace("-", " ").strip().capitalize())
            out.append(("progression", rec))
        return out
    if kind == "tree" and isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        report.problem(game, f"{kind}: the file is not a list of records")
        return out
    for rec in payload:
        if not isinstance(rec, dict):
            continue
        if kind == "class":
            specs = rec.get("specializations")
            if isinstance(specs, list):
                for s in specs:
                    if isinstance(s, dict):
                        s = dict(s)
                        s["class_ids"] = [slug(rec.get("id") or rec.get("name"))]
                        out.append(("specialization", s))
            out.append(("class", rec))
        elif kind == "tree":
            rest = dict(rec)
            for key, sub_kind in (("boards", "board"), ("glyphs", "glyph"), ("tabs", "tab"), ("starts", "start")):
                items = rest.pop(key, None)
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict):
                            it = dict(it)
                            it.setdefault("tree_id", slug(rest.get("id") or rest.get("kind") or "tree"))
                            if key == "starts":
                                it.setdefault("kind", "start")
                                out.append(("node", it))
                            else:
                                out.append((sub_kind, it))
            rest.setdefault("id", slug(rest.get("kind") or "tree"))
            rest.setdefault("name", str(rest.get("kind") or "tree").replace("-", " ").capitalize())
            out.append(("tree", rest))
        elif kind == "tempering":
            affixes = rec.get("affixes")
            if isinstance(affixes, list) and affixes and isinstance(affixes[0], dict):
                for a in affixes:
                    a = dict(a)
                    a.setdefault("kind", "tempering")
                    a["manual_id"] = slug(rec.get("id") or rec.get("name"))
                    if not a.get("slot_ids") and rec.get("slot_ids"):
                        a["slot_ids"] = rec["slot_ids"]
                    if not _class_ids(a) and _class_ids(rec):
                        a["class_ids"] = rec.get("class_ids") or rec.get("class_id")
                    out.append(("affix", a))
                rec = dict(rec)
                rec["affix_ids"] = [slug(a.get("id") or a.get("name")) for a in affixes if isinstance(a, dict)]
            out.append(("tempering", rec))
        elif kind == "skill":
            rec = dict(rec)
            ups = rec.get("upgrades")
            if isinstance(ups, list) and ups and isinstance(ups[0], dict):
                for u in ups:
                    if isinstance(u, dict) and not u.get("id"):
                        u["id"] = slug(u.get("name"))
                rec["upgrade_ids"] = [u["id"] for u in ups if isinstance(u, dict) and u.get("id")]
            syn = rec.get("synergies")
            if isinstance(syn, list) and syn:
                rec["synergy_ids"] = [slug(s.get("skill_id") or s.get("id") or s.get("skill")) if isinstance(s, dict) else slug(s) for s in syn]
                rec["synergy_ids"] = [s for s in rec["synergy_ids"] if s]
            out.append(("skill", rec))
        elif kind == "set":
            rec = dict(rec)
            pieces = rec.get("pieces") or rec.get("items")
            if isinstance(pieces, list):
                rec["piece_ids"] = [slug(p.get("id") or p.get("unique_id") or p.get("name")) if isinstance(p, dict) else slug(p) for p in pieces]
            out.append(("set", rec))
        elif kind == "runeword":
            rec = dict(rec)
            runes = rec.get("runes") or rec.get("rune_ids")
            if isinstance(runes, list):
                rec["rune_ids"] = [slug(r.get("id") or r.get("name")) if isinstance(r, dict) else slug(r) for r in runes]
            out.append(("runeword", rec))
        elif kind == "mercenary":
            rec = dict(rec)
            skills = rec.get("skills")
            if isinstance(skills, list) and skills and isinstance(skills[0], dict):
                for s in skills:
                    if not s.get("id"):
                        s["id"] = slug(s.get("name"))
            out.append(("mercenary", rec))
        else:
            out.append((kind, rec))
    return out


# ── the columns a record is filed under ──────────────────────────────────────

def normalise(kind: str, rec: dict, position: int) -> dict | None:
    rid = slug(rec.get("id") or rec.get("name"))
    if not rid:
        return None
    name = _text(rec.get("name"), 160) or rid
    sub = slug(_first(rec, SUB_KEYS)) if kind not in ("class", "slot") else ""
    if kind == "tree":
        sub = slug(rec.get("kind"))
    grp = _text(_first(rec, GROUP_KEYS), 80)
    slot_id, slot_ids = _slot(rec)
    tags = [str(t)[:40] for t in (rec.get("tags") or []) if isinstance(t, (str, int))] if isinstance(rec.get("tags"), list) else []
    level = _int(_first(rec, LEVEL_KEYS))
    summary = _text(_first(rec, SUMMARY_KEYS), MAX_SUMMARY)
    data = dict(rec)
    data["id"] = rid
    if slot_ids and "slot_ids" not in data:
        data["slot_ids"] = slot_ids
    return {"kind": kind, "id": rid, "name": name, "sub": sub, "grp": grp, "class_ids": _class_ids(rec), "slot_id": slot_id,
            "tags": tags, "level_req": level, "summary": summary, "position": position, "data": data}


def _links_of(game: str, row: dict) -> list[tuple]:
    out: list[tuple] = []
    data = row["data"]
    for fld, rel, to_kind in LINKS.get(row["kind"], ()):
        if fld == "class_ids":
            targets = row["class_ids"]
        else:
            targets = [slug(t) for t in _ids(data.get(fld)) if slug(t)]
        for t in targets:
            if t and not (to_kind == row["kind"] and t == row["id"]):
                out.append((game, row["kind"], row["id"], rel, to_kind, t, ""))
    if row["slot_id"] and row["kind"] not in ("slot",) and not any(l[3] == "fits" for l in out):
        out.append((game, row["kind"], row["id"], "fits", "slot", row["slot_id"], ""))
    return list(dict.fromkeys(out))      # a field and its alias name the same link once


# ── the build itself ─────────────────────────────────────────────────────────

def _read_json(path: Path, game: str, report: Report) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.problem(game, f"{path.name}: unreadable ({type(exc).__name__}: {str(exc)[:80]})")
        return None


def load_game(con: sqlite3.Connection, folder: Path, report: Report) -> str | None:
    game_json = folder / "game.json"
    game_meta = _read_json(game_json, folder.name, report) if game_json.exists() else {}
    if not isinstance(game_meta, dict):
        game_meta = {}
    game = slug(game_meta.get("id") or folder.name)
    g = report.game(game)
    seen: set[tuple[str, str]] = set()
    links: list[tuple] = []
    rows: list[dict] = []
    for filename, kind in FILES.items():
        path = folder / filename
        if not path.exists():
            continue
        payload = _read_json(path, game, report)
        if payload is None:
            continue
        g["files"].append(filename)
        for pos, (k, rec) in enumerate(_records(kind, payload, game, report)):
            row = normalise(k, rec, pos)
            if row is None:
                report.problem(game, f"{filename}: a {k} record without id or name was skipped")
                continue
            key = (row["kind"], row["id"])
            if key in seen:
                report.problem(game, f"{filename}: duplicate {row['kind']} id '{row['id']}' — first kept")
                continue
            seen.add(key)
            rows.append(row)
    con.executemany(
        "INSERT INTO entity (game, kind, id, name, sub, grp, class_ids, slot_id, tags, level_req, summary, position, data) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(game, r["kind"], r["id"], r["name"], r["sub"], r["grp"], json.dumps(r["class_ids"]), r["slot_id"], json.dumps(r["tags"]),
          r["level_req"], r["summary"], r["position"], json.dumps(r["data"], ensure_ascii=False, separators=(",", ":"))) for r in rows])
    for r in rows:
        links.extend(_links_of(game, r))
    con.executemany("INSERT INTO link (game, from_kind, from_id, rel, to_kind, to_id, note) VALUES (?, ?, ?, ?, ?, ?, ?)", links)
    # dangling links are reported, and kept: a pack fixed later makes them whole
    dangling = con.execute(
        "SELECT l.from_kind, l.from_id, l.rel, l.to_kind, l.to_id FROM link l LEFT JOIN entity e "
        "ON e.game = l.game AND e.kind = l.to_kind AND e.id = l.to_id WHERE l.game = ? AND e.n IS NULL", (game,)).fetchall()
    by_rel: dict[str, int] = {}
    for fk, fid, rel, tk, tid in dangling:
        by_rel[f"{fk}→{rel}→{tk}"] = by_rel.get(f"{fk}→{rel}→{tk}", 0) + 1
        if by_rel[f"{fk}→{rel}→{tk}"] <= 3:
            report.problem(game, f"{fk} '{fid}' {rel} {tk} '{tid}', which is not in the pack")
    for rel, n in by_rel.items():
        if n > 3:
            report.problem(game, f"{rel}: {n} links point at records not in the pack")
    for path in sorted(folder.glob("*.md")):
        try:
            con.execute("INSERT OR REPLACE INTO source (game, facet, body) VALUES (?, ?, ?)", (game, path.stem, path.read_text(encoding="utf-8")))
        except OSError:
            report.problem(game, f"{path.name}: unreadable")
    counts = dict(con.execute("SELECT kind, COUNT(*) FROM entity WHERE game = ? GROUP BY kind", (game,)).fetchall())
    g["counts"] = counts
    con.execute(
        "INSERT OR REPLACE INTO pack (game, name, patch, season, researched_at, level_cap, notes, loaded_at, counts, problems) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (game, _text(game_meta.get("name"), 80) or game, _text(game_meta.get("patch"), 80), _text(game_meta.get("season") or game_meta.get("league"), 80),
         _text(game_meta.get("researched_at"), 40), _int(game_meta.get("level_cap")), _text(game_meta.get("notes"), 1000),
         datetime.now(timezone.utc).isoformat(timespec="seconds"), json.dumps(counts), json.dumps(g["problems"][:200])))
    return game


def build_database(research_root: Path | str, db_path: Path | str, games: list[str] | None = None) -> Report:
    """
    Every game folder under `research_root` that holds a `game.json` (or any
    pack file) becomes a pack in a fresh database at `db_path`. Returns the
    report; the database is only moved into place when the build finished.
    """
    root, target = Path(research_root), Path(db_path)
    report = Report()
    folders = [p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
               and any((p / f).exists() for f in ("game.json", *FILES))]
    if games:
        folders = [p for p in folders if p.name in games]
    if not folders:
        report.problems.append(f"no packs under {root}")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".gamedata-", suffix=".sqlite3", dir=str(target.parent))
    os.close(fd)
    try:
        con = sqlite3.connect(tmp)
        con.executescript(DDL)
        for folder in folders:
            load_game(con, folder, report)
        con.execute("INSERT INTO entity_fts (entity_fts) VALUES ('rebuild')")
        con.commit()
        con.execute("VACUUM")
        con.close()
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return report
