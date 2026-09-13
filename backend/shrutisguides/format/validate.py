# SPDX-License-Identifier: AGPL-3.0-only
"""
Whether a guide is well-formed — the schema, and then everything the schema
cannot say.

⚠ JSON Schema can say a step has a `phase`; it cannot say the phase exists.
It can say a gate key looks like `level_min`; it cannot say `level` is a
declared check-in field, or that it is a number rather than an ordered list.
Those are the mistakes an author — or an agent drafting through the MCP —
actually makes, and they are all here as `Problem`s with a path that points
at the offending thing.

Used by: the CLI (`python -m shrutisguides.format validate`), the authoring
API (a draft is validated on every save), the MCP (an agent is told exactly
what is wrong), and CI (the example guides must always validate).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema

SCHEMA_PATH = Path(__file__).with_name("schema.json")
BUILTIN_GATE_KEYS = {"variant", "steps_done", "codex_active"}
_GATE_KEY = re.compile(r"^([a-z][a-z0-9_]*)_(min|max|at_least|is)$")


@dataclass(frozen=True)
class Problem:
    """One thing wrong, and where."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate(guide: dict) -> list[Problem]:
    """
    Every problem with a guide. An empty list means it is good.

    ⚠ Schema problems come first and, if there are any, ALONE. The semantic
    checks assume the shape is right — a `steps` that is a string would make
    them crash rather than report, and a crash is not a validation result.
    """
    problems = list(_schema_problems(guide))
    if problems:
        return problems
    return list(_semantic_problems(guide))


def validate_file(path: str | Path) -> list[Problem]:
    try:
        guide = json.loads(Path(path).read_text())
    except json.JSONDecodeError as exc:
        return [Problem("$", f"not JSON: {exc}")]
    return validate(guide)


# ── the schema ───────────────────────────────────────────────────────────────

def _schema_problems(guide: Any) -> Iterable[Problem]:
    validator = jsonschema.Draft202012Validator(load_schema())
    for error in sorted(validator.iter_errors(guide), key=lambda e: list(e.absolute_path)):
        where = "$" + "".join(
            f"[{p}]" if isinstance(p, int) else f".{p}" for p in error.absolute_path
        )
        yield Problem(where, error.message)


# ── everything the schema cannot say ─────────────────────────────────────────

def _semantic_problems(g: dict) -> Iterable[Problem]:
    variants = {v["id"] for v in g["game"]["variants"]}
    yield from _unique("$.game.variants", (v["id"] for v in g["game"]["variants"]))

    fields = {f["id"]: f for f in g["checkin"]}
    yield from _unique("$.checkin", (f["id"] for f in g["checkin"]))
    for i, f in enumerate(g["checkin"]):
        where = f"$.checkin[{i}]"
        if f["type"] == "ordered" and not f.get("options"):
            yield Problem(where, f"ordered field '{f['id']}' declares no options")
        if f["type"] == "number" and f.get("options"):
            yield Problem(where, f"number field '{f['id']}' should not declare options")
        if "min" in f and "max" in f and f["min"] > f["max"]:
            yield Problem(where, f"'{f['id']}' has min {f['min']} above max {f['max']}")
        yield from _applies_to(where, f, variants)
        yield from _gate(where + ".show_when", f.get("show_when"), fields, variants, set(), set())

    phases = {p["id"]: p for p in g["phases"]}
    yield from _unique("$.phases", (p["id"] for p in g["phases"]))
    yield from _unique("$.phases (order)", (p["order"] for p in g["phases"]), what="order")
    tracks = {t["id"]: t for t in g.get("tracks", [])}
    for i, p in enumerate(g["phases"]):
        where = f"$.phases[{i}]"
        yield from _applies_to(where, p, variants)
        if "track" in p and p["track"] not in tracks:
            yield Problem(where, f"phase '{p['id']}' names track '{p['track']}', which does not exist")

    step_ids = [s["id"] for s in g["steps"]]
    steps = set(step_ids)
    codex_ids = {c["id"] for c in g.get("codex", [])}
    yield from _unique("$.steps", step_ids)

    for i, s in enumerate(g["steps"]):
        where = f"$.steps[{i}] ({s['id']})"
        if s["phase"] not in phases:
            yield Problem(where, f"phase '{s['phase']}' does not exist")
        if "codex" in s and s["codex"] not in codex_ids:
            yield Problem(where, f"codex entry '{s['codex']}' does not exist")
        yield from _applies_to(where, s, variants)
        yield from _gate(where + ".gate", s.get("gate"), fields, variants, steps, codex_ids)
        yield from _gate(where + ".auto_done", s.get("auto_done"), fields, variants, steps, codex_ids)
        if s.get("ongoing") and "minutes" in s:
            yield Problem(where, "a step is ongoing or timed, not both")
        if s.get("kind") == "routine":
            # ⚠ A routine step is a smell: routines have their own list, and a
            # step of kind routine would count nowhere and reset never.
            yield Problem(where, "kind 'routine' belongs in routines[], not steps[]")

    # Order within a phase must be unambiguous, or "the current step" is not
    # computable — it is the first available step in track order.
    for pid in phases:
        orders = [s["order"] for s in g["steps"] if s["phase"] == pid]
        yield from _unique(f"$.steps in phase {pid} (order)", orders, what="order")

    routine_ids = [r["id"] for r in g.get("routines", [])]
    yield from _unique("$.routines", routine_ids)
    for i, r in enumerate(g.get("routines", [])):
        where = f"$.routines[{i}] ({r['id']})"
        yield from _unique(where + ".items", (it["id"] for it in r["items"]))
        yield from _applies_to(where, r, variants)
        yield from _gate(where + ".gate", r.get("gate"), fields, variants, steps, codex_ids)

    yield from _unique("$.codex", codex_ids_list := [c["id"] for c in g.get("codex", [])])
    for i, c in enumerate(g.get("codex", [])):
        where = f"$.codex[{i}] ({c['id']})"
        yield from _gate(where + ".show_when", c.get("show_when"), fields, variants, steps, codex_ids)

    yield from _unique("$.codex_notes", (n["id"] for n in g.get("codex_notes", [])))

    yield from _unique("$.tracks", list(tracks))
    for i, t in enumerate(g.get("tracks", [])):
        where = f"$.tracks[{i}] ({t['id']})"
        yield from _applies_to(where, t, variants)
        for sid in t.get("day_one", []):
            if sid not in steps:
                yield Problem(where + ".day_one", f"step '{sid}' does not exist")
        yield from _unique(where + ".ranks", (r["n"] for r in t.get("ranks", [])), what="rank")
        yield from _unique(where + ".counters", (c["id"] for c in t.get("counters", [])))
        yield from _unique(where + ".sections", (s["id"] for s in t.get("sections", [])))
        if not any(p.get("track") == t["id"] for p in g["phases"]):
            yield Problem(where, f"no phase names track '{t['id']}', so it has no steps")


def _unique(where: str, ids: Iterable[Any], what: str = "id") -> Iterable[Problem]:
    seen: set[Any] = set()
    for i in ids:
        if i in seen:
            yield Problem(where, f"duplicate {what} '{i}'")
        seen.add(i)


def _applies_to(where: str, thing: dict, variants: set[str]) -> Iterable[Problem]:
    for v in thing.get("applies_to", []):
        if v not in variants:
            yield Problem(where + ".applies_to", f"'{v}' is not a variant of this game")


def _gate(
    where: str, gate: dict | None, fields: dict[str, dict], variants: set[str],
    steps: set[str], codex: set[str],
) -> Iterable[Problem]:
    """
    ⚠ The check that matters most, because it is the mistake an author makes
    most: a gate on a field that does not exist, or the wrong comparison for
    the field's type. `level_at_least` on a number field is meaningless;
    `difficulty_min` on an ordered field is too. Either one would make a
    step silently never available.
    """
    if not gate:
        return
    for key, value in gate.items():
        if key == "variant":
            wanted = value if isinstance(value, list) else [value]
            for v in wanted:
                if v not in variants:
                    yield Problem(f"{where}.variant", f"'{v}' is not a variant of this game")
            continue
        if key == "steps_done":
            for sid in (value if isinstance(value, list) else [value]):
                if sid not in steps:
                    yield Problem(f"{where}.steps_done", f"step '{sid}' does not exist")
            continue
        if key == "codex_active":
            for cid in (value if isinstance(value, list) else [value]):
                if cid not in codex:
                    yield Problem(f"{where}.codex_active", f"codex entry '{cid}' does not exist")
            continue

        m = _GATE_KEY.match(key)
        if not m:
            yield Problem(f"{where}.{key}", "not a gate key")
            continue
        field, op = m.group(1), m.group(2)
        if field not in fields:
            yield Problem(f"{where}.{key}", f"'{field}' is not a check-in field of this guide")
            continue
        ftype = fields[field]["type"]
        if op in ("min", "max"):
            if ftype != "number":
                yield Problem(f"{where}.{key}", f"'{field}' is ordered; use {field}_at_least or {field}_is")
            elif not isinstance(value, int):
                yield Problem(f"{where}.{key}", f"expected a number, got {value!r}")
        else:  # at_least / is
            if ftype != "ordered":
                yield Problem(f"{where}.{key}", f"'{field}' is a number; use {field}_min or {field}_max")
            elif value not in fields[field].get("options", []):
                yield Problem(f"{where}.{key}", f"'{value}' is not one of {field}'s options")
