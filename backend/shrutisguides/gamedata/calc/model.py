# SPDX-License-Identifier: AGPL-3.0-only
"""
What a plan comes to — and where every number came from.

A CONTRIBUTION is one line from one thing a person chose: a unique's affix, a
paragon node's stat, a rune's effect. It says which stat it touches, how it
touches it, by how much, what it came from, and — the part that makes the
whole thing honest — how far we trust it.

A POOL is every contribution a plan makes. Asked for a stat, it returns a
TOTAL: the number, the arithmetic that produced it, the lines that made it,
and the worst trust state among them. Nothing computes a number without
being able to show its work, because a number a person cannot check is worse
than no number at all.

⚠ Three states, and they propagate upward. `counted` means every source for
this stat is in the model. `approximate` means something known is missing or
a range was collapsed. `not-counted` means we hold the fact and cannot
compute with it — the line is KEPT, listed in the breakdown, and left out of
the arithmetic. A total is only as good as its weakest line and says so.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

COUNTED, APPROXIMATE, NOT_COUNTED = "counted", "approximate", "not-counted"
STATES = (COUNTED, APPROXIMATE, NOT_COUNTED)          # best to worst

# How a contribution enters the arithmetic.
#   flat       added to the base                       +180 life
#   increased  summed, then applied once as (1 + Σ)    +24% increased life
#   more       each applied on its own                 ×1.15, then ×1.10
#   per_level  flat, multiplied by the character level  +1 life per level
FORMS = ("flat", "increased", "more", "per_level")


def worst(states: Iterable[str]) -> str:
    """The state of a thing made of several: the least trustworthy of them."""
    seen = [s for s in states if s in STATES]
    return max(seen, key=STATES.index) if seen else COUNTED


@dataclass(frozen=True, slots=True)
class Contribution:
    """One line, from one thing a person chose."""

    stat: str
    form: str
    value: float
    source_kind: str = ""
    source_id: str = ""
    source_name: str = ""
    text: str = ""                 # the line as the pack wrote it, for the breakdown
    state: str = COUNTED
    bucket: str = ""               # for games whose "more" multipliers group (Diablo IV's)
    place: str = ""                # the gear place it came from, where that differs from the source

    def __post_init__(self) -> None:
        if self.form not in FORMS:
            raise ValueError(f"{self.form}: not one of {FORMS}")
        if self.state not in STATES:
            raise ValueError(f"{self.state}: not one of {STATES}")

    @property
    def where(self) -> str:
        """Where a person goes to change this line."""
        return self.place or self.source_name or self.source_id


@dataclass
class Step:
    """One step of the arithmetic, for the breakdown to draw."""

    kind: str                      # base | flat | increased | more | per_level
    label: str
    value: float
    running: float
    lines: list[Contribution] = field(default_factory=list)


@dataclass
class Total:
    """A number, its working, and how far it is to be trusted."""

    stat: str
    value: float
    state: str = COUNTED
    steps: list[Step] = field(default_factory=list)
    lines: list[Contribution] = field(default_factory=list)
    uncounted: list[Contribution] = field(default_factory=list)

    @property
    def counted(self) -> bool:
        return self.state == COUNTED

    def by_source(self) -> dict[str, list[Contribution]]:
        """The lines grouped the way the breakdown shows them: gear, tree, skills…"""
        out: dict[str, list[Contribution]] = {}
        for c in self.lines + self.uncounted:
            out.setdefault(c.source_kind or "other", []).append(c)
        return out

    def as_dict(self) -> dict:
        return {
            "stat": self.stat, "value": round(self.value, 4), "state": self.state,
            "steps": [{"kind": s.kind, "label": s.label, "value": round(s.value, 4), "running": round(s.running, 4),
                       "lines": [_line(c) for c in s.lines]} for s in self.steps],
            "uncounted": [_line(c) for c in self.uncounted],
        }


def _line(c: Contribution) -> dict:
    return {"value": round(c.value, 4), "form": c.form, "text": c.text, "where": c.where,
            "kind": c.source_kind, "id": c.source_id, "name": c.source_name, "state": c.state}


class Pool:
    """
    Every contribution a plan makes, and the totals they come to.

    The arithmetic is the one every action RPG shares: a base, plus the flat
    additions, multiplied by one bracket of summed increases, then by each
    "more" multiplier on its own. A game whose multipliers group into buckets
    (Diablo IV's) puts the bucket's name on the contribution, and each bucket
    sums inside itself and multiplies against the others.
    """

    def __init__(self, level: int = 1):
        self.level = max(1, int(level))
        self._by_stat: dict[str, list[Contribution]] = {}

    def add(self, c: Contribution) -> None:
        self._by_stat.setdefault(c.stat, []).append(c)

    def extend(self, cs: Iterable[Contribution]) -> None:
        for c in cs:
            self.add(c)

    def stats(self) -> list[str]:
        return sorted(self._by_stat)

    def lines(self, stat: str) -> list[Contribution]:
        return list(self._by_stat.get(stat, ()))

    def total(self, stat: str, base: float = 0.0, base_label: str = "base") -> Total:
        counted = [c for c in self._by_stat.get(stat, ()) if c.state != NOT_COUNTED]
        uncounted = [c for c in self._by_stat.get(stat, ()) if c.state == NOT_COUNTED]
        t = Total(stat=stat, value=base, lines=counted, uncounted=uncounted,
                  state=worst([c.state for c in self._by_stat.get(stat, ())]))
        running = base
        if base:
            t.steps.append(Step("base", base_label, base, running))

        flat = [c for c in counted if c.form == "flat"]
        per_level = [c for c in counted if c.form == "per_level"]
        if flat or per_level:
            added = sum(c.value for c in flat) + sum(c.value * self.level for c in per_level)
            running += added
            t.steps.append(Step("flat", "added", added, running, flat + per_level))

        increased = [c for c in counted if c.form == "increased"]
        if increased:
            pct = sum(c.value for c in increased)
            running *= 1 + pct / 100.0
            t.steps.append(Step("increased", "increased", pct, running, increased))

        for bucket in dict.fromkeys(c.bucket for c in counted if c.form == "more"):
            group = [c for c in counted if c.form == "more" and c.bucket == bucket]
            # inside one bucket the multipliers add; between buckets they multiply
            pct = sum(c.value for c in group)
            running *= 1 + pct / 100.0
            t.steps.append(Step("more", bucket or "more", pct, running, group))

        t.value = running
        return t
