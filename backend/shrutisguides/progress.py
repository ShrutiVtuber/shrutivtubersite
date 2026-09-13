# SPDX-License-Identifier: AGPL-3.0-only
"""
A run as a person sees it: the view, the resets, the check-in, the re-entry
words, and what each overlay element draws.

Pure functions over plain dicts, so the site, a self-hosted tracker and the
overlays all compute the same answer from the same stored run. A stored run
is a dict with the keys the site's `guide_run` table has:

    variant, checkin, steps, routines, tracks, later, note, link_overrides,
    last_done, last_done_at (iso), last_seen_at (iso)

Nothing here writes; every function returns what to store or what to draw.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from shrutisguides import engine

REENTRY_AFTER = timedelta(hours=6)
STATES = ("done", "skipped", "later", "open")
GUIDE_KINDS = ("guide-now", "guide-sigil", "guide-path", "guide-routine", "guide-layout")
ELEMENT_KINDS = ("guide-now", "guide-sigil", "guide-path", "guide-routine", "guide-goal", "counter")
# The two kinds a host fills in rather than the run: a group's goal and the
# site's counter. The self-hosted tracker has neither and draws them empty.
HOST_KINDS = ("guide-goal", "counter")
# Where each element sits when nobody has moved it: the boards' positions at
# 1920 × 1080, so a layout with no coordinates is the frame the design shows.
DEFAULT_PLACES = {
    "guide-now": {"x": 72, "y": 72, "w": 900},
    "guide-sigil": {"x": 1620, "y": 72, "w": 224},
    "guide-path": {"x": 72, "y": 936, "w": 1776},
    "guide-routine": {"x": 72, "y": 640, "w": 760},
    "guide-goal": {"x": 72, "y": 300, "w": 860},
    "counter": {"x": 1416, "y": 300, "w": 432},
}
THEMES = ("almanac", "grimoire", "plain")
MOTIONS = ("full", "reduced", "still")


def _dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def engine_run(stored: dict) -> engine.Run:
    """The stored run as the engine reads it."""
    return engine.Run(
        variant=str(stored.get("variant") or ""),
        checkin=dict(stored.get("checkin") or {}),
        states={sid: v.get("state", "") for sid, v in (stored.get("steps") or {}).items() if isinstance(v, dict)},
        routines={rid: list(v.get("ticked", [])) for rid, v in (stored.get("routines") or {}).items() if isinstance(v, dict)},
        tracks=dict(stored.get("tracks") or {}),
    )


def zone_of(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name or "UTC")
    except Exception:                                  # noqa: BLE001
        return ZoneInfo("UTC")


def clean_checkin(values: dict, doc: dict) -> dict:
    """Only the fields the guide declares, typed and clamped as it declares them."""
    out: dict = {}
    for f in doc.get("checkin", []):
        if not isinstance(f, dict) or f["id"] not in values:
            continue
        v = values[f["id"]]
        if v is None or v == "":
            continue
        if f.get("type") == "number":
            try:
                n = float(v)
            except (TypeError, ValueError):
                continue
            lo, hi = f.get("min"), f.get("max")
            if lo is not None:
                n = max(float(lo), n)
            if hi is not None:
                n = min(float(hi), n)
            out[f["id"]] = int(n) if n == int(n) else n
        elif v in (f.get("options") or []):
            out[f["id"]] = v
    return out


def reset_due(kind: str, reset_at: datetime | None, last_seen: datetime | None, now: datetime, zone: ZoneInfo) -> bool:
    """
    Whether a routine's ticks should be cleared: session (six hours since the
    run was last seen), daily (04:00 local), weekly (Tuesday 04:00 local).
    """
    if kind == "manual":
        return False
    if kind == "session":
        return last_seen is not None and now - last_seen >= REENTRY_AFTER
    local = now.astimezone(zone)
    boundary = local.replace(hour=4, minute=0, second=0, microsecond=0)
    if local < boundary:
        boundary -= timedelta(days=1)
    if kind == "weekly":
        boundary -= timedelta(days=(boundary.weekday() - 1) % 7)
    return reset_at is None or reset_at < boundary.astimezone(timezone.utc)


def apply_resets(stored: dict, doc: dict, zone: ZoneInfo, now: datetime) -> dict | None:
    """The routines dict with due ticks cleared, or None when nothing is due."""
    changed = False
    routines = dict(stored.get("routines") or {})
    last_seen = _dt(stored.get("last_seen_at"))
    for r in doc.get("routines", []):
        if not isinstance(r, dict):
            continue
        state = routines.get(r["id"])
        if not state or not state.get("ticked"):
            continue
        if reset_due(r.get("resets", "manual"), _dt(state.get("reset_at")), last_seen, now, zone):
            routines[r["id"]] = {"ticked": [], "reset_at": now.isoformat()}
            changed = True
    return routines if changed else None


def weekday_evening(dt: datetime, zone: ZoneInfo) -> str:
    """"Tuesday evening", never "3 days ago": a weekday is a place, a count is a measurement of absence."""
    local = dt.astimezone(zone)
    part = "morning" if local.hour < 12 else "afternoon" if local.hour < 18 else "evening"
    return f"{local.strftime('%A')} {part}"


def set_step(stored: dict, doc: dict, step_id: str, state: str, now: datetime) -> dict:
    """
    The stored run after done · skipped · later · open. `open` is the undo and
    takes the step off the Later list too. Returns the fields that changed.
    """
    steps = dict(stored.get("steps") or {})
    later = list(stored.get("later") or [])
    titles = {s["id"]: s.get("title", "") for s in doc.get("steps", []) if isinstance(s, dict)}
    out: dict = {}
    if state == "open":
        steps.pop(step_id, None)
        later = [x for x in later if x.get("step") != step_id]
    else:
        steps[step_id] = {"state": state, "at": now.isoformat()}
        if state == "later" and not any(x.get("step") == step_id for x in later):
            later.append({"text": titles.get(step_id, step_id), "step": step_id, "at": now.isoformat()})
        if state != "later":
            later = [x for x in later if x.get("step") != step_id]
        if state == "done":
            out["last_done"], out["last_done_at"] = step_id, now.isoformat()
    out["steps"], out["later"] = steps, later
    return out


def view(stored: dict, doc: dict, *, zone: ZoneInfo, now: datetime, guide_meta: dict,
         version_id: int | None, published_version_id: int | None) -> dict:
    """Everything a track page needs, in one answer."""
    run = engine_run(stored)
    progress = engine.compute(doc, run)
    steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
    current = steps.get(progress.current) if progress.current else None
    last_seen = _dt(stored.get("last_seen_at"))
    reentry = None
    if last_seen and now - last_seen >= REENTRY_AFTER and stored.get("last_done"):
        last = steps.get(stored["last_done"])
        reentry = {
            "when": weekday_evening(_dt(stored.get("last_done_at")) or last_seen, zone),
            "lastDone": {"id": stored["last_done"], "title": last.get("title", "") if last else stored["last_done"]},
            "note": stored.get("note") or "",
            "next": {"id": current["id"], "title": current.get("title", "")} if current else None,
        }
    return {
        "name": stored.get("name") or "", "variant": stored.get("variant") or "",
        "guide": guide_meta,
        "versionId": version_id, "publishedVersionId": published_version_id,
        "stale": bool(version_id) and version_id != published_version_id,
        "checkin": stored.get("checkin") or {},
        "steps": stored.get("steps") or {},
        "routines": stored.get("routines") or {},
        "tracks": stored.get("tracks") or {},
        "later": stored.get("later") or [],
        "note": stored.get("note") or "",
        "linkOverrides": stored.get("link_overrides") or {},
        "lastDone": {"id": stored["last_done"], "at": stored.get("last_done_at")} if stored.get("last_done") else None,
        "lastSeenAt": stored.get("last_seen_at"),
        "reentry": reentry,
        "checkinShown": {
            f["id"]: engine.applies(f, run) and engine.holds(f.get("show_when"), doc, run)
            for f in doc.get("checkin", []) if isinstance(f, dict)
        },
        "progress": {
            "states": progress.states,
            "current": progress.current,
            "trackCurrent": progress.track_current,
            "codex": progress.codex,
            "routines": progress.routines,
            "orphaned": progress.orphaned,
            "proposals": progress.proposals,
            "phaseCounts": {k: list(v) for k, v in progress.phase_counts.items()},
            "sigil": engine.sigil_parts(doc, progress, run),
        },
    }


def element(kind: str, stored: dict, doc: dict, routine_id: str = "") -> dict:
    """What one overlay element draws — only that, so a source never carries the whole guide."""
    run = engine_run(stored)
    progress = engine.compute(doc, run)
    steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
    phases = {p["id"]: p for p in doc.get("phases", []) if isinstance(p, dict)}
    path = [s for ph in engine.phases_in_order(doc) if not ph.get("track") for s in engine.steps_in(doc, ph["id"])]
    cur = steps.get(progress.current) if progress.current else None
    phase = phases.get(cur["phase"]) if cur else None
    here = engine.steps_in(doc, phase["id"]) if phase else []
    counted = [s for s in here if s.get("kind") != "optional"]
    done_here = sum(1 for s in counted if progress.states.get(s["id"]) == "done")
    if kind == "guide-now":
        return {
            "phase": phase.get("name", "") if phase else "",
            "id": cur["id"] if cur else None,
            "title": cur.get("title", "") if cur else "",
            "line": (cur.get("oneliner") or cur.get("do", "").split("\n")[0]) if cur else "",
            "count": f"{done_here} of {len(counted)}" if phase else "",
            "finished": cur is None and bool(path) and all(progress.states.get(s["id"]) in ("done", "skipped") for s in path),
        }
    if kind == "guide-sigil":
        main = [ph for ph in engine.phases_in_order(doc) if not ph.get("track")]
        idx = main.index(phase) + 1 if phase in main else 0
        return {"parts": engine.sigil_parts(doc, progress, run),
                "label": f"{idx}/{len(main)}" if idx else "",
                "count": f"{done_here} of {len(counted)}" if phase else ""}
    if kind == "guide-path":
        i = next((k for k, s in enumerate(path) if s["id"] == progress.current), None)
        window = path[-6:] if i is None else path[max(0, i - 2): i + 4]
        return {"strip": [{"id": s["id"], "title": s.get("title", ""), "state": progress.states.get(s["id"], "locked")} for s in window]}
    if kind == "guide-routine":
        routines = [r for r in doc.get("routines", []) if isinstance(r, dict)]
        routine = next((r for r in routines if r["id"] == routine_id), None) or (routines[0] if routines else None)
        if routine is None:
            return {"routine": None}
        ticked = set((stored.get("routines") or {}).get(routine["id"], {}).get("ticked", []))
        return {"routine": {"name": routine.get("name", ""), "open": progress.routines.get(routine["id"], False),
                            "items": [{"id": i["id"], "text": i["text"], "done": i["id"] in ticked} for i in routine.get("items", [])],
                            "count": f"{len(ticked)} / {len(routine.get('items', []))}"}}
    return {}


def export(stored: dict, guide_meta: dict, now: datetime) -> dict:
    """A run file, so nobody's progress is trapped."""
    return {
        "format": 1, "kind": "run", "guide": guide_meta,
        "name": stored.get("name") or "", "variant": stored.get("variant") or "",
        "checkin": stored.get("checkin") or {}, "steps": stored.get("steps") or {},
        "routines": stored.get("routines") or {}, "tracks": stored.get("tracks") or {},
        "later": stored.get("later") or [], "note": stored.get("note") or "",
        "linkOverrides": stored.get("link_overrides") or {}, "lastDone": stored.get("last_done") or "",
        "lastDoneAt": stored.get("last_done_at"), "exportedAt": now.isoformat(),
    }


def from_export(r: dict, doc: dict, fallback_name: str) -> dict:
    """The stored fields from a run file. Raises ValueError when it is not one."""
    if r.get("kind") != "run":
        raise ValueError("that is not a run file")
    return {
        "name": str(r.get("name") or fallback_name)[:80], "variant": str(r.get("variant") or ""),
        "checkin": clean_checkin(r.get("checkin") or {}, doc),
        "steps": {str(k): v for k, v in (r.get("steps") or {}).items() if isinstance(v, dict) and v.get("state") in ("done", "skipped", "later")},
        "routines": {str(k): v for k, v in (r.get("routines") or {}).items() if isinstance(v, dict)},
        "tracks": {str(k): v for k, v in (r.get("tracks") or {}).items() if isinstance(v, dict)},
        "later": [x for x in (r.get("later") or []) if isinstance(x, dict) and x.get("text")][:200],
        "note": str(r.get("note") or "")[:2000],
        "link_overrides": {str(k): v for k, v in (r.get("linkOverrides") or {}).items() if isinstance(v, list)},
        "last_done": str(r.get("lastDone") or ""),
    }


def clean_layout(layout: Any) -> list[dict]:
    """
    A layout as stored: [{kind, x, y, w, routine_id, shows}], clamped to the
    1920 × 1080 canvas. Unknown kinds are dropped; nothing else is invented.
    """
    out: list[dict] = []
    if not isinstance(layout, list):
        return out
    for e in layout:
        if not isinstance(e, dict) or e.get("kind") not in ELEMENT_KINDS:
            continue
        place = DEFAULT_PLACES[e["kind"]]
        def num(key: str, default: float, lo: float, hi: float) -> int:
            try:
                v = float(e.get(key, default))
            except (TypeError, ValueError):
                v = default
            return int(min(hi, max(lo, v)))
        out.append({
            "kind": e["kind"],
            "x": num("x", place["x"], 0, 1920), "y": num("y", place["y"], 0, 1080),
            "w": num("w", place["w"], 120, 1920),
            "routine_id": str(e.get("routine_id") or "")[:80],
            "shows": str(e.get("shows") or "")[:40],
            # A goal element draws a group, not the run: the group's join code.
            "group": str(e.get("group") or "")[:12].upper(),
            "counter_id": num("counter_id", 0, 0, 10**9),
        })
    return out[:12]


def layout_elements(layout: list[dict], stored: dict, doc: dict) -> list[dict]:
    """Every element of a layout, drawn: the placement plus what the element shows."""
    # A goal element is a group's, not the run's; the host fills it in (the
    # site knows groups, the self-hosted tracker has none and draws it empty).
    return [{**e, "element": {} if e["kind"] in HOST_KINDS else element(e["kind"], stored, doc, e.get("routine_id", ""))} for e in layout]
