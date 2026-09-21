# SPDX-License-Identifier: AGPL-3.0-only
"""
From a plan to a pool: everything a person chose, as contributions.

Walks the plan section by section, pulls the record behind every choice, and
hands each of its stat lines to the game's mapper. Provenance travels the
whole way — a number in the panel opens to the lines that made it, and each
line names the gear place or the node a person can go and change.

⚠ An AFFIX chosen as a goal is a wish, not an item: the person has said "I
want cooldown reduction on this helm", and the pack holds a range across
tiers. It is counted at the best tier's best roll and marked APPROXIMATE, so
the panel shows what the plan is reaching for without claiming it is in hand.

⚠ A game with no mapper yet produces an empty pool and says so. That is a
working state, not an error: the planner still records the plan.
"""
from __future__ import annotations

from typing import Iterator

from ..query import GameData
from ..recipes import recipe_for
from .damage import hits
from .games import module_for
from .model import APPROXIMATE, Contribution, NOT_COUNTED, Pool, worst
from .vocabulary import GROUPS, grouped, stat

# The kinds that carry stat lines worth counting. A skill's own damage is the
# damage model's business (per game), not the pool's.
STATTED = ("unique", "base", "affix", "aspect", "rune", "runeword", "gem", "jewel", "charm", "node", "glyph", "set", "flask", "tempering")


def _best_tier(rec: dict) -> dict | None:
    """The highest tier a pack lists for an affix — what a plan is reaching for."""
    tiers = [t for t in (rec.get("tiers") or []) if isinstance(t, dict)]
    if not tiers:
        return None

    def rank(t: dict) -> float:
        for key in ("item_level", "level", "item_power", "tier"):
            v = t.get(key)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
        return 0.0

    return max(tiers, key=rank)


def raw_lines(rec: dict) -> Iterator[dict]:
    """
    Every stat-ish line on a record, however the pack shaped it.

    ⚠ An affix keeps its identity and its value in two different places. The
    `stats` entry says WHICH stat and, for some games, which element — but
    its numbers may be the engine's own budget rather than anything a person
    reads (Diablo IV's fire resistance affix carries 2275–2800 there and
    30–50 in its tier). The tiers say WHAT the roll is worth. So where a
    record has both, the tier's numbers are given to the stat entry's
    identity, and the entry's own numbers are passed over. Reading them the
    other way round is how every resistance in a game ends up uncounted.
    """
    tier = _best_tier(rec)
    tier_stats = [x for x in ((tier or {}).get("stats") or []) if isinstance(x, dict)]
    tier_numbers = {k: tier[k] for k in ("min", "max", "value") if tier and k in tier} if tier else {}

    for key in ("stats", "affixes", "implicit", "effects", "bonuses"):
        v = rec.get(key)
        if not isinstance(v, list):
            continue
        for x in v:
            if not isinstance(x, dict):
                continue
            if key == "stats" and tier_numbers and not tier_stats:
                yield {**x, **tier_numbers, "from_tier": True}
            else:
                yield x

    for x in tier_stats:                      # the tier carries its own stats (Diablo II's shape)
        yield x
    if tier and not tier_stats and tier_numbers and not isinstance(rec.get("stats"), list):
        # no stat entry to give the numbers to: the record's own words name it
        yield {**tier_numbers, "stat": rec.get("stat") or rec.get("id"),
               "text": rec.get("stat_text") or rec.get("name") or ""}


def chosen(plan: dict, data: GameData) -> Iterator[tuple[dict, dict]]:
    """Every record the plan picked, with where it sits: (source, record)."""
    game = plan.get("game", "")
    recipe = recipe_for(game)
    if not recipe:
        return
    seen: set[tuple[str, str, str]] = set()

    def take(kind: str, rid: str, place: str = "") -> Iterator[tuple[dict, dict]]:
        if not rid or kind not in STATTED or (kind, rid, place) in seen:
            return
        seen.add((kind, rid, place))
        rec = data.get(game, kind, rid)
        if rec:
            yield {"kind": kind, "id": rid, "name": rec.get("name") or rid, "place": place}, rec

    def fields(spec: dict, choice: dict, place: str = "") -> Iterator[tuple[dict, dict]]:
        if not isinstance(choice, dict):
            return
        for name, f in (spec or {}).items():
            if f.get("type") == "id":
                yield from take(f["kind"], choice.get(name) or "", place)
            elif f.get("type") == "ids":
                for rid in (choice.get(name) or []):
                    yield from take(f["kind"], rid, place)

    for sec in recipe["sections"]:
        value = (plan.get("sections") or {}).get(sec["id"])
        if not value:
            continue
        spec = sec.get("fields") or {}
        # ⚠ A cleaned plan writes a pick as {"id": …} and a picks entry the
        # same way, but this is a public function and a plan may arrive as a
        # person's shorthand — a bare id, a bare list. Take both shapes here
        # rather than crash on the short one.
        if sec["type"] == "pick":
            choice = value if isinstance(value, dict) else {"id": value}
            yield from take(sec["kind"], str(choice.get("id") or ""))
            yield from fields(spec, choice)
        elif sec["type"] == "picks":
            picks = value.get("picks", []) if isinstance(value, dict) else value
            for p in (picks if isinstance(picks, list) else []):
                p = p if isinstance(p, dict) else {"id": p}
                yield from take(sec["kind"], str(p.get("id") or ""))
                yield from fields(spec, p)
        elif sec["type"] == "gear" and isinstance(value, dict):
            for place, choice in value.items():
                if isinstance(choice, dict):
                    yield from fields(spec, choice, place)


def pool_for(plan: dict, data: GameData) -> Pool:
    """Every contribution the plan makes. An empty pool means the game has no mapper yet."""
    game = plan.get("game", "")
    pool = Pool(level=int(plan.get("level") or 1))
    module = module_for(game)
    if module is None:
        return pool
    for source, rec in chosen(plan, data):
        for line in raw_lines(rec):
            pool.extend(module.map_line(line, source))
    return pool


def sheet(plan: dict, data: GameData) -> dict:
    """
    The stats panel: groups of rows, each row a total with its working and
    its state. Rows whose every line is uncountable are still shown — a
    person should see that a thing they chose is not in the arithmetic.
    """
    game = plan.get("game", "")
    module = module_for(game)
    pool = pool_for(plan, data)
    base_for = getattr(module, "base_for", None)
    base = dict(base_for(plan, data, pool) if base_for else (getattr(module, "BASE", {}) or {}))
    ids = sorted(set(pool.stats()) | set(base))
    # ⚠ A stat whose base the pack does not record cannot be exact, however
    # well its lines are counted: a Diablo IV character has life before any
    # gear and the pack does not say how much, so the sum of the gear is not
    # "maximum life". The game declares those stats and the row is marked
    # approximate with the reason on it, rather than showing a confident
    # number that is quietly missing its largest term.
    incomplete = dict(getattr(module, "INCOMPLETE_BASE", {}) or {})
    rows: dict[str, dict] = {}
    for sid in ids:
        total = pool.total(sid, base=base.get(sid, 0.0), base_label="the character itself")
        s = stat(sid)
        row = total.as_dict() | {"name": s.name, "unit": s.unit, "group": s.group, "integer": s.integer}
        if sid in incomplete:
            row["state"] = worst([row["state"], APPROXIMATE])
            row["why"] = incomplete[sid]
        if s.cap:
            row["cap"] = s.cap
        rows[sid] = row
    out_groups = []
    for g, stats_in in grouped(ids):
        out_groups.append({"group": g, "rows": [rows[st.id] for st in stats_in]})
    uncounted = [c for sid in ids for c in pool.lines(sid) if c.state == NOT_COUNTED]
    damage = hits(plan, data, pool)
    return {
        "game": game, "level": pool.level, "supported": module is not None,
        "groups": out_groups,
        "damage": [h.as_dict() for h in damage],
        "state": worst([r["state"] for r in rows.values()]),
        "uncounted": {"lines": len(uncounted), "things": len({(c.source_kind, c.source_id) for c in uncounted})},
    }
