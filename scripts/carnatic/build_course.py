#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build Swara Studio's course import bundle from the private course repository.

    python3 scripts/carnatic/build_course.py <course-dir> <out.json>

The course (SYLLABUS.md, lessons/<lang>/*.md, exercises/*.yaml,
glossary.yaml, research/recordings*) is Sophia's text, written in the
private swara-studio repository and never committed here. This script reads
it as it is and writes ONE JSON file the backend imports into the database
(`python -m shruti.carnatic_import`), where she edits it in the admin.

It reads format 2 (course/FORMAT.md; FORMAT_CHANGES.md lists what changed
from format 1) and refuses anything else: a lesson that doesn't say
`format: 2`, and the format-1 fields the drafts invented, are errors that
name the file and the field. Markdown bodies are kept exactly as written
(editor notes included; the API strips them). Each item
gets a hash of its file content, so the import can tell a file that changed
from one that didn't, and never overwrites a lesson Sophia has edited.

Needs PyYAML on the machine that runs it (the sync script's machine), not in
the backend image.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

FORMAT = 2
LESSON_REQUIRED = ("format", "id", "slug", "lang", "revision", "status", "unit", "order", "title", "summary",
                   "level", "minutes", "goals", "sources")
KINDS = {"quiz", "tap", "practice", "listening", "checkpoint"}
# Format-1 and draft fields format 2 replaced (FORMAT_CHANGES.md), and what replaced them.
DROPPED = {
    "checkpoint": "kind: checkpoint", "includes": "parts:", "drills": "parts: [{drill: ...}]",
    "recording": "recordings: [{id, start, end}]", "clip": "recordings: [{id, start, end}]",
    "also": "recordings:", "also_recordings": "recordings:", "recordings_also": "recordings:", "pool": "recordings: + pick",
    "alternatives": "recordings: + pick", "comparison": "recordings:", "recording_choices": "recordings: + pick",
    "hide_raga": "guess: true", "compare_with": "private_check", "compare": "private_check", "report": "(removed: always the five counts)",
    "nadai_sequence": "segments:", "extra_targets": "targets: [...]",
}
ITEM_DROPPED = {"accept_from": "answer_from: raga", "choices": "suggest: [slugs]", "hide_raga": "guess: true",
                "compare_with": "private_check"}


class BuildError(Exception):
    pass


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def plain(obj):
    """YAML dates and other non-JSON scalars as strings."""
    if isinstance(obj, dict):
        return {str(k): plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [plain(v) for v in obj]
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj


# ── SYLLABUS.md: units and the full lesson list ─────────────────────────────

UNIT_RE = re.compile(r"^## Unit (\d+)\. (.+)$")
LESSON_RE = re.compile(r"^#### (U\d\d\.L\d\d) (.+)$")
META_RE = re.compile(r"^`([a-z0-9-]+)`\s*·\s*(.+)$")


def parse_syllabus(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    levels: dict[int, str] = {}
    for m in re.finditer(r"^\| (\d+) \| (.+?) \| (\d+) \| ([a-z ]+) \|$", text, re.M):
        levels[int(m.group(1))] = m.group(4).strip()
    units: list[dict] = []
    unit = lesson = None
    intro: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        um = UNIT_RE.match(line)
        lm = LESSON_RE.match(line)
        if um:
            unit = {"n": int(um.group(1)), "title": um.group(2).strip(), "level": levels.get(int(um.group(1)), ""),
                    "intro": "", "lessons": []}
            units.append(unit)
            lesson = None
            intro = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#"):
                intro.append(lines[j])
                j += 1
            unit["intro"] = " ".join(" ".join(intro).split())
        elif lm and unit is not None:
            lesson = {"id": lm.group(1), "title": lm.group(2).strip(), "slug": "", "level": "", "minutes": 0,
                      "after": [], "tools": [], "goals": ""}
            unit["lessons"].append(lesson)
            meta = lines[i + 1] if i + 1 < len(lines) else ""
            mm = META_RE.match(meta.strip())
            if mm:
                lesson["slug"] = mm.group(1)
                for part in [p.strip() for p in mm.group(2).split("·")]:
                    if re.fullmatch(r"\d+ min", part):
                        lesson["minutes"] = int(part.split()[0])
                    elif part.startswith("after:"):
                        v = part[6:].strip()
                        lesson["after"] = [] if v in ("none", "") else [x.strip() for x in v.split(",")]
                    elif part.startswith("tools:"):
                        lesson["tools"] = [x.strip() for x in part[6:].split(",") if x.strip()]
                    elif part in ("beginner", "intermediate", "advanced", "any"):
                        lesson["level"] = part
        elif lesson is not None and line.startswith("Goals:"):
            goals = [line[6:].strip()]
            j = i + 1
            while j < len(lines) and lines[j].strip():
                goals.append(lines[j].strip())
                j += 1
            lesson["goals"] = " ".join(goals)
        i += 1
    if len(units) < 21:
        raise BuildError(f"SYLLABUS.md: found {len(units)} units, expected 21")
    return units


# ── lessons ──────────────────────────────────────────────────────────────────

def parse_lesson(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise BuildError(f"{path.name}: no front matter")
    _, fm, body = raw.split("---", 2)
    front = plain(yaml.safe_load(fm) or {})
    if front.get("format") != FORMAT:
        raise BuildError(f"{path.name}: says format {front.get('format')!r}; the site reads format 2 (FORMAT_CHANGES.md)")
    missing = [k for k in LESSON_REQUIRED if front.get(k) in (None, "", [])]
    if missing:
        raise BuildError(f"{path.name}: front matter lacks {', '.join(missing)}")
    if front.get("level") not in ("beginner", "intermediate", "advanced"):
        raise BuildError(f"{path.name}: level {front.get('level')!r} isn't beginner, intermediate or advanced")
    return {"file": f"lessons/{path.parent.name}/{path.name}", "hash": sha(raw), "front": front,
            "body": body.lstrip("\n")}


# ── exercises ────────────────────────────────────────────────────────────────

def unit_of(ex_id: str, fallback: int, lesson: str = "") -> int:
    m = re.match(r"U(\d\d)\.", ex_id) or re.match(r"CP\.U(\d\d)$", ex_id) or re.match(r"U(\d\d)\.", lesson or "")
    return int(m.group(1)) if m else fallback


def check_exercise(where: str, ex: dict) -> None:
    """Format 2 only: the fields format 1 and the drafts used are errors that say what replaced them."""
    if ex.get("kind") not in KINDS:
        raise BuildError(f"{where}: {ex['id']} has kind {ex.get('kind')!r}; format 2 kinds are {', '.join(sorted(KINDS))}")
    for key, instead in DROPPED.items():
        if key in ex:
            raise BuildError(f"{where}: {ex['id']} uses {key}:, which format 2 replaced with {instead}")
    if "recordings" in ex and not all(isinstance(r, dict) and r.get("id") for r in ex["recordings"]):
        raise BuildError(f"{where}: {ex['id']} recordings: must be a list of {{id, start, end}}")
    if ex["kind"] == "tap" and "targets" in ex and not isinstance(ex["targets"], list):
        raise BuildError(f"{where}: {ex['id']} targets: must be a list")
    if ex["kind"] == "checkpoint" and not (isinstance(ex.get("skills"), list) and all(isinstance(k, dict) for k in ex["skills"])):
        raise BuildError(f"{where}: {ex['id']} skills: must be a list of {{id, name}}")
    for key in ("items", "auto"):
        for n, item in enumerate(ex.get(key) or [], 1):
            for bad, instead in ITEM_DROPPED.items():
                if isinstance(item, dict) and bad in item:
                    raise BuildError(f"{where}: {ex['id']} item {n} uses {bad}:, which format 2 replaced with {instead}")
            if isinstance(item, dict) and item.get("type") == "ear" and (item.get("audio") or {}).get("kind") == "recording":
                raise BuildError(f"{where}: {ex['id']} item {n}: an ear item can't play a recording (a choice with recording: instead)")


def parse_exercises(folder: Path) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for path in sorted(folder.glob("u*.yaml")) + sorted(folder.glob("selftest.yaml")):
        fallback = int(re.sub(r"\D", "", path.stem) or 0)
        items = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for ex in items:
            ex = plain(ex)
            if not isinstance(ex, dict) or "id" not in ex:
                raise BuildError(f"{path.name}: an entry without an id")
            if ex["id"] in seen:
                raise BuildError(f"{path.name}: {ex['id']} is defined twice")
            seen.add(ex["id"])
            check_exercise(path.name, ex)
            out.append({"id": ex["id"], "unit": unit_of(ex["id"], fallback, ex.get("lesson", "")), "lesson": ex.get("lesson", ""),
                        "kind": ex.get("kind", "quiz"), "hash": sha(canon(ex)), "data": ex,
                        "file": f"exercises/{path.name}"})
    return out


# ── glossary (FORMAT.md §3e: term, iso, forms, definition, lesson, source) ──

def parse_glossary(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    doc = plain(yaml.safe_load(path.read_text(encoding="utf-8")) or [])
    entries = doc.get("terms", doc.get("glossary", [])) if isinstance(doc, dict) else doc
    out = []
    for e in entries:
        term = str(e.get("term", "")).strip()
        if not term:
            continue
        if "aliases" in e:
            raise BuildError(f"glossary.yaml: {term} uses aliases:, which format 2 calls forms:")
        slug = e.get("slug") or re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        forms = [str(f) for f in (e.get("forms") or [term])]
        entry = {"slug": slug, "term": term, "definition": " ".join(str(e.get("definition", "")).split()),
                 "lesson": e.get("lesson", "") or "", "aliases": forms, "iso": str(e.get("iso", "") or ""),
                 "source": str(e.get("source", "") or "")}
        out.append({**entry, "hash": sha(canon(entry))})
    return out


# ── recordings (candidates; nothing is public until Sophia approves) ────────

SECTION_RE = re.compile(r"^## (.+?) \(([a-z0-9-]+)\)\s*$")
ID_RES = [re.compile(r"^\*\*([a-z0-9]+(?:-[a-z0-9]+)*-\d\d)\*\*\s*$"),
          re.compile(r"^- \*\*([a-z0-9]+(?:-[a-z0-9]+)*-\d\d)\*\*\s*$"),
          re.compile(r"^### ([a-z0-9]+(?:-[a-z0-9]+)*-\d\d)\s*$")]
FIELD_RE = re.compile(r"^\s*- ([A-Z][A-Za-z()/ ]+?): (.*)$")


def provider_of(url: str) -> str:
    for host, name in (("youtube.com", "youtube"), ("youtu.be", "youtube"), ("soundcloud.com", "soundcloud"),
                       ("vimeo.com", "vimeo"), ("bandcamp.com", "bandcamp"), ("archive.org", "archive")):
        if host in url:
            return name
    return ""


def uploader_kind(text: str) -> str:
    t = text.lower()
    if "unofficial" in t or "unclear" in t:
        return "unofficial"
    if "official artist" in t or "artist channel" in t or "teacher" in t:
        return "official-artist"
    if "broadcaster" in t:
        return "broadcaster"
    if "label" in t:
        return "label"
    if any(k in t for k in ("institution", "museum", "festival", "sabha", "education", "foundation", "presenter")):
        return "institution"
    return t.split("(")[0].strip()[:40]


def parse_recordings(folder: Path) -> list[dict]:
    out: dict[str, dict] = {}
    files = sorted(folder.glob("part_*.md"))
    for path in files:
        section = ("", "")
        current: dict | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            sm = SECTION_RE.match(line)
            if sm:
                section = (sm.group(1).strip(), sm.group(2))
                current = None
                continue
            idm = next((r.match(line) for r in ID_RES if r.match(line)), None)
            if idm:
                rid = idm.group(1)
                slug = section[1]
                current = {"id": rid, "fields": {}, "section": section[0],
                           "raga": "" if slug.startswith("form-") else slug,
                           "formSection": slug[5:] if slug.startswith("form-") else "",
                           "file": f"research/recordings/{path.name}"}
                out[rid] = current
                continue
            if line.startswith("## ") or line.startswith("---"):
                current = None
                continue
            fm = FIELD_RE.match(line)
            if fm and current is not None:
                current["fields"][fm.group(1).strip()] = fm.group(2).strip()
    records = []
    for rid, r in out.items():
        f = r["fields"]
        get = lambda *names: next((f[n] for n in names if n in f), "")
        url = get("URL")
        comp_line = get("Composition / composer / form", "Composition / composer", "Composition")
        parts = [p.strip() for p in comp_line.split(" / ")]
        composition = parts[0] if parts else ""
        composer = parts[1] if len(parts) > 1 else ""
        # "Chakkani Rajamargamu; composer Thyagaraja": the writers put the composer after a semicolon.
        if "; composer" in composition.lower():
            composition, _, rest = composition.partition(";")
            composer = composer or re.sub(r"(?i)^\s*composer\s*", "", rest).strip()
        composition = composition.strip()
        form = (parts[2] if len(parts) > 2 else "") or get("Form") or r["formSection"]
        artists_text = get("Artist(s)", "Artists", "Artists as stated")
        flags_text = get("Flags")
        rec = {
            "id": rid, "provider": provider_of(url), "url": url,
            "title": get("Title"), "channel": get("Channel"),
            "uploader_kind": uploader_kind(get("Uploader", "Uploader type")),
            "artists": [a.strip() for a in re.split(r";", artists_text) if a.strip()],
            "composition": composition, "composer": composer, "form": (r["formSection"] or re.sub(r"[^a-z-]", "", (form.split(" ")[0] if form else "").lower())),
            "raga": r["raga"], "tala": "",
            "page_says": {"text": get("Raga / tala on page", "Raga / tala as page states", "Raga / tala as stated",
                                      "Page states", "Raga as stated")},
            "listen_for": get("Listen for"),
            "flags": [x.strip() for x in re.split(r";", flags_text) if x.strip() and x.strip().lower() != "none"],
            "duration": get("Duration", "Length"),
            "raw": {"section": r["section"], "file": r["file"], **f},
        }
        rec["hash"] = sha(canon(rec))
        records.append(rec)
    return records


# ── EDITING.md: the questions for Sophia, as a checklist she answers in the Studio ──

def parse_questions(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == "## questions for sophia")
    except StopIteration:
        return []
    out: list[dict] = []
    group = ""
    current: list[str] | None = None

    def flush():
        if current:
            text = " ".join(" ".join(current).split())
            key = f"{group}|{re.sub(r'[^a-z0-9]+', ' ', text.lower())[:60]}"
            out.append({"id": sha(key)[:16], "group": group, "text": text, "position": len(out),
                        "lessons": sorted(set(re.findall(r"U\d\d\.L\d\d", text)))})

    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        g = re.match(r"^\*\*(.+?)\*\*", line.strip())
        if g and not line.startswith("-"):
            flush(); current = None
            group = re.sub(r"\s*\(.*\)\s*$", "", g.group(1)).strip()
            continue
        if line.startswith("- "):
            flush()
            current = [line[2:]]
        elif current is not None and line.startswith("  ") and line.strip():
            current.append(line.strip())
        elif not line.strip():
            flush(); current = None
    flush()
    return out


COMMON = {"Which", "What", "Second", "Front", "Clip", "Beat", "Your", "Research", "Sources", "Some", "Dikshitar", "Sambamoorthy", "Then",
          "Most", "None", "Shruti", "Sophia", "Data", "Choices", "Carnatic"}


def link_questions(questions: list[dict], lessons: list[dict]) -> None:
    """The lessons a question concerns: ids it names, lessons that use a recording it names, and
    lessons whose own notes for Sophia name the same proper nouns (Vatapi, Analekara…)."""
    en = [l for l in lessons if l["front"].get("lang", "en") == "en"]
    notes = {l["front"]["id"]: " ".join(re.findall(r"<!--\s*Sophia:(.*?)-->", l["body"], re.S)) for l in en}
    for q in questions:
        found = set(q["lessons"])
        for rid in re.findall(r"\b[a-z]+(?:-[a-z]+)*-\d\d\b", q["text"]):
            for l in en:
                recs = [(r.get("id") if isinstance(r, dict) else r) for r in l["front"].get("recordings") or []]
                if rid in recs or re.search(rf"id={re.escape(rid)}\b", l["body"]):
                    found.add(l["front"]["id"])
        names = [w for w in re.findall(r"\b[A-Z][a-z]{4,}(?: [a-z]+ [a-z]+)?\b", q["text"]) if w.split()[0] not in COMMON]
        for w in names:
            for lid, text in notes.items():
                if w.split()[0] in text:
                    found.add(lid)
        q["lessons"] = sorted(found)[:12]


# ── main ─────────────────────────────────────────────────────────────────────

def build(course: Path) -> dict:
    if not (course / "LICENSE.md").is_file():
        raise BuildError("course/LICENSE.md is missing; the course is not imported without it")
    units = parse_syllabus(course / "SYLLABUS.md")
    lessons = []
    for lang_dir in sorted((course / "lessons").iterdir()):
        if lang_dir.is_dir():
            for path in sorted(lang_dir.glob("*.md")):
                lessons.append(parse_lesson(path))
    ids = [(l["front"]["id"], l["front"].get("lang", "en")) for l in lessons]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise BuildError(f"lessons defined twice: {sorted(dupes)}")
    exercises = parse_exercises(course / "exercises")
    glossary = parse_glossary(course / "glossary.yaml")
    recordings = parse_recordings(course / "research" / "recordings")
    questions = parse_questions(course / "EDITING.md")
    link_questions(questions, lessons)
    try:
        commit = subprocess.run(["git", "-C", str(course), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = ""
    return {"format": FORMAT, "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "source": {"commit": commit}, "units": units, "lessons": lessons, "exercises": exercises,
            "glossary": glossary, "recordings": recordings, "questions": questions}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    try:
        bundle = build(Path(argv[1]))
    except (BuildError, yaml.YAMLError) as e:
        print(f"course: {e}", file=sys.stderr)
        return 1
    Path(argv[2]).write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"units": len(bundle["units"]), "lessons": len(bundle["lessons"]),
                      "exercises": len(bundle["exercises"]), "glossary": len(bundle["glossary"]),
                      "recordings": len(bundle["recordings"]), "questions": len(bundle["questions"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
