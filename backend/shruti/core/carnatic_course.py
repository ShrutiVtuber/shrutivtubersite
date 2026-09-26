# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio's course: importing it, and the rules that read it.

IMPORTING (`import_bundle`, run by `python -m shruti.carnatic_import`):
the bundle comes from `scripts/carnatic/build_course.py`, built from the
private course repository. The first import creates every lesson, exercise,
glossary term and recording. After that:

- a row Sophia has NOT edited in the admin follows the files: a changed
  file replaces it, and the old version goes into the revision history;
- a row she HAS edited (`admin_edited`) is never overwritten. A file that
  changed since her copy started (`base_hash`) is kept beside it
  (`file_*`), and the admin shows "a newer file version exists";
- recordings arrive as candidates; one she has decided on (approved,
  rejected, held, retired) or annotated is never touched again.

Nothing is deleted by an import; a lesson missing from the files is only
reported.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shruti.models.carnatic_course import (
    CarnaticExercise, CarnaticGlossary, CarnaticLesson, CarnaticLessonRevision, CarnaticRecording,
    CarnaticUnit,
)

BUNDLE_FORMAT = 1
LEVEL_LABEL = {"foundations": "Foundations", "intermediate": "Intermediate", "advanced": "Advanced",
               "any time": "Any time"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def lesson_fields(front: dict) -> dict:
    return {
        "slug": str(front.get("slug", "")),
        "unit": int(front.get("unit", 0) or 0),
        "order": int(front.get("order", 0) or 0),
        "status": str(front.get("status", "draft")),
        "revision": int(front.get("revision", 1) or 1),
    }


async def import_bundle(session: AsyncSession, bundle: dict, *, by: str = "import") -> dict:
    if bundle.get("format") != BUNDLE_FORMAT:
        raise ValueError(f"unknown bundle format {bundle.get('format')!r}")
    now = _now()
    summary = {k: {"created": 0, "updated": 0, "unchanged": 0, "keptEdited": 0, "newerFile": 0}
               for k in ("lessons", "exercises", "glossary", "recordings")}
    summary["units"] = 0

    for u in bundle.get("units", []):
        row = await session.get(CarnaticUnit, u["n"])
        if row is None:
            row = CarnaticUnit(n=u["n"])
            session.add(row)
        row.title, row.level, row.intro, row.lessons = u["title"], u["level"], u["intro"], u["lessons"]
        row.updated_at = now
        summary["units"] += 1

    # ── lessons
    seen: set[tuple[str, str]] = set()
    for item in bundle.get("lessons", []):
        front, body, h = item["front"], item["body"], item["hash"]
        key = (str(front["id"]), str(front.get("lang", "en")))
        seen.add(key)
        row = await session.get(CarnaticLesson, key)
        s = summary["lessons"]
        if row is None:
            row = CarnaticLesson(id=key[0], lang=key[1], front=front, body=body, base_hash=h, **lesson_fields(front))
            if row.status == "published":
                row.published_at = now
            session.add(row)
            session.add(CarnaticLessonRevision(lesson_id=key[0], lang=key[1], revision=row.revision, front=front,
                                               body=body, source="import", by=by, created_at=now))
            s["created"] += 1
        elif row.admin_edited:
            if h != row.base_hash:
                row.file_hash, row.file_front, row.file_body, row.file_seen_at = h, front, body, now
                s["newerFile"] += 1
            else:
                row.file_hash, row.file_front, row.file_body = "", None, None
            s["keptEdited"] += 1
        elif h != row.base_hash:
            was_published = row.status == "published"
            row.front, row.body, row.base_hash = front, body, h
            for k, v in lesson_fields(front).items():
                setattr(row, k, v)
            if row.status == "published" and not was_published:
                row.published_at = now
            row.file_hash, row.file_front, row.file_body = "", None, None
            row.updated_at = now
            session.add(CarnaticLessonRevision(lesson_id=key[0], lang=key[1], revision=row.revision, front=front,
                                               body=body, source="import", by=by, created_at=now))
            s["updated"] += 1
        else:
            s["unchanged"] += 1

    # ── exercises
    for item in bundle.get("exercises", []):
        row = await session.get(CarnaticExercise, item["id"])
        s = summary["exercises"]
        if row is None:
            session.add(CarnaticExercise(id=item["id"], unit=item["unit"], lesson=item.get("lesson", ""),
                                         kind=item.get("kind", "quiz"), data=item["data"], base_hash=item["hash"]))
            s["created"] += 1
        elif row.admin_edited:
            if item["hash"] != row.base_hash:
                row.file_hash, row.file_data = item["hash"], item["data"]
                s["newerFile"] += 1
            s["keptEdited"] += 1
        elif item["hash"] != row.base_hash:
            row.data, row.base_hash = item["data"], item["hash"]
            row.unit, row.lesson, row.kind = item["unit"], item.get("lesson", ""), item.get("kind", "quiz")
            row.updated_at = now
            s["updated"] += 1
        else:
            s["unchanged"] += 1

    # ── glossary
    for item in bundle.get("glossary", []):
        row = await session.get(CarnaticGlossary, item["slug"])
        s = summary["glossary"]
        data = {k: item[k] for k in ("term", "definition", "lesson", "aliases")}
        if row is None:
            session.add(CarnaticGlossary(slug=item["slug"], base_hash=item["hash"], **data))
            s["created"] += 1
        elif row.admin_edited:
            if item["hash"] != row.base_hash:
                row.file_hash, row.file_data = item["hash"], data
                s["newerFile"] += 1
            s["keptEdited"] += 1
        elif item["hash"] != row.base_hash:
            for k, v in data.items():
                setattr(row, k, v)
            row.base_hash, row.updated_at = item["hash"], now
            s["updated"] += 1
        else:
            s["unchanged"] += 1

    # ── recordings: candidates only; decisions and annotations are hers
    fields = ("provider", "url", "title", "channel", "uploader_kind", "artists", "composition", "composer", "form",
              "raga", "tala", "page_says", "listen_for", "flags", "duration", "raw")
    for item in bundle.get("recordings", []):
        row = await session.get(CarnaticRecording, item["id"])
        s = summary["recordings"]
        if row is None:
            session.add(CarnaticRecording(id=item["id"], status="candidate", base_hash=item["hash"],
                                          **{k: item.get(k) if item.get(k) is not None else "" for k in fields}))
            s["created"] += 1
        elif row.status != "candidate" or row.admin_edited or row.clips or row.sections or row.beat_map:
            s["keptEdited"] += 1
        elif item["hash"] != row.base_hash:
            for k in fields:
                setattr(row, k, item.get(k) if item.get(k) is not None else "")
            row.base_hash, row.updated_at = item["hash"], now
            s["updated"] += 1
        else:
            s["unchanged"] += 1

    existing = (await session.execute(select(CarnaticLesson.id, CarnaticLesson.lang))).all()
    summary["notInFiles"] = sorted(f"{i}:{l}" for i, l in existing if (i, l) not in seen)
    await session.commit()
    return summary


# ── reading ─────────────────────────────────────────────────────────────────

EDITOR_NOTE = re.compile(r"<!--.*?-->\s*\n?", re.S)
FOOTNOTE = re.compile(r"\[\^([A-Za-z0-9_.:-]+)\]")
EMBED_LINE = re.compile(r"^\{\{\s*([a-z]+)((?:\s+[a-z_]+=(?:\"[^\"]*\"|[^\s}]+))*)\s*\}\}\s*$")
EMBED_ATTR = re.compile(r'([a-z_]+)=("([^"]*)"|[^\s}]+)')


def strip_notes(body: str) -> str:
    return EDITOR_NOTE.sub("", body)


def editor_notes(body: str) -> list[str]:
    return [m.strip()[4:-3].strip() for m in re.findall(r"<!--.*?-->", body, re.S)]


def footnote_order(body: str) -> list[str]:
    order: list[str] = []
    for key in FOOTNOTE.findall(strip_notes(body)):
        if key not in order:
            order.append(key)
    return order


def embeds(body: str) -> list[dict]:
    out = []
    in_fence = False
    for n, line in enumerate(body.splitlines(), 1):
        if line.startswith("```"):
            if line.startswith("```sargam") and not in_fence:
                out.append({"kind": "sargam-block", "attrs": dict(
                    (m.group(1), m.group(3) if m.group(3) is not None else m.group(2))
                    for m in EMBED_ATTR.finditer(line[9:])), "line": n})
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = EMBED_LINE.match(line.strip())
        if m:
            attrs = {a.group(1): a.group(3) if a.group(3) is not None else a.group(2)
                     for a in EMBED_ATTR.finditer(m.group(2) or "")}
            out.append({"kind": m.group(1), "attrs": attrs, "line": n})
    return out


def words(body: str) -> int:
    text = strip_notes(body)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^\{\{.*\}\}$", " ", text, flags=re.M)
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", text))


KNOWN_EMBEDS = {"drone", "sargam", "tala", "raga", "mela", "gamaka", "konnakol", "recording", "quiz", "practice",
                "listen", "drill", "tuner", "composer", "tap"}
REQUIRED_FRONT = ("format", "id", "slug", "lang", "revision", "status", "unit", "order", "title", "summary",
                  "level", "minutes", "goals", "sources")


def check_lesson(front: dict, body: str, exercise_ids: set[str], drill_ids: set[str] | None = None) -> dict:
    """
    FORMAT.md §5-§6 in words: what to fix, and whether publishing is blocked.
    Saving a draft is never blocked; publishing is blocked only by a missing
    required field, an unknown exercise id or an open editor note.
    """
    problems: list[dict] = []

    def say(text: str, blocks: bool = False, kind: str = "check"):
        problems.append({"text": text, "blocksPublishing": blocks, "kind": kind})

    for f in REQUIRED_FRONT:
        if front.get(f) in (None, "", []):
            say(f"The {f} field is empty.", True, "field")
    sources = {s.get("key") for s in (front.get("sources") or []) if isinstance(s, dict)}
    used = footnote_order(body)
    for key in used:
        if key not in sources:
            say(f"Footnote {key} has no source.", False, "footnote")
    for key in sorted(sources - set(used)):
        say(f"Source {key} is never cited in the text.", False, "footnote")
    for ex in front.get("exercises") or []:
        if ex not in exercise_ids:
            say(f"Exercise {ex} doesn't exist.", True, "exercise")
    for e in embeds(body):
        if e["kind"] == "sargam-block":
            continue
        if e["kind"] not in KNOWN_EMBEDS:
            say(f"Line {e['line']}: {{{{{e['kind']}}}}} isn't a tag the site knows; it shows as a grey box.")
        elif e["kind"] in ("quiz", "practice", "listen", "tap") and e["attrs"].get("id") not in exercise_ids:
            say(f"Line {e['line']}: exercise {e['attrs'].get('id')} doesn't exist.", True, "exercise")
        elif e["kind"] == "drill" and drill_ids is not None and e["attrs"].get("id") not in drill_ids:
            say(f"Line {e['line']}: drill {e['attrs'].get('id')} doesn't exist.")
        elif e["kind"] == "sargam" and not e["attrs"].get("line"):
            say(f"Line {e['line']}: a sargam tag needs line=\"…\".")
    notes = editor_notes(body)
    for note in notes:
        say(f"An editor note is still open: “{note[:90]}”", True, "note")
    return {"problems": problems, "notes": notes,
            "publishable": not any(p["blocksPublishing"] for p in problems)}


def is_meaning_change(old: str, new: str) -> bool:
    """More than a typo-sized edit (FORMAT.md §6): about more than 12 characters changed."""
    import difflib
    a, b = strip_notes(old), strip_notes(new)
    if a == b:
        return False
    changed = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in
                  difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if tag != "equal")
    return changed > 12


def digest(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:16]


async def course_version(session: AsyncSession) -> dict:
    lessons = (await session.execute(select(CarnaticLesson.id, CarnaticLesson.lang, CarnaticLesson.revision,
                                            CarnaticLesson.updated_at)
                                     .where(CarnaticLesson.status == "published"))).all()
    ex = (await session.execute(select(func.count(), func.max(CarnaticExercise.updated_at))
                                .select_from(CarnaticExercise))).one()
    gl = (await session.execute(select(func.count(), func.max(CarnaticGlossary.updated_at))
                                .select_from(CarnaticGlossary))).one()
    un = (await session.execute(select(func.max(CarnaticUnit.updated_at)))).scalar_one()
    from shruti.models.carnatic_course import CarnaticRagaFlag
    fl = (await session.execute(select(func.max(CarnaticRagaFlag.updated_at)))).scalar_one()
    stamps = [x for x in [ex[1], gl[1], un, fl, *[l[3] for l in lessons]] if x]
    return {"digest": digest(sorted((l[0], l[1], l[2], str(l[3])) for l in lessons), str(ex), str(gl), str(un),
                             str(fl)),
            "lessons": len(lessons), "exercises": ex[0], "glossary": gl[0],
            "updatedAt": max(stamps).isoformat() if stamps else None}
