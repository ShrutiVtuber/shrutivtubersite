# SPDX-License-Identifier: AGPL-3.0-only
"""
What changed between two bodies of a guide — by id, in the guide's own
terms: a step added, a phase renamed, a routine's item dropped. Not a line
diff of JSON; an author reads "step 3.2 — the do text changed" and knows
where to look.
"""
from __future__ import annotations

from typing import Any

LISTS = (
    ("phases", "phase", "name"),
    ("steps", "step", "title"),
    ("routines", "routine", "name"),
    ("codex", "codex entry", "title"),
    ("tracks", "track", "name"),
)
META = (("guide", "the guide"), ("game", "the game"))
LIMIT = 280


def _short(value: Any) -> Any:
    if isinstance(value, str):
        return value if len(value) <= LIMIT else value[:LIMIT] + "…"
    if isinstance(value, (list, dict)):
        text = str(value)
        return text if len(text) <= LIMIT else text[:LIMIT] + "…"
    return value


def _by_id(doc: dict, key: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for item in doc.get(key, []) or []:
        if isinstance(item, dict) and item.get("id") is not None:
            out[str(item["id"])] = item
    return out


def _fields(before: dict, after: dict) -> list[dict]:
    names = sorted(set(before) | set(after))
    out = []
    for name in names:
        if before.get(name) != after.get(name):
            out.append({"name": name, "before": _short(before.get(name)), "after": _short(after.get(name))})
    return out


def changes(before: dict, after: dict) -> list[dict]:
    """Every difference, as the guide names things. Empty means identical."""
    out: list[dict] = []
    for key, word in META:
        b, a = before.get(key) or {}, after.get(key) or {}
        if isinstance(b, dict) and isinstance(a, dict):
            fields = _fields(b, a)
            if fields:
                out.append({"kind": word, "id": "", "title": "", "change": "changed", "fields": fields})
    checkin_b, checkin_a = before.get("checkin") or {}, after.get("checkin") or {}
    if checkin_b != checkin_a:
        out.append({"kind": "check-in", "id": "", "title": "", "change": "changed",
                    "fields": _fields(checkin_b if isinstance(checkin_b, dict) else {}, checkin_a if isinstance(checkin_a, dict) else {})})
    for key, word, label in LISTS:
        b, a = _by_id(before, key), _by_id(after, key)
        for id_ in a:
            if id_ not in b:
                out.append({"kind": word, "id": id_, "title": str(a[id_].get(label, "")), "change": "added", "fields": []})
        for id_ in b:
            if id_ not in a:
                out.append({"kind": word, "id": id_, "title": str(b[id_].get(label, "")), "change": "removed", "fields": []})
        for id_ in a:
            if id_ in b and a[id_] != b[id_]:
                out.append({"kind": word, "id": id_, "title": str(a[id_].get(label, "") or b[id_].get(label, "")),
                            "change": "changed", "fields": _fields(b[id_], a[id_])})
    return out


def summary(items: list[dict]) -> dict[str, int]:
    """How many of each: the desk's one-line count."""
    out = {"added": 0, "removed": 0, "changed": 0}
    for item in items:
        out[item["change"]] = out.get(item["change"], 0) + 1
    return out
