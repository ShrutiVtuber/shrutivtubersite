# SPDX-License-Identifier: AGPL-3.0-only
"""
The engine: what a run's progress means, computed from the guide and the
person's check-in. One implementation, shared by the site, the overlays and
the tracker, so a step is "current" in the same place everywhere.

Vocabulary, from the spec (C.1, C.2, D.2) and the design handoff:

- A **run** is one person's progress through one guide: a variant, a
  check-in (the guide's declared fields, last values kept), step states
  (only the ones a person set: done, skipped, later), routine ticks, track
  state, a note, a Later list.
- A **gate** is an object of conditions, all of which must hold. Keys are
  `<field>_min`, `<field>_max` (number fields), `<field>_at_least`,
  `<field>_is` (ordered fields), and the built-ins `variant`, `steps_done`,
  `codex_active`. A missing value fails the condition — a locked row states
  its gate, it never guesses.
- **Step states**: locked · available · current · done · skipped · later.
  The current step is COMPUTED, never stored: the first step in path order
  that is available and applies to the run's variant. Only one step is ever
  current, and only on the main path; a track has its own.
- **Proposals**: `auto_done` uses the gate language; when it holds for a
  step that is available or locked, the step is PROPOSED as done, with the
  evidence — never applied silently. The spec's A.4.12, not negotiable.
- **Codex**: an entry is active when its `show_when` holds or a `system`
  step that opens it is done; "soon" when it declares `ignore_until` and is
  not yet active; hidden otherwise. Revealing loses nothing, so no proposal.
- **Versions never delete progress.** States are keyed by step id; an id
  the current version no longer has is kept and reported as `orphaned`, so
  the path can show it done and greyed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Gate = dict[str, Any]
BUILT_IN = ("variant", "steps_done", "codex_active")


@dataclass
class Run:
    """The person's side, as stored. Everything optional but the variant."""

    variant: str = ""
    checkin: dict[str, Any] = field(default_factory=dict)
    # step id → "done" | "skipped" | "later"
    states: dict[str, str] = field(default_factory=dict)
    # routine id → list of ticked item ids
    routines: dict[str, list[str]] = field(default_factory=dict)
    # track id → {"rank": int, "day_one": [ids], "counters": {id: n}}
    tracks: dict[str, dict[str, Any]] = field(default_factory=dict)


# ── gates ────────────────────────────────────────────────────────────────────

def _fields(doc: dict) -> dict[str, dict]:
    return {f["id"]: f for f in doc.get("checkin", []) if isinstance(f, dict)}


def _ordered_index(field_: dict, value: Any) -> int | None:
    options = field_.get("options") or []
    try:
        return options.index(value)
    except ValueError:
        return None


def holds(gate: Gate | None, doc: dict, run: Run, *, done: set[str] | None = None,
          active: set[str] | None = None) -> bool:
    """
    Every condition in the gate holds. An absent or empty gate always holds.
    A condition on a field the person has not answered does NOT hold.
    """
    if not gate:
        return True
    fields = _fields(doc)
    done = done if done is not None else {k for k, v in run.states.items() if v == "done"}
    active = active if active is not None else set()
    for key, wanted in gate.items():
        if key == "variant":
            if run.variant != wanted:
                return False
            continue
        if key == "steps_done":
            if not set(wanted or []) <= done:
                return False
            continue
        if key == "codex_active":
            if not set(wanted or []) <= active:
                return False
            continue
        matched = False
        for suffix in ("_at_least", "_min", "_max", "_is"):
            if key.endswith(suffix):
                fid = key[: -len(suffix)]
                f = fields.get(fid)
                have = run.checkin.get(fid)
                if f is None or have is None or have == "":
                    return False
                if suffix == "_min":
                    ok = _number(have) is not None and _number(have) >= _number(wanted)
                elif suffix == "_max":
                    ok = _number(have) is not None and _number(have) <= _number(wanted)
                elif suffix == "_at_least":
                    hi, wi = _ordered_index(f, have), _ordered_index(f, wanted)
                    ok = hi is not None and wi is not None and hi >= wi
                else:
                    ok = have == wanted
                if not ok:
                    return False
                matched = True
                break
        if not matched:
            return False               # an unknown key never holds
    return True


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def applies(thing: dict, run: Run) -> bool:
    """`applies_to` absent means every variant; present means only those."""
    only = thing.get("applies_to")
    return not only or run.variant in only


# ── the path ─────────────────────────────────────────────────────────────────

def phases_in_order(doc: dict) -> list[dict]:
    return sorted((p for p in doc.get("phases", []) if isinstance(p, dict)),
                  key=lambda p: p.get("order", 0))


def steps_in(doc: dict, phase_id: str) -> list[dict]:
    return sorted((s for s in doc.get("steps", []) if isinstance(s, dict) and s.get("phase") == phase_id),
                  key=lambda s: s.get("order", 0))


def codex_states(doc: dict, run: Run) -> dict[str, str]:
    """entry id → active | soon | hidden."""
    done = {k for k, v in run.states.items() if v == "done"}
    opened = {s.get("codex") for s in doc.get("steps", [])
              if isinstance(s, dict) and s.get("codex") and s.get("id") in done}
    out: dict[str, str] = {}
    for entry in doc.get("codex", []):
        if not isinstance(entry, dict):
            continue
        eid = entry["id"]
        if eid in opened or holds(entry.get("show_when"), doc, run, done=done, active=set()):
            out[eid] = "active"
        elif entry.get("ignore_until"):
            out[eid] = "soon"
        else:
            out[eid] = "hidden"
    return out


@dataclass
class Progress:
    """Everything computed for one run, in one pass."""

    states: dict[str, str]                 # every step id in the version → state
    current: str | None                    # the one current step on the main path
    track_current: dict[str, str | None]   # track id → its current step
    codex: dict[str, str]                  # entry id → active | soon | hidden
    routines: dict[str, bool]              # routine id → available
    orphaned: dict[str, str]               # step ids with a state the version no longer has
    proposals: list[dict]                  # steps auto_done would mark, with evidence
    phase_counts: dict[str, tuple[int, int]]  # phase id → (done, counted)


def compute(doc: dict, run: Run) -> Progress:
    done = {k for k, v in run.states.items() if v == "done"}
    codex = codex_states(doc, run)
    active = {k for k, v in codex.items() if v == "active"}
    states: dict[str, str] = {}
    known: set[str] = set()
    current: str | None = None
    track_current: dict[str, str | None] = {}
    counts: dict[str, tuple[int, int]] = {}

    for phase in phases_in_order(doc):
        pid = phase["id"]
        track = phase.get("track")
        phase_done = phase_counted = 0
        for step in steps_in(doc, pid):
            sid = step["id"]
            known.add(sid)
            set_ = run.states.get(sid)
            if set_ in ("done", "skipped", "later"):
                state = set_
            elif not applies(step, run):
                state = "locked"
            elif holds(step.get("gate"), doc, run, done=done, active=active):
                state = "available"
            else:
                state = "locked"
            # ⚠ Only one step is ever "current", and it is on the main path.
            # A track's first available step is reported beside it, in
            # track_current, and stays "available" in the states — so the
            # sigil has one accent arc and the path one tinted row.
            if state == "available":
                if track:
                    if track_current.get(track) is None:
                        track_current[track] = sid
                elif current is None:
                    current = sid
                    state = "current"
            states[sid] = state
            if step.get("kind") != "optional":
                phase_counted += 1
                if state == "done":
                    phase_done += 1
        counts[pid] = (phase_done, phase_counted)

    orphaned = {sid: st for sid, st in run.states.items() if sid not in known}

    routines = {r["id"]: applies(r, run) and holds(r.get("gate"), doc, run, done=done, active=active)
                for r in doc.get("routines", []) if isinstance(r, dict)}

    proposals: list[dict] = []
    fields = _fields(doc)
    for step in doc.get("steps", []):
        if not isinstance(step, dict) or not step.get("auto_done"):
            continue
        sid = step["id"]
        if states.get(sid) not in ("available", "current", "locked"):
            continue
        if holds(step["auto_done"], doc, run, done=done, active=active):
            proposals.append({"id": sid, "title": step.get("title", ""),
                              "evidence": evidence(step["auto_done"], fields, run)})

    return Progress(states=states, current=current, track_current=track_current, codex=codex,
                    routines=routines, orphaned=orphaned, proposals=proposals, phase_counts=counts)


def evidence(gate: Gate, fields: dict[str, dict], run: Run) -> str:
    """The proposal sheet's mono line: `you passed level 12`, `you are on act2`."""
    parts: list[str] = []
    for key, wanted in gate.items():
        if key == "variant":
            parts.append(f"this is a {wanted} run")
        elif key == "steps_done":
            parts.append("after " + ", ".join(wanted or []))
        elif key == "codex_active":
            parts.append("with " + ", ".join(wanted or []))
        else:
            for suffix in ("_at_least", "_min", "_max", "_is"):
                if key.endswith(suffix):
                    fid = key[: -len(suffix)]
                    label = (fields.get(fid) or {}).get("label", fid).lower()
                    have = run.checkin.get(fid)
                    if suffix == "_min":
                        parts.append(f"you passed {label} {wanted}" if have != wanted else f"you reached {label} {wanted}")
                    elif suffix == "_max":
                        parts.append(f"{label} is still {have}")
                    else:
                        f = fields.get(fid) or {}
                        name = (f.get("labels") or {}).get(have, str(have))
                        parts.append(f"you are at {name}")
                    break
    return " · ".join(parts)


def bulk_skip_proposal(doc: dict, groups: list[str]) -> list[dict]:
    """
    Starting a run: the phases in the chosen skip groups, with their steps —
    a proposal the person confirms. "Skip 27 steps", never a silent skip.
    """
    out: list[dict] = []
    for phase in phases_in_order(doc):
        if phase.get("skip_group") in groups:
            steps = [s["id"] for s in steps_in(doc, phase["id"])]
            out.append({"phase": phase["id"], "name": phase.get("name", ""), "steps": steps})
    return out


def sigil_parts(doc: dict, progress: Progress, run: Run) -> list[dict]:
    """
    One arc per main-path phase: {"pct": fraction done, "state": done|now|todo}.
    The sigil takes any ordered list of parts, so a track or a group goal
    passes its own.
    """
    parts: list[dict] = []
    current_phase = None
    if progress.current:
        current_phase = next((s.get("phase") for s in doc.get("steps", []) if s.get("id") == progress.current), None)
    for phase in phases_in_order(doc):
        if phase.get("track"):
            continue
        d, n = progress.phase_counts.get(phase["id"], (0, 0))
        pct = (d / n) if n else 0.0
        state = "done" if n and d == n else ("now" if phase["id"] == current_phase else "todo")
        parts.append({"pct": pct if state != "done" else 1.0, "state": state, "id": phase["id"]})
    return parts
