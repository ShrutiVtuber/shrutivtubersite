# SPDX-License-Identifier: AGPL-3.0-only
"""
Builds: a set of goals for one character, tracked slot by slot.

A TEMPLATE says what a build of one game is made of — categories of items,
each a slot to fill, a counter to reach or a thing to tick. A BUILD is one
person's: the template with their own targets written in and how far they
have got. This module is the whole of the logic, shared by shrutivtuber.com
and the self-hosted tracker so the two cannot disagree: the template's
shape, the state of each goal, the progress, the plate's element, and the
paste grammar the admin reads a list with.

⚠ Nothing measures absence. A goal is met, partly met or not yet; there is
no "since", no rate, no percentage of a person. The one number on the
plate is met of total, which is a fact about the build.
"""
from __future__ import annotations

import re
from typing import Any

ITEM_KINDS = ("slot", "counter", "check")
STATES = ("open", "partial", "met")
MAX_CATEGORIES = 24
MAX_ITEMS = 60
MAX_COUNT = 1_000_000

GOAL_FIELDS = ("target", "note", "met", "partial", "have", "want")


# ── the template's shape ─────────────────────────────────────────────────────

def ident(value: Any, fallback: str) -> str:
    """A stable id from a label: lowercase, dashes, forty characters."""
    v = "".join(ch for ch in str(value or "").strip().lower().replace(" ", "-") if ch.isalnum() or ch in "-_")[:40]
    return v or fallback


def clean_categories(raw: Any) -> list[dict]:
    """
    [{id, name, grid, items: [{id, label, kind, hint, max, unit}]}], with
    unknown kinds becoming checks and ids made unique. One category per
    template may be the grid — the one whose slot labels the plate draws
    five to a row — and the first flagged keeps the flag.
    """
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    seen: set[str] = set()
    for ci, c in enumerate(raw[:MAX_CATEGORIES]):
        if not isinstance(c, dict):
            continue
        cid = ident(c.get("id") or c.get("name"), f"c{ci + 1}")
        while cid in seen:
            cid += "-2"
        seen.add(cid)
        items: list[dict] = []
        used: set[str] = set()
        for ii, it in enumerate((c.get("items") or [])[:MAX_ITEMS]):
            if not isinstance(it, dict):
                continue
            iid = ident(it.get("id") or it.get("label"), f"{cid}-{ii + 1}")
            while iid in used:
                iid += "-2"
            used.add(iid)
            kind = it.get("kind") if it.get("kind") in ITEM_KINDS else "check"
            try:
                mx = max(0, min(MAX_COUNT, int(it.get("max") or 0)))
            except (TypeError, ValueError):
                mx = 0
            items.append({"id": iid, "label": str(it.get("label") or iid)[:80], "kind": kind,
                          "hint": str(it.get("hint") or "")[:120], "max": mx, "unit": str(it.get("unit") or "")[:20]})
        out.append({"id": cid, "name": str(c.get("name") or cid)[:60], "items": items, "grid": bool(c.get("grid"))})
    seen_grid = False
    for c in out:
        if c["grid"] and not seen_grid:
            seen_grid = True
        else:
            c["grid"] = False
    return out


def known_items(categories: list[dict]) -> set[str]:
    return {it["id"] for c in categories or [] for it in c.get("items", [])}


# ── the paste grammar: four rules read a list ────────────────────────────────

_CATEGORY = re.compile(r"^(.+?):\s*$")
_CHECK = re.compile(r"^\[\s*[xX ]?\s*\]\s*(.+)$")
_COUNTER = re.compile(r"^(.+?)\s*=\s*(\d+)\s*(.*)$")
_SLOT = re.compile(r"^(.+?)\s+(?:—|–|-)\s+(.+)$")


def parse_list(text: str) -> list[dict]:
    """
    One category per block, one item per line:
        Category:               starts a category
        Label — hint            a slot, hint optional
        Label = 300 points      a counter, max and unit
        [ ] Label               a check
    The first category is the grid. Returns cleaned categories.
    """
    cats: list[dict] = []
    cat: dict | None = None
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _CATEGORY.match(line)
        if m:
            cat = {"name": m.group(1).strip(), "items": [], "grid": not cats}
            cats.append(cat)
            continue
        if cat is None:
            cat = {"name": "Goals", "items": [], "grid": True}
            cats.append(cat)
        m = _CHECK.match(line)
        if m:
            cat["items"].append({"label": m.group(1).strip(), "kind": "check"})
            continue
        m = _COUNTER.match(line)
        if m:
            cat["items"].append({"label": m.group(1).strip(), "kind": "counter", "max": int(m.group(2)), "unit": m.group(3).strip()})
            continue
        m = _SLOT.match(line)
        if m:
            cat["items"].append({"label": m.group(1).strip(), "kind": "slot", "hint": m.group(2).strip()})
        else:
            cat["items"].append({"label": line, "kind": "slot"})
    return clean_categories(cats)


def as_list(categories: list[dict]) -> str:
    """The grammar the other way: a template as the list the admin reads."""
    lines: list[str] = []
    for c in categories or []:
        lines.append(f"{c['name']}:")
        for it in c.get("items", []):
            if it["kind"] == "check":
                lines.append(f"[ ] {it['label']}")
            elif it["kind"] == "counter":
                lines.append(f"{it['label']} = {it.get('max', 0)} {it.get('unit', '')}".rstrip())
            else:
                lines.append(f"{it['label']} — {it['hint']}" if it.get("hint") else it["label"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


# ── a goal, and its state ────────────────────────────────────────────────────

def clean_goal(patch: Any) -> dict:
    """A goal's own words and state, bounded. Absent fields are absent."""
    out: dict = {}
    if not isinstance(patch, dict):
        return out
    if patch.get("target") is not None:
        out["target"] = str(patch["target"])[:120]
    if patch.get("note") is not None:
        out["note"] = str(patch["note"])[:200]
    for flag in ("met", "partial"):
        if patch.get(flag) is not None:
            out[flag] = bool(patch[flag])
    for count in ("have", "want"):
        if patch.get(count) is not None:
            try:
                out[count] = max(0, min(MAX_COUNT, int(patch[count])))
            except (TypeError, ValueError):
                pass
    return out


def apply_goal(goals: Any, item_id: str, patch: Any) -> dict:
    """The goals with one merged in. Met clears partly; nothing else is inferred."""
    goals = dict(goals) if isinstance(goals, dict) else {}
    g = dict(goals.get(item_id) or {}) if isinstance(goals.get(item_id), dict) else {}
    g.update(clean_goal(patch))
    if g.get("met"):
        g["partial"] = False
    goals[item_id] = g
    return goals


def _goal(goals: Any, item_id: str) -> dict:
    g = goals.get(item_id) if isinstance(goals, dict) else None
    return g if isinstance(g, dict) else {}


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def item_state(item: dict, goal: dict) -> tuple[str, float]:
    """met | partial | open, and how far along, for one item."""
    if item["kind"] == "counter":
        want = _int(goal.get("want"), -1) if goal.get("want") not in (None, "") else _int(item.get("max"))
        if want < 0:
            want = _int(item.get("max"))
        have = _int(goal.get("have"))
        if want <= 0:
            return ("met" if goal.get("met") else "open"), (1.0 if goal.get("met") else 0.0)
        ratio = max(0.0, min(1.0, have / want))
        return ("met" if have >= want else ("partial" if have > 0 else "open")), ratio
    met = bool(goal.get("met"))
    if item["kind"] == "slot" and not met and goal.get("partial"):
        return "partial", 0.5
    return ("met" if met else "open"), (1.0 if met else 0.0)


# ── progress, computed once so every surface agrees ─────────────────────────

def progress(categories: list[dict], goals: Any) -> dict:
    """
    Per category and overall: met, partly, total, a ratio; each item's
    state; the next open goals (with enough to act on them); complete.
    """
    cats: list[dict] = []
    met_all = partly_all = total_all = 0
    next_open: list[dict] = []
    for c in categories or []:
        met = partly = total = 0
        ratio_sum = 0.0
        items: list[dict] = []
        for it in c.get("items", []):
            g = _goal(goals, it["id"])
            state, ratio = item_state(it, g)
            total += 1
            met += 1 if state == "met" else 0
            partly += 1 if state == "partial" else 0
            ratio_sum += ratio
            row: dict = {"id": it["id"], "label": it["label"], "kind": it["kind"], "state": state, "ratio": round(ratio, 3),
                         "target": str(g.get("target") or "")[:120], "note": str(g.get("note") or "")[:200]}
            if it["kind"] == "counter":
                row["have"] = _int(g.get("have"))
                row["want"] = _int(g.get("want"), _int(it.get("max"))) if g.get("want") not in (None, "") else _int(it.get("max"))
                row["unit"] = it.get("unit", "")
            items.append(row)
            if state != "met" and len(next_open) < 6:
                next_open.append({"id": it["id"], "kind": it["kind"], "category": c["name"], "categoryId": c["id"],
                                  "label": it["label"], "target": row["target"], "state": state,
                                  "have": row.get("have"), "want": row.get("want"), "unit": row.get("unit", "")})
        cats.append({"id": c["id"], "name": c["name"], "met": met, "partly": partly, "total": total,
                     "ratio": round(ratio_sum / total, 3) if total else 0.0, "grid": bool(c.get("grid")), "items": items})
        met_all += met
        partly_all += partly
        total_all += total
    return {"met": met_all, "partly": partly_all, "total": total_all,
            "ratio": round(met_all / total_all, 3) if total_all else 0.0,
            "categories": cats, "next": next_open, "complete": total_all > 0 and met_all == total_all}


# ── what somebody else may see ───────────────────────────────────────────────

PRIVATE_GOAL_FIELDS = ("note",)


def public_goals(goals: Any) -> dict:
    """
    The goals as somebody else may see them: what was aimed for and how far
    it got, never the note a person wrote to themselves.

    ⚠ The same rule the plate follows on stream, applied to a shared page.
    It lives here rather than in either server so the two cannot come to
    disagree about what is private.
    """
    out: dict = {}
    for item_id, g in (goals or {}).items() if isinstance(goals, dict) else ():
        if isinstance(g, dict):
            out[item_id] = {k: v for k, v in g.items() if k not in PRIVATE_GOAL_FIELDS}
    return out


def public_progress(categories: list[dict], goals: Any) -> dict:
    """
    Progress for a shared page: computed from the stripped goals, and stripped
    again — a row still carrying an empty `note` would be a note-shaped hole
    for somebody to fill later without noticing what it was for.
    """
    prog = progress(categories, public_goals(goals))
    for category in prog.get("categories", []):
        for row in category.get("items", []):
            row.pop("note", None)
    for row in prog.get("next", []):
        row.pop("note", None)
    return prog


def element(name: str, variant: str, game: str, prog: dict) -> dict:
    """
    What the build plate draws: the eyebrow, the name, met of total, one arc
    per category with two fills (rose to met, blue on to partly — motion,
    not absence), the grid category's slot labels, the next open goals.
    A person's own notes never reach the stream.
    """
    grid = next((c for c in prog["categories"] if c.get("grid")), None)
    return {
        "name": name, "variant": variant, "game": game,
        "eyebrow": " · ".join(x for x in ("Build", game, variant) if x),
        "met": prog["met"], "partly": prog["partly"], "total": prog["total"], "ratio": prog["ratio"], "complete": prog["complete"],
        "count": f"{prog['met']} of {prog['total']}",
        "parts": [{"pct": (c["met"] / c["total"]) if c["total"] else 0.0,
                   "partly": ((c["met"] + c["partly"]) / c["total"]) if c["total"] else 0.0,
                   "state": "done" if c["total"] and c["met"] == c["total"] else ("now" if (c["met"] + c["partly"]) > 0 else "todo"),
                   "name": c["name"], "met": c["met"], "total": c["total"]} for c in prog["categories"]],
        "gridName": grid["name"] if grid else "",
        "slots": [{"label": it["label"], "state": it["state"]} for it in (grid["items"] if grid else []) if it["kind"] == "slot"][:25],
        "next": [{"category": n["category"], "label": n["label"],
                  "detail": n["target"] or (f"{n['have']} of {n['want']} {n['unit']}".strip() if n["kind"] == "counter" else ""),
                  "word": "partly" if n["state"] == "partial" else "not yet"} for n in prog["next"][:3]],
    }
