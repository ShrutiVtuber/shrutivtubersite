# SPDX-License-Identifier: AGPL-3.0-only
"""
A plan: a person's choices for one character, checked against the game
database and turned into the goals the build tracker already follows.

    plan = {"game": "diablo-iv", "class_id": "sorcerer", "level": 60, "notes": "",
            "sections": {"skills": {"picks": [{"id": "fireball", "ranks": 5, "upgrades": ["enhanced-fireball"]}]},
                         "gear":   {"helm": {"unique": "harlequin-crest", "affixes": ["cooldown-reduction"]}},
                         "targets": {"paragon-points": 300}}}

`clean_plan` bounds every field by the game's recipe and drops what the
database does not know, reporting each drop. `plan_to_categories` writes the
plan as a build template — Gear as the grid of slots with the chosen item
as each slot's target, skills and boards as checks, glyph levels and stat
targets as counters — so the phone, the site and the overlay track a planned
build exactly as they track any other. `plan_summary` is the plan with its
names resolved, for a page to draw.

⚠ A plan is a person's own; it never reaches the stream except as the goals
the build already shows. Nothing here counts how far anyone is from it.
"""
from __future__ import annotations

from typing import Any

from .. import builds
from .load import slug
from .query import GameData
from .recipes import recipe_for

MAX_TEXT = 120
MAX_NOTES = 400
MAX_LEVEL = 200


def _int(value: Any, lo: int, hi: int) -> int | None:
    if value is None or value == "" or isinstance(value, bool):      # 1 == True in Python; a bool is not a number here
        return None
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return None


def _text(value: Any, limit: int = MAX_TEXT) -> str:
    return "" if value is None or isinstance(value, (dict, list)) else str(value).strip()[:limit]


class _Check:
    """Existence checks against the database, remembered so a plan of forty items asks forty times at most."""

    def __init__(self, data: GameData, game: str, class_id: str):
        self.data, self.game, self.class_id = data, game, class_id
        self.cache: dict[tuple, bool] = {}

    def known(self, kind: str, id: str, sub: str | list[str] | None = None, by_class: bool = False, slot_id: str | None = None) -> bool:
        key = (kind, id, tuple(sub) if isinstance(sub, list) else sub, by_class, slot_id)
        if key not in self.cache:
            self.cache[key] = self.data.exists_id(self.game, kind, id, sub=sub, class_id=self.class_id if by_class else None, slot_id=slot_id)
        return self.cache[key]

    def record(self, kind: str, id: str) -> dict | None:
        return self.data.get(self.game, kind, id)


SLOTTED = ("unique", "base", "aspect", "affix", "runeword")      # the kinds a gear choice must fit its slot with


def _clean_fields(spec: dict, raw: dict, chk: _Check, where: str, problems: list[str], chosen: dict | None = None,
                  slot_id: str | None = None) -> dict:
    out: dict = {}
    if not isinstance(raw, dict):
        return out
    for name, f in (spec or {}).items():
        v = raw.get(name)
        if v in (None, "", [], {}):
            continue
        t = f["type"]
        if t == "int":
            n = _int(v, int(f.get("min", 0)), int(f.get("max", builds.MAX_COUNT)))
            if n is not None:
                out[name] = n
        elif t == "text":
            s = _text(v)
            if s:
                out[name] = s
        elif t == "choice":
            s = _text(v, 40)
            if s in f.get("options", ()):
                out[name] = s
            else:
                problems.append(f"{where}.{name}: '{s}' is not one of the choices")
        elif t == "id":
            s = slug(v)
            fit = slot_id if f["kind"] in SLOTTED else None
            if s and chk.known(f["kind"], s, f.get("sub"), f.get("by_class", False), fit):
                out[name] = s
            elif s and fit and chk.known(f["kind"], s, f.get("sub"), f.get("by_class", False)):
                problems.append(f"{where}.{name}: '{s}' does not fit that slot")
            elif s:
                problems.append(f"{where}.{name}: no {f['kind']} called '{s}'")
        elif t == "ids":
            ids: list[str] = []
            fit = slot_id if f["kind"] in SLOTTED else None
            for x in (v if isinstance(v, list) else [v])[: int(f.get("max", 12)) + 12]:
                s = slug(x)
                if not s or s in ids:
                    continue
                if chk.known(f["kind"], s, f.get("sub"), f.get("by_class", False), fit):
                    ids.append(s)
                elif fit and chk.known(f["kind"], s, f.get("sub"), f.get("by_class", False)):
                    problems.append(f"{where}.{name}: '{s}' does not fit that slot")
                else:
                    problems.append(f"{where}.{name}: no {f['kind']} called '{s}'")
            if len(ids) > int(f.get("max", 12)):
                problems.append(f"{where}.{name}: more than {f['max']} — the first {f['max']} kept")
                ids = ids[: int(f.get("max", 12))]
            if ids:
                out[name] = ids
        elif t == "within":
            inner = [slug(x.get("id") if isinstance(x, dict) else x) for x in ((chosen or {}).get(f["list"]) or [])]
            ids: list[str] = []
            for x in (v if isinstance(v, list) else [v]):
                s = slug(x)
                if s in inner and s not in ids:
                    ids.append(s)
                elif s:
                    problems.append(f"{where}.{name}: '{s}' is not among the {f['list']} of the chosen one")
            if ids:
                out[name] = ids[: int(f.get("max", 6))]
    return out


MAX_CONDITIONS = 80


def held_conditions(raw: Any) -> list[str]:
    """
    The assumptions a plan makes, as a sorted list of ids. Accepts the shape a
    page of switches sends ({id: true}) and the shape a file keeps (a list).

    ⚠ Nothing is assumed by default. A number starts as what holds without
    conditions and rises as a person says which are true — which is the
    honest direction for it to move in.
    """
    if isinstance(raw, dict):
        got = [k for k, v in raw.items() if v]
    elif isinstance(raw, list):
        got = raw
    else:
        return []
    out: list[str] = []
    for c in got:
        s = slug(c, 120)
        if s and s not in out:
            out.append(s)
    return sorted(out[:MAX_CONDITIONS])


def gear_places(sec: dict, data: GameData, game: str, class_id: str) -> dict[str, str]:
    """
    The places a gear section offers, in order: {place id: slot id}. A slot
    with `count` 2 is two places (`ring`, `ring-2`); a recipe may name its
    slots outright — as a list, or as a mapping when the place and the slot
    whose items fill it differ (a mercenary wears the same helms a person
    does) — or leave some out (sockets, the charms' own section).
    """
    if isinstance(sec.get("slots"), dict):
        return dict(sec["slots"])
    if sec.get("slots"):
        return {s: s for s in sec["slots"]}
    out: dict[str, str] = {}
    left_out = set(sec.get("exclude") or ())
    for slot in data.list(game, "slot", class_id=class_id or None):
        if slot["id"] in left_out:
            continue
        try:
            count = max(1, min(12, int(slot.get("count") or 1)))
        except (TypeError, ValueError):
            count = 1
        out[slot["id"]] = slot["id"]
        for i in range(2, count + 1):
            out[f"{slot['id']}-{i}"] = slot["id"]
    return out


def place_label(place: str, slot_id: str, names: "_Names") -> str:
    """
    The place's own name where the pack has one (a mercenary's helm), the
    slot's name with the place's suffix where the place is one of several
    (`ring-2` → "Ring 2"), the slot's name otherwise.
    """
    own = names.known("slot", place)
    if own:
        return own
    name = names.of("slot", slot_id)
    return name if place == slot_id else f"{name} {place[len(slot_id) + 1:]}" if place.startswith(f"{slot_id}-") else f"{name} ({place})"


def clean_plan(raw: Any, data: GameData) -> tuple[dict, list[str]]:
    """The plan as the recipe allows it, and every reason a part of it was refused."""
    problems: list[str] = []
    raw = raw if isinstance(raw, dict) else {}
    game = slug(raw.get("game"))
    recipe = recipe_for(game)
    if recipe is None:
        return {}, [f"no planner for '{game or 'no game'}'"]
    if data.game(game) is None:
        return {}, [f"the data for {game} is not loaded"]
    class_id = slug(raw.get("class_id") or raw.get("class"))
    if class_id and not data.exists_id(game, "class", class_id):
        problems.append(f"no class called '{class_id}'")
        class_id = ""
    chk = _Check(data, game, class_id)
    plan: dict = {"game": game, "class_id": class_id, "level": _int(raw.get("level"), 1, MAX_LEVEL),
                  "notes": _text(raw.get("notes"), MAX_NOTES), "conditions": held_conditions(raw.get("conditions")),
                  "sections": {}}
    sections = raw.get("sections") if isinstance(raw.get("sections"), dict) else {}
    for sec in recipe["sections"]:
        sid, value = sec["id"], sections.get(sec["id"])
        if value in (None, "", [], {}):
            continue
        by_class = bool(sec.get("by_class"))
        if sec["type"] == "pick":
            s = slug(value.get("id") if isinstance(value, dict) else value)
            if s and chk.known(sec["kind"], s, sec.get("sub"), by_class):
                plan["sections"][sid] = {"id": s, **_clean_fields(sec.get("fields"), value if isinstance(value, dict) else {}, chk, sid, problems)}
            elif s:
                problems.append(f"{sid}: no {sec['kind']} called '{s}'" + (" for this class" if by_class else ""))
        elif sec["type"] == "picks":
            picks_raw = value.get("picks") if isinstance(value, dict) else value
            points = _int(value.get("points"), 0, builds.MAX_COUNT) if isinstance(value, dict) else None
            picks: list[dict] = []
            seen: set[str] = set()
            for p in (picks_raw if isinstance(picks_raw, list) else [])[: int(sec.get("max", 24)) + 24]:
                pid = slug(p.get("id") if isinstance(p, dict) else p)
                if not pid or pid in seen:
                    continue
                if not chk.known(sec["kind"], pid, sec.get("sub"), by_class):
                    problems.append(f"{sid}: no {sec['kind']} called '{pid}'" + (" for this class" if by_class else ""))
                    continue
                seen.add(pid)
                chosen = chk.record(sec["kind"], pid) if any(f["type"] == "within" for f in (sec.get("fields") or {}).values()) else None
                picks.append({"id": pid, **_clean_fields(sec.get("fields"), p if isinstance(p, dict) else {}, chk, f"{sid}.{pid}", problems, chosen)})
            if len(picks) > int(sec.get("max", 24)):
                problems.append(f"{sid}: more than {sec['max']} — the first {sec['max']} kept")
                picks = picks[: int(sec.get("max", 24))]
            if picks or points:
                plan["sections"][sid] = {"picks": picks, **({"points": points} if points else {})}
        elif sec["type"] == "gear":
            places = gear_places(sec, data, game, class_id)
            gear: dict = {}
            for slot_id, choice in (value.items() if isinstance(value, dict) else []):
                s = slug(slot_id)
                if s not in places:
                    problems.append(f"{sid}: no slot called '{s}'" + (" for this class" if class_id else ""))
                    continue
                fields = _clean_fields(sec.get("fields"), choice, chk, f"{sid}.{s}", problems, slot_id=places[s])
                if fields:
                    gear[s] = fields
            if gear:
                plan["sections"][sid] = gear
        elif sec["type"] == "targets":
            targets: dict = {}
            for e in sec.get("entries", []):
                n = _int((value or {}).get(e["id"]) if isinstance(value, dict) else None, 0, int(e.get("max", builds.MAX_COUNT)))
                if n:
                    targets[e["id"]] = n
            if targets:
                plan["sections"][sid] = targets
    return plan, problems


# ── names, once ──────────────────────────────────────────────────────────────

class _Names:
    def __init__(self, data: GameData, game: str, plan: dict, recipe: dict):
        self.data, self.game = data, game
        wanted: dict[str, set[str]] = {}

        def want(kind: str, id: Any) -> None:
            if isinstance(id, str) and id:
                wanted.setdefault(kind, set()).add(id)

        want("class", plan.get("class_id"))
        for sec in recipe["sections"]:
            value = plan.get("sections", {}).get(sec["id"])
            if not value:
                continue
            fields = sec.get("fields") or {}
            if sec["type"] == "pick":
                want(sec["kind"], value.get("id"))
                self._want_fields(fields, value, want)
            elif sec["type"] == "picks":
                for p in value.get("picks", []):
                    want(sec["kind"], p.get("id"))
                    self._want_fields(fields, p, want)
            elif sec["type"] == "gear":
                for place, choice in value.items():
                    want("slot", place)
                    want("slot", place.rsplit("-", 1)[0] if place[-1:].isdigit() and "-" in place else place)
                    for mapped in ([sec["slots"].get(place)] if isinstance(sec.get("slots"), dict) else []):
                        want("slot", mapped)
                    self._want_fields(fields, choice, want)
        self.names = {kind: data.names(game, kind, sorted(ids)) for kind, ids in wanted.items()}

    @staticmethod
    def _want_fields(fields: dict, choice: dict, want) -> None:
        for name, f in fields.items():
            if f["type"] == "id":
                want(f["kind"], choice.get(name))
            elif f["type"] == "ids":
                for x in choice.get(name) or []:
                    want(f["kind"], x)

    def of(self, kind: str, id: str) -> str:
        return self.names.get(kind, {}).get(id) or id.replace("-", " ")

    def known(self, kind: str, id: str) -> str:
        """The name the pack gives, or nothing — so a caller can tell a real record from a guess."""
        return self.names.get(kind, {}).get(id, "")


def _detail(fields: dict, choice: dict, names: _Names, chosen: dict | None = None) -> str:
    """The choice in words: 'Harlequin Crest · Aspect of Might · cooldown reduction, life · masterwork 12'."""
    parts: list[str] = []
    for name, f in fields.items():
        v = choice.get(name)
        if v in (None, "", [], {}):
            continue
        if f["type"] == "id":
            parts.append(names.of(f["kind"], v))
        elif f["type"] == "ids":
            parts.append(", ".join(names.of(f["kind"], x) for x in v))
        elif f["type"] == "within":
            inner = {slug(x.get("id")): x.get("name") for x in ((chosen or {}).get(f["list"]) or []) if isinstance(x, dict)}
            parts.append(", ".join(str(inner.get(x) or x.replace("-", " ")) for x in v))
        elif f["type"] == "int":
            unit = f.get("unit", "")
            parts.append(f"{v} {unit}".strip() if unit != "level" else f"level {v}")
        elif f["type"] in ("choice", "text"):
            parts.append(str(v))
    return " · ".join(p for p in parts if p)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def plan_to_categories(plan: dict, data: GameData) -> list[dict]:
    """The plan as a build template: categories of slots, counters and checks, ids stable across re-plans."""
    recipe = recipe_for(plan.get("game", ""))
    if not recipe or not plan.get("sections"):
        return []
    names = _Names(data, plan["game"], plan, recipe)
    cats: list[dict] = []
    for sec in recipe["sections"]:
        value = plan["sections"].get(sec["id"])
        if not value:
            continue
        sid, fields, items = sec["id"], sec.get("fields") or {}, []
        if sec["type"] == "pick":
            items.append({"id": sid, "label": names.of(sec["kind"], value["id"]), "kind": "check", "hint": _clip(_detail(fields, value, names), MAX_TEXT)})
        elif sec["type"] == "picks":
            track = sec.get("track", "check")
            for p in value.get("picks", []):
                chosen = data.get(plan["game"], sec["kind"], p["id"]) if any(f["type"] == "within" for f in fields.values()) else None
                label = names.of(sec["kind"], p["id"])
                if track != "check" and track in fields and fields[track]["type"] == "int" and p.get(track):
                    items.append({"id": f"{sid}-{p['id']}", "label": label, "kind": "counter", "max": int(p[track]), "unit": fields[track].get("unit", ""),
                                  "hint": _clip(_detail({k: f for k, f in fields.items() if k != track}, p, names, chosen), MAX_TEXT)})
                else:
                    items.append({"id": f"{sid}-{p['id']}", "label": label, "kind": "check", "hint": _clip(_detail(fields, p, names, chosen), MAX_TEXT)})
            pts = sec.get("points")
            if pts:
                total = value.get("points") or (sum(int(p.get(pts["field"]) or 0) for p in value.get("picks", [])) if pts.get("field") else 0)
                if total:
                    items.append({"id": f"{sid}-{pts['id']}", "label": pts["name"], "kind": "counter", "max": int(total), "unit": pts.get("unit", "")})
        elif sec["type"] == "gear":
            places = gear_places(sec, data, plan["game"], plan.get("class_id", ""))
            order = list(places)
            for place in sorted(value, key=lambda s: order.index(s) if s in order else len(order)):
                slot_id = places.get(place, place)
                items.append({"id": f"{sid}-{place}", "label": place_label(place, slot_id, names), "kind": "slot",
                              "hint": _clip(_detail(fields, value[place], names), MAX_TEXT)})
        elif sec["type"] == "targets":
            for e in sec.get("entries", []):
                if value.get(e["id"]):
                    items.append({"id": f"{sid}-{e['id']}", "label": e["name"], "kind": "counter", "max": int(value[e["id"]]), "unit": e.get("unit", "")})
        if items:
            cats.append({"id": sid, "name": sec["name"], "grid": bool(sec.get("grid")), "items": items[: builds.MAX_ITEMS]})
    return builds.clean_categories(cats)


def plan_goals(categories: list[dict], goals: Any = None) -> dict:
    """
    Every planned item's detail written in as its target — the slot's item,
    the skill's ranks and upgrades, the gem's supports — so the overlay's
    next goals and the phone's rows show the plan before the person has
    said a word. Goals already set keep their words and their state; goals
    for items the re-plan dropped are let go.
    """
    out: dict = {}
    old = goals if isinstance(goals, dict) else {}
    for c in categories:
        for it in c.get("items", []):
            g = dict(old.get(it["id"]) or {}) if isinstance(old.get(it["id"]), dict) else {}
            if it.get("hint") and not g.get("target"):
                g["target"] = it["hint"]
            if g:
                out[it["id"]] = g
    return out


def plan_summary(plan: dict, data: GameData) -> dict:
    """The plan with names, for a page: the class, then each section's lines."""
    recipe = recipe_for(plan.get("game", ""))
    pack = data.game(plan.get("game", ""))
    if not recipe or not pack:
        return {"game": plan.get("game", ""), "sections": []}
    names = _Names(data, plan["game"], plan, recipe)
    out = {"game": plan["game"], "gameName": pack["name"], "patch": pack["patch"], "season": pack["season"],
           "classId": plan.get("class_id", ""), "className": names.of("class", plan["class_id"]) if plan.get("class_id") else "",
           "level": plan.get("level"), "notes": plan.get("notes", ""), "sections": [], "choices": 0}
    for sec in recipe["sections"]:
        value = plan.get("sections", {}).get(sec["id"])
        if not value:
            continue
        fields = sec.get("fields") or {}
        lines: list[dict] = []
        if sec["type"] == "pick":
            lines.append({"id": value["id"], "label": names.of(sec["kind"], value["id"]), "detail": _detail(fields, value, names)})
        elif sec["type"] == "picks":
            for p in value.get("picks", []):
                chosen = data.get(plan["game"], sec["kind"], p["id"]) if any(f["type"] == "within" for f in fields.values()) else None
                lines.append({"id": p["id"], "label": names.of(sec["kind"], p["id"]), "detail": _detail(fields, p, names, chosen)})
            if value.get("points"):
                lines.append({"id": "points", "label": (sec.get("points") or {}).get("name", "Points"), "detail": str(value["points"])})
        elif sec["type"] == "gear":
            places = gear_places(sec, data, plan["game"], plan.get("class_id", ""))
            for place, choice in value.items():
                slot_id = places.get(place, place)
                lines.append({"id": place, "label": place_label(place, slot_id, names), "detail": _detail(fields, choice, names)})
        elif sec["type"] == "targets":
            for e in sec.get("entries", []):
                if value.get(e["id"]):
                    lines.append({"id": e["id"], "label": e["name"], "detail": f"{value[e['id']]} {e.get('unit', '')}".strip()})
        out["sections"].append({"id": sec["id"], "name": sec["name"], "type": sec["type"], "lines": lines})
        out["choices"] += len(lines)
    return out
