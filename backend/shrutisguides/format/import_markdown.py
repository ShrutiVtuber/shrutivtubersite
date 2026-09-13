# SPDX-License-Identifier: AGPL-3.0-only
"""
Turn a guide written in the Grimoire spec's markdown into the format.

⚠ A parser, not a transcription. The Diablo spec is 1,195 lines, and its
step, routine and codex entries are written in a regular shape that a regex
holds exactly:

    **P2.7 · Title** · milestone · 10 min
    Gate: story_at_least act2 · Auto-done: … · Realm: both · Codex: whispers
    Do: …
    Done when: …
    Why: …
    One-liner: …

Parsing it means the import is checkable (the validator runs on the output),
repeatable (a corrected spec re-imports), and reusable (the next guide written
this way imports the same way). Hand-typing 1,195 lines into JSON would be
none of those.

⚠ Two things are not parsed, deliberately, and are set here with a comment
naming the spec section they come from: the check-in fields (C.2, a prose
table of types and ranges) and the Favor Token counter (G.4, a sentence).
Both are one-time knowledge that the guide editor owns after import.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# ── the shapes ──────────────────────────────────────────────────────────────

# ⚠ `· 10 min` OR `· ongoing`. The first import silently dropped every step
# without a minute count — two of the endgame ones — and the validator only
# noticed because a later step gated on one of them.
STEP_HEAD = re.compile(
    r"^\*\*([A-Z]+\d*\.\d+) · (.+?)\*\* · (milestone|optional|routine|system) · (?:(\d+) min|(ongoing))\s*$"
)
ROUTINE_HEAD = re.compile(r"^\*\*(R\d+) · (.+?)\*\*(.*?)· resets: (\w+)")
ROUTINE_ITEM = re.compile(r"^(\d+)\. (.+)$")
CODEX_HEAD = re.compile(r"^\*\*([a-z_]+) · (.+?)\*\* · (\w+) · (.+?) · (.+)$")
PHASE_ROW = re.compile(r"^\| (P\d+|S) \| (.+?) \| (.+?) \| (.+?) \|\s*$")
RANK_ROW = re.compile(r"^\| (\d+) \| (.+?) \| (.+?) \|\s*$")
HEADING = re.compile(r"^(#{1,3}) (.+)$")
CAVEAT = re.compile(r"\s*\*\*\[([^\]]+)\]\*\*")
FIELD = re.compile(r"^(Do|Done when|Why|One-liner|What|When|How): ?(.*)$")


def parse_gate(text: str) -> dict:
    """
    `level_min 60` · `steps_done [P7.1, P7.2]` · `realm seasonal` · `—`

    ⚠ `realm` becomes `variant`: the spec is Diablo-shaped and the format is
    not. Ordered values are lowercased because option ids are identifiers
    (`t1`, not `T1`); the display name lives in the field's labels.
    """
    text = text.strip()
    if text in ("—", "-", "", "always"):
        return {}
    gate: dict = {}
    # ⚠ Conditions are ANDed and separated by commas — but so are the ids
    # inside `steps_done [P7.1, P7.2]`. Split only on commas outside brackets.
    parts, depth, current = [], 0, ""
    for ch in text:
        depth += (ch == "[") - (ch == "]")
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    for part in (q for p in parts for q in re.split(r"\s+and\s+|;\s*", p)):
        if not part.strip():
            continue
        m = re.match(r"^(\w+)\s+(\[.*?\]|\S+)$", part.strip())
        if not m:
            raise ValueError(f"cannot read gate condition {part!r}")
        key, raw = m.group(1), m.group(2)
        if key == "realm":
            key = "variant"
        value: object
        if raw.startswith("["):
            value = [v.strip() for v in raw[1:-1].split(",") if v.strip()]
        elif raw.lstrip("-").isdigit():
            value = int(raw)
        else:
            value = raw.lower() if key.endswith(("_at_least", "_is")) else raw
        gate[key] = value
    return gate


def _realm(text: str) -> list[str] | None:
    text = text.strip()
    return None if text == "both" else [text]


def _strip_caveats(text: str, into: list[str]) -> str:
    for m in CAVEAT.finditer(text):
        note = m.group(1).strip()
        if note not in into:
            into.append(note)
    return CAVEAT.sub("", text).strip()


# ── the parts of the document ───────────────────────────────────────────────

def _phases(lines: list[str]) -> list[dict]:
    """The E.0 table. `same` copies the row above; the campaign rows share a skip group."""
    out: list[dict] = []
    previous: dict | None = None
    for line in lines:
        m = PHASE_ROW.match(line)
        if not m:
            continue
        pid, name, band, applies = m.groups()
        phase: dict = {"id": pid.lower(), "name": name.strip(), "order": len(out)}
        if band.strip() not in ("—", "-", ""):
            phase["band"] = band.strip()
        applies = applies.strip()
        if applies == "same" and previous is not None:
            for k in ("applies_to", "skip_group"):
                if k in previous:
                    phase[k] = previous[k]
        elif "seasonal-first-campaign" in applies:
            # ⚠ Shown on a seasonal run only if the campaign was not skipped —
            # that is a choice made when the run is created, not content. So
            # the phase applies to both and is bulk-skippable as a group.
            phase["skip_group"] = "campaign"
        elif applies not in ("both", ""):
            phase["applies_to"] = [v.strip() for v in applies.split(",")]
        if pid == "S":
            # ⚠ The track's own phase carries no applies_to: its steps do.
            # S0.* are preparation on an ETERNAL run; S1.* are seasonal.
            phase.pop("applies_to", None)
            phase["track"] = "s15"
        out.append(phase)
        previous = phase
    return out


def _steps(lines: list[str], caveats: list[str]) -> list[dict]:
    out: list[dict] = []
    step: dict | None = None
    order_in_phase: dict[str, int] = {}

    def close() -> None:
        nonlocal step
        if step is not None:
            out.append(step)
            step = None

    for line in lines:
        m = STEP_HEAD.match(line)
        if m:
            close()
            sid, title, kind, minutes, ongoing = m.groups()
            pid = sid.split(".")[0]
            pid = "s" if pid.startswith("S") else pid.lower()
            order_in_phase[pid] = order_in_phase.get(pid, 0) + 1
            step = {
                "id": sid, "phase": pid, "kind": kind, "order": order_in_phase[pid],
                "title": _strip_caveats(title, caveats), "do": "",
            }
            if ongoing:
                step["ongoing"] = True
            else:
                step["minutes"] = int(minutes)
            continue
        if step is None:
            continue
        if line.startswith("Gate:"):
            for part in line.split(" · "):
                key, _, value = part.partition(":")
                key, value = key.strip(), value.strip()
                if key == "Gate":
                    g = parse_gate(value)
                    if g:
                        step["gate"] = g
                elif key == "Auto-done":
                    g = parse_gate(value)
                    if g:
                        step["auto_done"] = g
                elif key == "Realm":
                    r = _realm(value)
                    if r:
                        step["applies_to"] = r
                elif key == "Codex":
                    step["codex"] = value
            continue
        f = FIELD.match(line)
        if f:
            key, value = f.group(1), _strip_caveats(f.group(2), caveats)
            step[{"Do": "do", "Done when": "done_when", "Why": "why",
                  "One-liner": "oneliner"}.get(key, key)] = value
            continue
        if HEADING.match(line):
            close()
    close()
    return out


def _routines(lines: list[str]) -> list[dict]:
    out: list[dict] = []
    routine: dict | None = None
    for line in lines:
        m = ROUTINE_HEAD.match(line)
        if m:
            rid, name, qualifier, resets = m.groups()
            routine = {"id": rid.lower(), "name": name.strip(), "resets": resets, "items": []}
            q = qualifier.strip(" ·")
            # ⚠ "(seasonal characters)" and "(level 70+)" are the only two
            # qualifiers the spec uses; both are content, not prose.
            if "seasonal" in q:
                routine["applies_to"] = ["seasonal"]
            lvl = re.search(r"level (\d+)\+", q)
            if lvl:
                routine["gate"] = {"level_min": int(lvl.group(1))}
            out.append(routine)
            continue
        if routine is None:
            continue
        item = ROUTINE_ITEM.match(line)
        if item:
            n = len(routine["items"]) + 1
            routine["items"].append({"id": f"{routine['id'].upper()}.{n}", "text": item.group(2).strip()})
        elif HEADING.match(line):
            routine = None
    return out


def _codex(lines: list[str], caveats: list[str]) -> list[dict]:
    out: list[dict] = []
    entry: dict | None = None
    for line in lines:
        m = CODEX_HEAD.match(line)
        if m:
            cid, name, group, show_when, ignore = m.groups()
            local: list[str] = []
            ignore = _strip_caveats(ignore, local).strip('"')
            entry = {"id": cid, "name": name.strip(), "group": group}
            g = parse_gate(show_when)
            if g:
                entry["show_when"] = g
            if ignore not in ("—", "-", ""):
                entry["ignore_until"] = ignore
            if local:
                entry["caveats"] = local
                for c in local:
                    if c not in caveats:
                        caveats.append(c)
            out.append(entry)
            continue
        if entry is None:
            continue
        f = FIELD.match(line)
        if f and f.group(1) in ("What", "When", "How"):
            entry[f.group(1).lower()] = _strip_caveats(f.group(2), caveats)
        elif HEADING.match(line):
            entry = None
    return out


def _section(lines: list[str], heading_prefix: str) -> tuple[str, list[str]]:
    """The body of one `## X.n …` section as text, and its heading."""
    body: list[str] = []
    title = ""
    inside = False
    for line in lines:
        h = HEADING.match(line)
        if h:
            if inside:
                break
            if h.group(2).startswith(heading_prefix):
                inside = True
                title = h.group(2)[len(heading_prefix):].strip(" —-")
            continue
        if inside:
            body.append(line)
    return title, body


def _codex_notes(lines: list[str]) -> list[dict]:
    title, body = _section(lines, "H.0")
    items = [l[2:].strip() for l in body if l.startswith("- ")]
    if not items:
        return []
    return [{"id": "notes", "title": title.split("(")[0].strip(), "items": items}]


def _track(lines: list[str], steps: list[dict], caveats: list[str]) -> list[dict]:
    ranks = []
    _, g3 = _section(lines, "G.3")
    for line in g3:
        m = RANK_ROW.match(line)
        if m and m.group(1).isdigit():
            ranks.append({"n": int(m.group(1)), "capstone": m.group(2).strip(), "when": m.group(3).strip()})
    sections = []
    for key, sid in (("G.4", "reliquary"), ("G.5", "blessings"), ("G.6", "specifics")):
        title, body = _section(lines, key)
        local: list[str] = []
        title = _strip_caveats(title, local)
        text = _strip_caveats("\n".join(l for l in body if l.strip()), local)
        s: dict = {"id": sid, "title": re.sub(r"\s*\(Season tab.*\)$", "", title), "body": text}
        if local:
            s["caveats"] = local
            for c in local:
                if c not in caveats:
                    caveats.append(c)
        sections.append(s)
    return [{
        "id": "s15", "name": "Season 15", "applies_to": ["seasonal"],
        "day_one": [s["id"] for s in steps if s["id"].startswith("S1.")],
        "ranks": ranks,
        # ⚠ From G.4, a sentence, not a table: "a token counter (manual), a
        # 'spend soon' nudge at ≥ 90, cap 99". Set here once; the editor owns
        # it after import.
        "counters": [{"id": "favor", "label": "Favor Tokens", "max": 99, "nudge_at": 90,
                      "nudge": "Spend soon — the cap is 99 and extra progress is wasted."}],
        "sections": sections,
    }]


# ⚠ From C.2, a prose table of types and ranges. Declared once here; the
# editor owns it after import. Ordered options are identifiers, so Torment
# tiers are t1…t12 with their display names in `labels`.
CHECKIN = [
    {"id": "level", "label": "Level", "type": "number", "min": 1, "max": 70},
    {"id": "paragon", "label": "Paragon", "type": "number", "min": 0, "max": 300,
     "show_when": {"level_min": 70}},
    {"id": "story", "label": "Story checkpoint", "type": "ordered",
     "options": ["prologue", "act1", "act2", "act3", "act4", "act5", "act6", "base_done",
                 "voh_started", "voh_done", "loh_started", "loh_done"],
     "labels": {"base_done": "Base story done", "voh_started": "Vessel of Hatred started",
                "voh_done": "Vessel of Hatred done", "loh_started": "Lord of Hatred started",
                "loh_done": "Lord of Hatred done"}},
    {"id": "difficulty", "label": "Difficulty", "type": "ordered",
     "options": ["normal", "hard", "expert", "penitent"] + [f"t{i}" for i in range(1, 13)],
     "labels": {f"t{i}": f"Torment {i}" for i in range(1, 13)}},
    {"id": "pit", "label": "Highest Pit tier cleared", "type": "number", "min": 0, "max": 150,
     "show_when": {"level_min": 60}},
    {"id": "season_rank", "label": "Season Rank", "type": "number", "min": 0, "max": 5,
     "applies_to": ["seasonal"]},
]


def import_markdown(text: str, *, guide_id: str, title: str, authors: list[str],
                    version: str, game_patch: str) -> dict:
    lines = text.splitlines()
    caveats: list[str] = []
    steps = _steps(lines, caveats)
    guide = {
        "format": 1,
        "game": {"id": "diablo-iv", "name": "Diablo IV",
                 "variants": [{"id": "eternal", "name": "Eternal"},
                              {"id": "seasonal", "name": "Seasonal"}]},
        "guide": {"id": guide_id, "title": title, "authors": authors,
                  "version": version, "game_patch": game_patch},
        "checkin": CHECKIN,
        "phases": _phases(lines),
        "steps": steps,
        "routines": _routines(lines),
        "codex": _codex(lines, caveats),
        "codex_notes": _codex_notes(lines),
        "tracks": _track(lines, steps, caveats),
    }
    if caveats:
        guide["guide"]["caveats"] = caveats
    return guide


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Import a Grimoire-format markdown guide.")
    ap.add_argument("markdown")
    ap.add_argument("--out", required=True)
    ap.add_argument("--id", default="shrutis-diablo-iv-squirrel-guide-for-warlocks")
    ap.add_argument("--title", default="Shruti's Diablo IV Squirrel Guide for Warlocks")
    ap.add_argument("--author", action="append", default=None)
    ap.add_argument("--version", default="2026-09-13")
    ap.add_argument("--game-patch", default="3.1.x + S15 PTR")
    a = ap.parse_args(argv)
    guide = import_markdown(
        Path(a.markdown).read_text(), guide_id=a.id, title=a.title,
        authors=a.author or ["shruti"], version=a.version, game_patch=a.game_patch,
    )
    Path(a.out).write_text(json.dumps(guide, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {a.out}: {len(guide['phases'])} phases, {len(guide['steps'])} steps, "
          f"{len(guide['routines'])} routines, {len(guide['codex'])} codex entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
