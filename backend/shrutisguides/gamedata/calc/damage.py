# SPDX-License-Identifier: AGPL-3.0-only
"""
What a skill hits for.

The shape is one thing across three games, because the question is one
question: at the rank this plan reaches, with the things this plan chose
feeding it, what does this skill do? A HIT is the answer — a range, the
element it lands as, the working that produced it, and how far it is to be
trusted.

⚠ The number this aims at is **the game's own skill tooltip**: the damage the
skill does before anything about the thing it hits. No enemy resistance, no
mitigation, no simulation. That is a number a person can check against their
own screen, which is the only kind worth showing. What happens to it on the
way to a monster needs the assumptions panel, and that comes after.

⚠ A game whose model is not written yet returns nothing. The panel then
shows the plan's stats and no damage, which is a working state.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .model import APPROXIMATE, COUNTED, NOT_COUNTED, Step, worst


@dataclass
class Hit:
    """One skill's damage, with its working."""

    skill_id: str
    skill_name: str
    element: str = ""
    low: float = 0.0
    high: float = 0.0
    rank: int = 0                  # the rank the plan actually reaches, gear included
    state: str = COUNTED
    why: str = ""
    steps: list[Step] = field(default_factory=list)

    @property
    def average(self) -> float:
        return (self.low + self.high) / 2

    def as_dict(self) -> dict:
        return {"skill": self.skill_id, "name": self.skill_name, "element": self.element,
                "low": round(self.low, 1), "high": round(self.high, 1), "average": round(self.average, 1),
                "rank": self.rank, "state": self.state, "why": self.why,
                "steps": [{"kind": s.kind, "label": s.label, "value": round(s.value, 3), "running": round(s.running, 1)}
                          for s in self.steps]}


def between(table: list[dict], rank: int, key: str) -> tuple[tuple[float, float] | None, str]:
    """
    A skill's value at a rank, from the per-rank table the pack records.

    The tables are not continuous — Diablo II's stop at twenty and then jump
    to twenty-five and thirty, because gear takes a skill past its twenty
    points. A rank between two rows is interpolated and SAYS SO; a rank past
    the last row is carried on at the slope of the final pair, and says so
    more loudly.
    """
    rows: list[tuple[int, list]] = []
    for r in table or []:
        v = (r.get("values") or {}).get(key)
        n = r.get("rank")
        if isinstance(n, int) and isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
            rows.append((n, v))
    if not rows:
        return None, NOT_COUNTED
    rows.sort()
    rank = max(1, rank)
    for n, v in rows:
        if n == rank:
            return (float(v[0]), float(v[1])), COUNTED
    below = [r for r in rows if r[0] < rank]
    above = [r for r in rows if r[0] > rank]
    if below and above:
        (n0, v0), (n1, v1) = below[-1], above[0]
        t = (rank - n0) / (n1 - n0)
        return (v0[0] + (v1[0] - v0[0]) * t, v0[1] + (v1[1] - v0[1]) * t), APPROXIMATE
    if below and len(below) >= 2:
        (n0, v0), (n1, v1) = below[-2], below[-1]
        step = (rank - n1) / max(1, n1 - n0)
        return (v1[0] + (v1[0] - v0[0]) * step, v1[1] + (v1[1] - v0[1]) * step), APPROXIMATE
    if below:
        return (float(below[-1][1][0]), float(below[-1][1][1])), APPROXIMATE
    return (float(above[0][1][0]), float(above[0][1][1])), APPROXIMATE


def hits(plan: dict, data, pool) -> list[Hit]:
    """Every skill in the plan the game's model can put a number on."""
    from .games import module_for
    module = module_for(plan.get("game", ""))
    model = getattr(module, "damage_for", None) if module else None
    if model is None:
        return []
    out: list[Hit] = []
    for sec_id in ("skills",):
        picks = ((plan.get("sections") or {}).get(sec_id) or {}).get("picks") or []
        for p in picks:
            hit = model(plan, data, pool, p)
            if hit is not None:
                out.append(hit)
    return out


def worst_of(hs: list[Hit]) -> str:
    return worst([h.state for h in hs])
