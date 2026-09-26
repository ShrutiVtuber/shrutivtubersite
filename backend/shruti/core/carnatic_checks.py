# SPDX-License-Identifier: AGPL-3.0-only
"""
The construction checks and prechecks (FORMAT.md §4d), in words.

They run on a learner's draft and say what they see ("the line is 30 units;
Adi at speed 2 needs 32 per avartanam"). They never block anything: a piece
can be deliberately unusual. The website and the app run the same rules in
the browser for construct items; these are the server's copy, used for the
hints a submission returns.
"""
from __future__ import annotations

import re

from shruti.core import carnatic as rules

NOTE = re.compile(r"^(?:(?P<g>[a-z-]+):)?(?P<low>\.{0,2})(?P<s>[SRGMPDN])(?P<v>[123])?(?P<high>'{0,2})$", re.I)
SPEED_UNITS = {1: 1, 2: 2, 3: 4, 4: 8}


def seconds(text: str) -> float | None:
    """'2:14' → 134; '1:02:03' → 3723; '134' → 134."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        parts = [float(p) for p in text.split(":")]
    except ValueError:
        return None
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def tokens(line: str) -> list[str]:
    """Notation tokens, sahitya lines and bars left out."""
    out = []
    for row in line.splitlines():
        if row.strip().startswith("~"):
            continue
        out.extend(t for t in row.split() if t not in ("|", "||"))
    return out


def units(toks: list[str]) -> int:
    return sum(2 if t == ";" else 1 for t in toks)


def tala_counts(tala: str) -> int | None:
    data = rules.data("talas.json") or {}
    for t in data.get("practical", []):
        if t.get("id") == tala:
            return len(t.get("counts") or []) or None
    for t in data.get("suladi", []):
        if t.get("id") == tala:
            return len(t.get("counts") or []) or t.get("aksharas")
    return rules.TALA_COUNTS.get(tala)


def raga_swaras(raga_id: str) -> set[str] | None:
    data = rules.data("ragas.json") or {}
    for r in data.get("janyas", []) + data.get("performed", []):
        if r["id"] == raga_id:
            found = set(re.findall(r"[SRGMPDN][123]?", f"{r.get('arohana', '')} {r.get('avarohana', '')}"))
            found |= {a.get("swara") for a in (r.get("anya") or []) if a.get("swara")}
            return found
    for m in data.get("melakartas", []):
        if m.get("id") == raga_id:
            return set(m.get("swaras") or [])
    return None


def only_raga_swaras(line: str, raga: str) -> list[str]:
    allowed = raga_swaras(raga)
    if not allowed:
        return []
    letters = {a[0] for a in allowed}
    outside = []
    for t in tokens(line):
        m = NOTE.match(t)
        if not m:
            continue
        s, v = m.group("s").upper(), m.group("v")
        if (v and f"{s}{v}" not in allowed and s not in ("S", "P")) or (not v and s not in letters):
            outside.append(f"{s}{v or ''}")
    if outside:
        uniq = ", ".join(dict.fromkeys(outside))
        return [f"{uniq} isn't in the raga's arohana, avarohana or anya swaras. Keep it if you meant it."]
    return []


def fits_tala(line: str, tala: str, speed: int = 1, eduppu: float = 0) -> list[str]:
    counts = tala_counts(tala)
    if not counts or tala == "none":
        return []
    per = counts * SPEED_UNITS.get(int(speed or 1), 1)
    n = units(tokens(line)) + int(round(float(eduppu or 0) * SPEED_UNITS.get(int(speed or 1), 1)))
    if n % per:
        name = tala.replace("_", " ")
        return [f"The line is {n} units; {name.capitalize()} at speed {speed} needs {per} per avartanam, "
                f"so it would end {per - n % per} units before samam."]
    return []


def total_matras(line: str, target) -> list[str]:
    n = units(tokens(line))
    if isinstance(target, list):
        if n not in target:
            return [f"It is {n} matras; this asks for {' or '.join(str(t) for t in target)}."]
    elif isinstance(target, int) and n != target:
        return [f"It is {n} matras; this asks for {target}."]
    return []


def three_equal(line: str) -> list[str]:
    toks = tokens(line)
    n = len(toks)
    for size in range(n // 3, 0, -1):
        rest = n - 3 * size
        if rest < 0:
            continue
        # Three equal statements with two equal gaps: P G P G P, gaps of holds.
        for gap in range(0, rest // 2 + 1):
            if 3 * size + 2 * gap != n:
                continue
            a = toks[:size]
            b = toks[size + gap:2 * size + gap]
            c = toks[2 * size + 2 * gap:]
            if a == b == c:
                return []
    return ["The three statements aren't the same length yet (or the gaps between them differ)."]


def precheck(check, line: str, spec: dict) -> list[str]:
    name, arg = (check, None) if isinstance(check, str) else next(iter(check.items()), (None, None))
    if name == "only_raga_swaras" and spec.get("raga") and spec.get("raga") != "choose":
        return only_raga_swaras(line, spec["raga"])
    if name == "fits_tala" and spec.get("tala") and spec.get("tala") not in ("none", "choose"):
        return fits_tala(line, spec["tala"], spec.get("speed", 1), spec.get("eduppu", 0))
    if name == "total_matras" and arg is not None:
        return total_matras(line, arg)
    if name == "three_equal":
        return three_equal(line)
    return []
