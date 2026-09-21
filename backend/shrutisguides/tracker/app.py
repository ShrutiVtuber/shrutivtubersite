# SPDX-License-Identifier: AGPL-3.0-only
"""
The self-hosted tracker.

One person's runs and overlays on their own machine — the same API shapes
as shrutivtuber.com's `/api/runs` and `/api/overlay/guide`, computed by the
same shared functions (`shrutisguides.progress`), so the phone app and the
overlays cannot tell the two apart. Guides come from the catalogue on the
site (pulled by address) or from a guide file.

    SHRUTI_SITE_URL   where guides and build templates are pulled from   default https://shrutivtuber.com
    TRACKER_DATA      where the database lives           default ./data
    TRACKER_SECRET    a bearer token for writes; unset = open (one machine, one person)
    TRACKER_TZ        the person's timezone              default UTC

Run it:  uvicorn shrutisguides.tracker.app:app --host 0.0.0.0 --port 8210
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

from shrutisguides import builds, engine, progress
from shrutisguides.format.validate import validate
from shrutisguides.gamedata import KINDS, GameData, clean_plan, plan_goals, plan_summary, plan_to_categories, recipe_for
from shrutisguides.gamedata.calc import sheet as compute_sheet

VERSION = "0.1.0"
SITE = os.environ.get("SHRUTI_SITE_URL", "https://shrutivtuber.com").rstrip("/")
DATA = Path(os.environ.get("TRACKER_DATA", "./data"))
SECRET = os.environ.get("TRACKER_SECRET", "").strip()
ZONE = progress.zone_of(os.environ.get("TRACKER_TZ", "UTC"))
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Squirrel Guides — tracker", version=VERSION)


# ── storage ──────────────────────────────────────────────────────────────────

def db() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DATA / "tracker.sqlite3")
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS guide (
            id INTEGER PRIMARY KEY, game_slug TEXT NOT NULL, slug TEXT NOT NULL, game_name TEXT NOT NULL,
            title TEXT NOT NULL, body TEXT NOT NULL, fetched_at TEXT NOT NULL, UNIQUE(game_slug, slug));
        CREATE TABLE IF NOT EXISTS run (
            id INTEGER PRIMARY KEY, guide_id INTEGER NOT NULL REFERENCES guide(id),
            stored TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS build_template (
            id INTEGER PRIMARY KEY, game_slug TEXT NOT NULL, game_name TEXT NOT NULL, name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '', categories TEXT NOT NULL DEFAULT '[]',
            visible INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0, UNIQUE(game_slug, name));
        CREATE TABLE IF NOT EXISTS build (
            id INTEGER PRIMARY KEY, template_id INTEGER REFERENCES build_template(id), run_id INTEGER REFERENCES run(id),
            name TEXT NOT NULL, variant TEXT NOT NULL DEFAULT '', goals TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL,
            game_slug TEXT NOT NULL DEFAULT '', game_name TEXT NOT NULL DEFAULT '', plan TEXT NOT NULL DEFAULT '{}',
            categories TEXT NOT NULL DEFAULT '[]');
        CREATE TABLE IF NOT EXISTS overlay (
            id INTEGER PRIMARY KEY, token TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, run_id INTEGER REFERENCES run(id),
            build_id INTEGER REFERENCES build(id),
            routine_id TEXT NOT NULL DEFAULT '', theme TEXT NOT NULL DEFAULT 'almanac', motion TEXT NOT NULL DEFAULT 'reduced',
            label TEXT NOT NULL DEFAULT '', last_seen TEXT, layout TEXT NOT NULL DEFAULT '[]');
    """)
    if "plan" not in {r["name"] for r in con.execute("PRAGMA table_info(build)").fetchall()}:
        # An older tracker: every build stood on a template. A planned build
        # stands on the game's data instead, so template_id may be empty —
        # and SQLite cannot loosen a NOT NULL, so the table is rebuilt beside
        # itself (never renamed away: overlays point at build(id)).
        con.executescript("""
            CREATE TABLE build_new (
                id INTEGER PRIMARY KEY, template_id INTEGER REFERENCES build_template(id), run_id INTEGER REFERENCES run(id),
                name TEXT NOT NULL, variant TEXT NOT NULL DEFAULT '', goals TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL,
                game_slug TEXT NOT NULL DEFAULT '', game_name TEXT NOT NULL DEFAULT '', plan TEXT NOT NULL DEFAULT '{}',
                categories TEXT NOT NULL DEFAULT '[]');
            INSERT INTO build_new (id, template_id, run_id, name, variant, goals, updated_at)
                SELECT id, template_id, run_id, name, variant, goals, updated_at FROM build;
            DROP TABLE build;
            ALTER TABLE build_new RENAME TO build;
        """)
        con.commit()
    columns = {r["name"] for r in con.execute("PRAGMA table_info(overlay)").fetchall()}
    if "layout" not in columns:
        con.execute("ALTER TABLE overlay ADD COLUMN layout TEXT NOT NULL DEFAULT '[]'")
        con.commit()
    if "build_id" not in columns:
        # An older tracker: the overlay belonged to a run and nothing else.
        # SQLite cannot loosen a NOT NULL, so the table is rebuilt in place.
        con.executescript("""
            ALTER TABLE overlay RENAME TO overlay_old;
            CREATE TABLE overlay (
                id INTEGER PRIMARY KEY, token TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, run_id INTEGER REFERENCES run(id),
                build_id INTEGER REFERENCES build(id),
                routine_id TEXT NOT NULL DEFAULT '', theme TEXT NOT NULL DEFAULT 'almanac', motion TEXT NOT NULL DEFAULT 'reduced',
                label TEXT NOT NULL DEFAULT '', last_seen TEXT, layout TEXT NOT NULL DEFAULT '[]');
            INSERT INTO overlay (id, token, kind, run_id, routine_id, theme, motion, label, last_seen, layout)
                SELECT id, token, kind, run_id, routine_id, theme, motion, label, last_seen, layout FROM overlay_old;
            DROP TABLE overlay_old;
        """)
        con.commit()
    return con


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _guide_row(con: sqlite3.Connection, guide_id: int) -> sqlite3.Row:
    row = con.execute("SELECT * FROM guide WHERE id = ?", (guide_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such guide")
    return row


def _run_row(con: sqlite3.Connection, run_id: int) -> sqlite3.Row:
    row = con.execute("SELECT * FROM run WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such run")
    return row


def _stored(row: sqlite3.Row) -> dict:
    return json.loads(row["stored"])


def _save(con: sqlite3.Connection, run_id: int, stored: dict) -> None:
    con.execute("UPDATE run SET stored = ?, updated_at = ? WHERE id = ?", (json.dumps(stored), _now().isoformat(), run_id))
    con.commit()


def _meta(g: sqlite3.Row) -> dict:
    return {"id": g["id"], "slug": g["slug"], "title": g["title"], "game": {"slug": g["game_slug"], "name": g["game_name"]}}


def _answer(con: sqlite3.Connection, run: sqlite3.Row, *, touch: bool = True) -> dict:
    g = _guide_row(con, run["guide_id"])
    doc = json.loads(g["body"])
    stored = _stored(run)
    now = _now()
    out = progress.view(stored, doc, zone=ZONE, now=now, guide_meta=_meta(g), version_id=None, published_version_id=None)
    out["id"] = run["id"]
    routines = progress.apply_resets(stored, doc, ZONE, now)
    changed = False
    if routines is not None:
        stored["routines"] = routines
        changed = True
    if touch:
        stored["last_seen_at"] = now.isoformat()
        changed = True
    if changed:
        _save(con, run["id"], stored)
    return out


# ── the one person ───────────────────────────────────────────────────────────

def owner(authorization: str = Header(default="")) -> None:
    """Writes need the secret when one is set. Unset means one machine, one person."""
    if not SECRET:
        return
    if not authorization.lower().startswith("bearer ") or not secrets.compare_digest(authorization[7:].strip(), SECRET):
        raise HTTPException(401, "not this tracker's person")


# ── health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict:
    con = db()
    n = con.execute("SELECT COUNT(*) FROM guide").fetchone()[0]
    templates = con.execute("SELECT COUNT(*) FROM build_template").fetchone()[0]
    return {"ok": True, "version": VERSION, "guides": n, "templates": templates, "site": SITE}


# ── guides: the library ──────────────────────────────────────────────────────

@app.get("/api/guides")
def guides() -> list[dict]:
    con = db()
    return [{**_meta(g), "fetchedAt": g["fetched_at"]} for g in con.execute("SELECT * FROM guide ORDER BY title").fetchall()]


class PullIn(BaseModel):
    game: str
    slug: str


def _store_guide(con: sqlite3.Connection, doc: dict, *, game_slug: str, slug: str, game_name: str, title: str) -> dict:
    problems = validate(doc)
    if problems:
        raise HTTPException(422, {"problems": [{"path": p.path, "message": p.message} for p in problems]})
    con.execute("""INSERT INTO guide (game_slug, slug, game_name, title, body, fetched_at) VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(game_slug, slug) DO UPDATE SET body = excluded.body, title = excluded.title,
                   game_name = excluded.game_name, fetched_at = excluded.fetched_at""",
                (game_slug, slug, game_name, title, json.dumps(doc), _now().isoformat()))
    con.commit()
    return _meta(con.execute("SELECT * FROM guide WHERE game_slug = ? AND slug = ?", (game_slug, slug)).fetchone())


@app.post("/api/guides/pull", status_code=201, dependencies=[Depends(owner)])
def pull(body: PullIn) -> dict:
    """Download a published guide from the site by its address."""
    try:
        r = httpx.get(f"{SITE}/api/guides/{body.game}/{body.slug}", timeout=20)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"{SITE} did not answer") from exc
    if r.status_code != 200:
        raise HTTPException(404, "no such guide on the site")
    card = r.json()
    doc = card["body"]
    con = db()
    return _store_guide(con, doc, game_slug=body.game, slug=body.slug,
                        game_name=card.get("game", {}).get("name", doc.get("game", {}).get("name", "")), title=card.get("title", doc.get("guide", {}).get("title", "")))


@app.post("/api/guides/import", status_code=201, dependencies=[Depends(owner)])
def import_guide(doc: dict) -> dict:
    """A guide file — the same one any guide's page offers to download."""
    con = db()
    return _store_guide(con, doc, game_slug=str(doc.get("game", {}).get("id", "")), slug=str(doc.get("guide", {}).get("id", "")),
                        game_name=str(doc.get("game", {}).get("name", "")), title=str(doc.get("guide", {}).get("title", "")))


@app.get("/api/guides/{game}/{slug}")
def one_guide(game: str, slug: str) -> dict:
    con = db()
    g = con.execute("SELECT * FROM guide WHERE game_slug = ? AND slug = ?", (game, slug)).fetchone()
    if g is None:
        raise HTTPException(404, "no such guide")
    return {**_meta(g), "body": json.loads(g["body"])}


# ── runs ─────────────────────────────────────────────────────────────────────

class RunIn(BaseModel):
    guide_id: int
    name: str = ""
    variant: str = ""
    skip_steps: list[str] = []
    checkin: dict = {}


@app.get("/api/runs", dependencies=[Depends(owner)])
def runs(guide: int | None = None) -> list[dict]:
    con = db()
    rows = con.execute("SELECT * FROM run" + (" WHERE guide_id = ?" if guide else "") + " ORDER BY updated_at DESC",
                       (guide,) if guide else ()).fetchall()
    out = []
    for row in rows:
        g = _guide_row(con, row["guide_id"]); doc = json.loads(g["body"]); stored = _stored(row)
        p = engine.compute(doc, progress.engine_run(stored))
        steps = {s["id"]: s for s in doc.get("steps", []) if isinstance(s, dict)}
        cur = steps.get(p.current) if p.current else None
        out.append({"id": row["id"], "name": stored.get("name", ""), "variant": stored.get("variant", ""), "guide": _meta(g),
                    "now": {"id": cur["id"], "title": cur.get("title", "")} if cur else None,
                    "sigil": engine.sigil_parts(doc, p, progress.engine_run(stored)), "updatedAt": row["updated_at"]})
    return out


@app.get("/api/runs/skip-proposal", dependencies=[Depends(owner)])
def skip_proposal(guide: int, groups: str = "") -> list[dict]:
    con = db()
    doc = json.loads(_guide_row(con, guide)["body"])
    return engine.bulk_skip_proposal(doc, [x.strip() for x in groups.split(",") if x.strip()])


@app.post("/api/runs", status_code=201, dependencies=[Depends(owner)])
def create(body: RunIn) -> dict:
    con = db()
    g = _guide_row(con, body.guide_id); doc = json.loads(g["body"])
    variants = {v.get("id") for v in doc.get("game", {}).get("variants", []) if isinstance(v, dict)}
    variant = body.variant if body.variant in variants else (sorted(variants)[0] if variants else "")
    known = {s["id"] for s in doc.get("steps", []) if isinstance(s, dict)}
    now = _now().isoformat()
    stored = {"name": body.name.strip()[:80] or g["title"], "variant": variant, "checkin": progress.clean_checkin(body.checkin, doc),
              "steps": {sid: {"state": "skipped", "at": now} for sid in body.skip_steps if sid in known},
              "routines": {}, "tracks": {}, "later": [], "note": "", "link_overrides": {}, "last_done": "", "last_done_at": None, "last_seen_at": None}
    cur = con.execute("INSERT INTO run (guide_id, stored, updated_at) VALUES (?, ?, ?)", (g["id"], json.dumps(stored), now))
    con.commit()
    return _answer(con, _run_row(con, cur.lastrowid))


@app.get("/api/runs/{run_id}", dependencies=[Depends(owner)])
def one(run_id: int) -> dict:
    con = db()
    return _answer(con, _run_row(con, run_id))


class LayoutIn(BaseModel):
    layout: list
    theme: str | None = None
    motion: str | None = None
    label: str | None = None


@app.put("/api/runs/{run_id}/overlays/{token_id}", dependencies=[Depends(owner)])
def set_layout(run_id: int, token_id: int, body: LayoutIn) -> dict:
    """Save a layout — the designer's one write."""
    con = db(); o = con.execute("SELECT * FROM overlay WHERE id = ? AND run_id = ?", (token_id, run_id)).fetchone()
    if o is None:
        raise HTTPException(404, "no such overlay")
    con.execute("UPDATE overlay SET layout = ?, theme = ?, motion = ?, label = ? WHERE id = ?",
                (json.dumps(progress.clean_layout(body.layout)),
                 body.theme if body.theme in progress.THEMES else o["theme"],
                 body.motion if body.motion in progress.MOTIONS else o["motion"],
                 (body.label or o["label"]).strip()[:80], token_id))
    con.commit()
    return {"ok": True}


class RunPatch(BaseModel):
    name: str | None = None
    variant: str | None = None


@app.put("/api/runs/{run_id}", dependencies=[Depends(owner)])
def rename(run_id: int, body: RunPatch) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    doc = json.loads(_guide_row(con, row["guide_id"])["body"])
    if body.name is not None:
        stored["name"] = body.name.strip()[:80] or stored.get("name", "")
    if body.variant is not None and body.variant in {v.get("id") for v in doc.get("game", {}).get("variants", []) if isinstance(v, dict)}:
        stored["variant"] = body.variant
    _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


@app.delete("/api/runs/{run_id}", dependencies=[Depends(owner)])
def delete(run_id: int) -> dict:
    con = db(); _run_row(con, run_id)
    con.execute("DELETE FROM overlay WHERE run_id = ?", (run_id,)); con.execute("DELETE FROM run WHERE id = ?", (run_id,)); con.commit()
    return {"ok": True}


class CheckIn(BaseModel):
    values: dict


@app.post("/api/runs/{run_id}/checkin", dependencies=[Depends(owner)])
def checkin(run_id: int, body: CheckIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    doc = json.loads(_guide_row(con, row["guide_id"])["body"])
    merged = dict(stored.get("checkin") or {}); merged.update(progress.clean_checkin(body.values, doc)); stored["checkin"] = merged
    _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class StepIn(BaseModel):
    state: str


@app.post("/api/runs/{run_id}/steps/{step_id}", dependencies=[Depends(owner)])
def set_step(run_id: int, step_id: str, body: StepIn) -> dict:
    if body.state not in progress.STATES:
        raise HTTPException(422, "state is done, skipped, later or open")
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    doc = json.loads(_guide_row(con, row["guide_id"])["body"])
    stored.update(progress.set_step(stored, doc, step_id, body.state, _now()))
    _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class AcceptIn(BaseModel):
    steps: list[str]


@app.post("/api/runs/{run_id}/accept", dependencies=[Depends(owner)])
def accept(run_id: int, body: AcceptIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    doc = json.loads(_guide_row(con, row["guide_id"])["body"])
    known = {s["id"] for s in doc.get("steps", []) if isinstance(s, dict)}
    steps = dict(stored.get("steps") or {}); now = _now().isoformat()
    for sid in body.steps:
        if sid in known:
            steps[sid] = {"state": "done", "at": now}
    stored["steps"] = steps
    _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class TicksIn(BaseModel):
    ticked: list[str]


@app.post("/api/runs/{run_id}/routines/{routine_id}", dependencies=[Depends(owner)])
def tick(run_id: int, routine_id: str, body: TicksIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    routines = dict(stored.get("routines") or {}); prior = routines.get(routine_id) or {}
    routines[routine_id] = {"ticked": body.ticked, "reset_at": prior.get("reset_at") or _now().isoformat()}
    stored["routines"] = routines; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


@app.post("/api/runs/{run_id}/routines/{routine_id}/reset", dependencies=[Depends(owner)])
def reset_routine(run_id: int, routine_id: str) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    routines = dict(stored.get("routines") or {}); routines[routine_id] = {"ticked": [], "reset_at": _now().isoformat()}
    stored["routines"] = routines; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class LaterIn(BaseModel):
    text: str
    step: str | None = None


@app.post("/api/runs/{run_id}/later", dependencies=[Depends(owner)])
def park(run_id: int, body: LaterIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    text = body.text.strip()[:280]
    if not text:
        raise HTTPException(422, "say what to park")
    later = list(stored.get("later") or []); later.append({"text": text, "step": body.step, "at": _now().isoformat()})
    stored["later"] = later; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


@app.delete("/api/runs/{run_id}/later/{index}", dependencies=[Depends(owner)])
def unpark(run_id: int, index: int) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    later = list(stored.get("later") or [])
    if 0 <= index < len(later):
        gone = later.pop(index)
        if gone.get("step"):
            steps = dict(stored.get("steps") or {})
            if steps.get(gone["step"], {}).get("state") == "later":
                steps.pop(gone["step"], None)
            stored["steps"] = steps
    stored["later"] = later; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class NoteIn(BaseModel):
    text: str


@app.put("/api/runs/{run_id}/note", dependencies=[Depends(owner)])
def note(run_id: int, body: NoteIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    stored["note"] = body.text.strip()[:2000]; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class TrackIn(BaseModel):
    rank: int | None = None
    day_one: list[str] | None = None
    counters: dict | None = None


@app.put("/api/runs/{run_id}/track/{track_id}", dependencies=[Depends(owner)])
def track(run_id: int, track_id: str, body: TrackIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    tracks = dict(stored.get("tracks") or {}); state = dict(tracks.get(track_id) or {})
    if body.rank is not None:
        state["rank"] = max(0, int(body.rank))
    if body.day_one is not None:
        state["day_one"] = [str(x) for x in body.day_one]
    if body.counters is not None:
        state["counters"] = {str(k): int(v) for k, v in body.counters.items() if isinstance(v, (int, float))}
    tracks[track_id] = state; stored["tracks"] = tracks; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


class LinksIn(BaseModel):
    links: list[dict]


@app.put("/api/runs/{run_id}/links/{step_id}", dependencies=[Depends(owner)])
def links(run_id: int, step_id: str, body: LinksIn) -> dict:
    con = db(); row = _run_row(con, run_id); stored = _stored(row)
    overrides = dict(stored.get("link_overrides") or {})
    clean = [{"label": str(l.get("label", ""))[:120], "url": str(l.get("url", ""))[:500], "type": str(l.get("type", ""))[:20]}
             for l in body.links if isinstance(l, dict) and str(l.get("url", "")).startswith(("http://", "https://"))]
    if clean:
        overrides[step_id] = clean
    else:
        overrides.pop(step_id, None)
    stored["link_overrides"] = overrides; _save(con, run_id, stored)
    return _answer(con, _run_row(con, run_id))


@app.get("/api/runs/{run_id}/export", dependencies=[Depends(owner)])
def export_run(run_id: int):
    con = db(); row = _run_row(con, run_id); g = _guide_row(con, row["guide_id"])
    body = progress.export(_stored(row), {"game": g["game_slug"], "slug": g["slug"], "title": g["title"]}, _now())
    return JSONResponse(body, headers={"Content-Disposition": f'attachment; filename="{g["slug"]}.run.json"'})


class ImportIn(BaseModel):
    guide_id: int
    run: dict


@app.post("/api/runs/import", status_code=201, dependencies=[Depends(owner)])
def import_run(body: ImportIn) -> dict:
    con = db(); g = _guide_row(con, body.guide_id); doc = json.loads(g["body"])
    try:
        fields = progress.from_export(body.run, doc, g["title"])
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    stored = {**fields, "last_done_at": body.run.get("lastDoneAt"), "last_seen_at": None}
    cur = con.execute("INSERT INTO run (guide_id, stored, updated_at) VALUES (?, ?, ?)", (g["id"], json.dumps(stored), _now().isoformat()))
    con.commit()
    return _answer(con, _run_row(con, cur.lastrowid))


# ── overlays ─────────────────────────────────────────────────────────────────

class TokenIn(BaseModel):
    kind: str
    theme: str = "almanac"
    motion: str = "reduced"
    routine_id: str = ""
    label: str = ""
    layout: list = []


# ── builds: one character's goals, slot by slot ──────────────────────────────
#
# The same shapes as shrutivtuber.com's /api/builds, computed by the same
# shared functions (shrutisguides.builds). Templates are pulled from the
# site by name, imported from a file, or written here — the tracker is one
# person's, so its person is the admin.

def _template_row(con: sqlite3.Connection, template_id: int) -> sqlite3.Row:
    row = con.execute("SELECT * FROM build_template WHERE id = ?", (template_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such template")
    return row


def _build_row(con: sqlite3.Connection, build_id: int) -> sqlite3.Row:
    row = con.execute("SELECT * FROM build WHERE id = ?", (build_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such build")
    return row


def _template_view(t: sqlite3.Row) -> dict:
    return {"id": t["id"], "name": t["name"], "description": t["description"], "visible": bool(t["visible"]), "position": t["position"],
            "game": {"slug": t["game_slug"], "name": t["game_name"]}, "categories": json.loads(t["categories"] or "[]")}


def _categories_of(con: sqlite3.Connection, b: sqlite3.Row) -> list:
    """A planned build carries its own categories; one made from a template reads the template's."""
    own = json.loads(b["categories"] or "[]")
    if own or not b["template_id"]:
        return own
    return _template_view(_template_row(con, b["template_id"]))["categories"]


def _build_view(con: sqlite3.Connection, b: sqlite3.Row, with_sheet: bool = False) -> dict:
    if b["template_id"]:
        t = _template_view(_template_row(con, b["template_id"]))
    else:
        # A planned build shown in a template's shape, so the phone and the
        # overlay — which read template.categories and template.game — need
        # no second shape for it.
        t = {"id": None, "name": "Planned", "description": "", "visible": True, "position": 0,
             "game": {"slug": b["game_slug"], "name": b["game_name"]}, "categories": json.loads(b["categories"] or "[]")}
    goals = json.loads(b["goals"] or "{}")
    view = {"id": b["id"], "name": b["name"], "variant": b["variant"], "runId": b["run_id"], "template": t, "goals": goals,
            "progress": builds.progress(_categories_of(con, b), goals), "updatedAt": b["updated_at"]}
    plan = json.loads(b["plan"] or "{}")
    if plan:
        view["plan"] = plan
        view["planned"] = plan_summary(plan, gamedata())
        if with_sheet:
            # off the list on purpose: a sheet walks every chosen record
            view["sheet"] = compute_sheet(plan, gamedata())
    return view


def _build_element(view: dict) -> dict:
    return builds.element(view["name"], view["variant"], view["template"]["game"]["name"], view["progress"])


def _store_template(con: sqlite3.Connection, t: dict) -> dict:
    """Upsert by game and name; the categories are cleaned once, here."""
    slug = builds.ident(t.get("game") or (t.get("game_slug") if isinstance(t, dict) else ""), "game") if not isinstance(t.get("game"), dict) else str(t["game"].get("slug") or "game")
    game_name = (t["game"].get("name") if isinstance(t.get("game"), dict) else (t.get("game_name") or t.get("game") or slug)) or slug
    name = str(t.get("name") or "").strip()[:80]
    if not name:
        raise HTTPException(422, "a template needs a name")
    cats = json.dumps(builds.clean_categories(t.get("categories")))
    con.execute("""INSERT INTO build_template (game_slug, game_name, name, description, categories, visible, position)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(game_slug, name) DO UPDATE SET game_name = excluded.game_name, description = excluded.description,
                   categories = excluded.categories, visible = excluded.visible, position = excluded.position""",
                (slug, str(game_name)[:80], name, str(t.get("description") or "")[:400], cats,
                 1 if t.get("visible", True) else 0, int(t.get("position") or 0)))
    con.commit()
    return _template_view(con.execute("SELECT * FROM build_template WHERE game_slug = ? AND name = ?", (slug, name)).fetchone())


@app.get("/api/builds/templates")
def build_templates(game: str = "") -> list[dict]:
    con = db()
    rows = con.execute("SELECT * FROM build_template WHERE visible = 1" + (" AND game_slug = ?" if game else "") + " ORDER BY position, id",
                       (game,) if game else ()).fetchall()
    return [_template_view(t) for t in rows]


@app.post("/api/builds/templates/pull", status_code=201, dependencies=[Depends(owner)])
def pull_templates() -> dict:
    """Her templates, from the site: every visible one, upserted by game and name."""
    try:
        r = httpx.get(f"{SITE}/api/builds/templates", timeout=20)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"could not reach {SITE}: {type(exc).__name__}")
    if r.status_code != 200:
        raise HTTPException(502, f"{SITE} answered {r.status_code}")
    con = db()
    got = [_store_template(con, t) for t in r.json() if isinstance(t, dict)]
    return {"ok": True, "templates": got}


@app.get("/api/builds/admin/templates", dependencies=[Depends(owner)])
def admin_templates() -> list[dict]:
    con = db()
    rows = con.execute("SELECT * FROM build_template ORDER BY position, id").fetchall()
    counts = dict(con.execute("SELECT template_id, COUNT(*) FROM build GROUP BY template_id").fetchall())
    return [{**_template_view(t), "builds": int(counts.get(t["id"], 0))} for t in rows]


@app.post("/api/builds/admin/templates", status_code=201, dependencies=[Depends(owner)])
def create_template(body: dict) -> dict:
    return _store_template(db(), body)


@app.put("/api/builds/admin/templates/{template_id}", dependencies=[Depends(owner)])
def update_template(template_id: int, body: dict) -> dict:
    con = db(); t = _template_row(con, template_id)
    con.execute("UPDATE build_template SET name = ?, description = ?, categories = ?, visible = ?, position = ? WHERE id = ?",
                (str(body.get("name") or t["name"]).strip()[:80], str(body.get("description") or "")[:400],
                 json.dumps(builds.clean_categories(body.get("categories"))), 1 if body.get("visible", True) else 0,
                 int(body.get("position") or 0), template_id))
    con.commit()
    return _template_view(_template_row(con, template_id))


@app.delete("/api/builds/admin/templates/{template_id}", status_code=204, dependencies=[Depends(owner)])
def delete_template(template_id: int) -> None:
    con = db(); _template_row(con, template_id)
    used = con.execute("SELECT 1 FROM build WHERE template_id = ? LIMIT 1", (template_id,)).fetchone()
    if used:
        con.execute("UPDATE build_template SET visible = 0 WHERE id = ?", (template_id,))      # builds stand on it
    else:
        con.execute("DELETE FROM build_template WHERE id = ?", (template_id,))
    con.commit()


class BuildIn(BaseModel):
    template_id: int
    name: str
    variant: str = ""
    run_id: int | None = None


@app.get("/api/builds", dependencies=[Depends(owner)])
def my_builds() -> list[dict]:
    con = db()
    out = []
    for b in con.execute("SELECT * FROM build ORDER BY updated_at DESC").fetchall():
        v = _build_view(con, b); v.pop("goals", None)
        p = v["progress"]
        v["progress"] = {"met": p["met"], "partly": p["partly"], "total": p["total"], "ratio": p["ratio"], "complete": p["complete"],
                         "categories": [{k: c[k] for k in ("id", "name", "met", "partly", "total", "ratio")} for c in p["categories"]]}
        out.append(v)
    return out


@app.post("/api/builds", status_code=201, dependencies=[Depends(owner)])
def create_build(body: BuildIn) -> dict:
    con = db(); t = _template_row(con, body.template_id)
    if not t["visible"]:
        raise HTTPException(404, "no such template")
    run_id = body.run_id if body.run_id and con.execute("SELECT 1 FROM run WHERE id = ?", (body.run_id,)).fetchone() else None
    name = body.name.strip()[:80]
    if not name:
        raise HTTPException(422, "a build needs a name")
    cur = con.execute("INSERT INTO build (template_id, run_id, name, variant, goals, updated_at) VALUES (?, ?, ?, ?, '{}', ?)",
                      (t["id"], run_id, name, body.variant.strip()[:80], _now().isoformat()))
    con.commit()
    return _build_view(con, _build_row(con, cur.lastrowid))


# ── the game data, and a build planned from it ───────────────────────────────
#
# The same database the site reads (shrutisguides.gamedata), pulled from it
# as one file so the tracker plans offline. The planner's routes mirror the
# site's /api/builds/plan exactly; the shared functions do the work.

def gamedata() -> GameData:
    return GameData(DATA / "gamedata.sqlite3")


def _loaded(game: str) -> GameData:
    d = gamedata()
    if not d.exists() or d.game(game) is None:
        raise HTTPException(404, "that game's data is not loaded — pull it from the site first")
    return d


@app.get("/api/gamedata/games")
def gamedata_games() -> list[dict]:
    return [{**g, "problems": len(g["problems"]), "planner": recipe_for(g["id"]) is not None} for g in gamedata().games()]


@app.post("/api/gamedata/pull", status_code=201, dependencies=[Depends(owner)])
def pull_gamedata() -> dict:
    """The site's current game database, whole, checked against its digest and swapped in atomically."""
    try:
        m = httpx.get(f"{SITE}/api/gamedata/manifest", timeout=20)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"could not reach {SITE}: {type(exc).__name__}")
    if m.status_code != 200:
        raise HTTPException(502, f"{SITE} answered {m.status_code}")
    manifest = m.json() if isinstance(m.json(), dict) else {}
    url = str(manifest.get("url") or "")
    if not url.startswith("/"):
        raise HTTPException(502, f"{SITE} published no game data")
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = DATA / ".gamedata.download"
    digest = hashlib.sha256()
    try:
        with httpx.stream("GET", f"{SITE}{url}", timeout=300, follow_redirects=True) as r:
            if r.status_code != 200:
                raise HTTPException(502, f"{SITE} answered {r.status_code} for the file")
            with open(tmp, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
                    digest.update(chunk)
    except httpx.HTTPError as exc:
        tmp.unlink(missing_ok=True)
        raise HTTPException(502, f"the download failed: {type(exc).__name__}")
    if manifest.get("digest") and not digest.hexdigest().startswith(str(manifest["digest"])):
        tmp.unlink(missing_ok=True)
        raise HTTPException(502, "the file did not match its digest")
    os.replace(tmp, DATA / "gamedata.sqlite3")
    return {"ok": True, "file": manifest.get("file", ""), "games": gamedata_games()}


@app.get("/api/gamedata/{game}")
def gamedata_game(game: str) -> dict:
    g = _loaded(game).game(game)
    return {**g, "problems": len(g["problems"]), "recipe": recipe_for(game)}


@app.get("/api/gamedata/{game}/recipe")
def gamedata_recipe(game: str) -> dict:
    _loaded(game)
    r = recipe_for(game)
    if r is None:
        raise HTTPException(404, "no planner for that game yet")
    return r


@app.get("/api/gamedata/{game}/search")
def gamedata_search(game: str, q: str = Query(min_length=1, max_length=80), kinds: str = "", class_id: str = "", limit: int = Query(40, ge=1, le=200)) -> list[dict]:
    wanted = [k for k in kinds.split(",") if k in KINDS]
    return _loaded(game).search(game, q, kinds=wanted or None, class_id=class_id or None, limit=limit)


@app.get("/api/gamedata/{game}/{kind}")
def gamedata_records(game: str, kind: str, sub: str = "", class_id: str = "", slot_id: str = "", group: str = "", tag: str = "", q: str = "",
                     ids: str = "", brief: bool = True, limit: int = Query(500, ge=1, le=5000), offset: int = Query(0, ge=0)) -> list[dict]:
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    return _loaded(game).list(game, kind, sub=[x for x in sub.split(",") if x] or None, class_id=class_id or None, slot_id=slot_id or None,
                              group=group or None, tag=tag or None, q=q or None, ids=[i for i in ids.split(",") if i] or None,
                              limit=limit, offset=offset, brief=brief)


@app.get("/api/gamedata/{game}/{kind}/groups")
def gamedata_groups(game: str, kind: str, class_id: str = "") -> list[dict]:
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    return _loaded(game).groups(game, kind, class_id=class_id or None)


@app.get("/api/gamedata/{game}/{kind}/{id}")
def gamedata_record(game: str, kind: str, id: str) -> dict:
    if kind not in KINDS:
        raise HTTPException(404, "no such kind")
    d = _loaded(game)
    r = d.get(game, kind, id)
    if r is None:
        raise HTTPException(404, "no such record")
    return {**r, "links": d.links(game, kind, id), "linked_from": d.links(game, kind, id, direction="in")}


class SheetIn(BaseModel):
    game: str
    plan: dict = {}


@app.post("/api/builds/sheet")
def plan_sheet(body: SheetIn) -> dict:
    """What a plan comes to, saved or not. Reads the game data and nothing about anybody."""
    d = gamedata()
    slug = builds.ident(body.game, "game")
    plan, problems = clean_plan({**body.plan, "game": slug}, d)
    if not plan:
        raise HTTPException(422, problems[0] if problems else "that plan cannot be read")
    return {"plan": plan, "problems": problems, "summary": plan_summary(plan, d), "sheet": compute_sheet(plan, d)}


class PlanIn(BaseModel):
    game: str
    name: str
    variant: str = ""
    run_id: int | None = None
    plan: dict = {}


class RePlanIn(BaseModel):
    plan: dict = {}


def _planned(raw_plan: dict, game_slug: str) -> tuple[dict, list, list[str]]:
    d = gamedata()
    plan, problems = clean_plan({**raw_plan, "game": game_slug}, d)
    if not plan:
        raise HTTPException(422, problems[0] if problems else "that plan cannot be read")
    cats = plan_to_categories(plan, d)
    if not cats:
        raise HTTPException(422, "the plan chooses nothing yet")
    return plan, cats, problems


@app.post("/api/builds/plan", status_code=201, dependencies=[Depends(owner)])
def create_planned_build(body: PlanIn) -> dict:
    """A build from a plan: no template, the game's data instead."""
    con = db()
    slug = builds.ident(body.game, "game")
    plan, cats, problems = _planned(body.plan, slug)
    pack = gamedata().game(slug) or {}
    name = body.name.strip()[:80]
    if not name:
        raise HTTPException(422, "a build needs a name")
    run_id = body.run_id if body.run_id and con.execute("SELECT 1 FROM run WHERE id = ?", (body.run_id,)).fetchone() else None
    variant = body.variant.strip()[:80] or plan_summary(plan, gamedata()).get("className", "")
    cur = con.execute("INSERT INTO build (template_id, run_id, name, variant, goals, updated_at, game_slug, game_name, plan, categories) "
                      "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (run_id, name, variant, json.dumps(plan_goals(cats)), _now().isoformat(), slug, str(pack.get("name") or body.game)[:80],
                       json.dumps(plan), json.dumps(cats)))
    con.commit()
    return {**_build_view(con, _build_row(con, cur.lastrowid), with_sheet=True), "problems": problems}


@app.put("/api/builds/{build_id}/plan", dependencies=[Depends(owner)])
def replan_build(build_id: int, body: RePlanIn) -> dict:
    """The plan changed: the categories are rewritten, and every goal whose id survives keeps its words and its state."""
    con = db(); b = _build_row(con, build_id)
    if b["template_id"] and not json.loads(b["plan"] or "{}"):
        raise HTTPException(409, "this build was made from a template, not a plan")
    if not b["game_slug"]:
        raise HTTPException(409, "this build has no game to plan against")
    plan, cats, problems = _planned(body.plan, b["game_slug"])
    goals = plan_goals(cats, json.loads(b["goals"] or "{}"))
    con.execute("UPDATE build SET plan = ?, categories = ?, goals = ?, updated_at = ? WHERE id = ?",
                (json.dumps(plan), json.dumps(cats), json.dumps(goals), _now().isoformat(), build_id))
    con.commit()
    return {**_build_view(con, _build_row(con, build_id), with_sheet=True), "problems": problems}


@app.get("/api/builds/{build_id}", dependencies=[Depends(owner)])
def one_build(build_id: int) -> dict:
    con = db()
    return _build_view(con, _build_row(con, build_id), with_sheet=True)


class BuildPatch(BaseModel):
    name: str | None = None
    variant: str | None = None
    run_id: int | None = None


@app.put("/api/builds/{build_id}", dependencies=[Depends(owner)])
def rename_build(build_id: int, body: BuildPatch) -> dict:
    con = db(); b = _build_row(con, build_id)
    name = (body.name.strip()[:80] or b["name"]) if body.name is not None else b["name"]
    variant = body.variant.strip()[:80] if body.variant is not None else b["variant"]
    run_id = b["run_id"]
    if body.run_id is not None:
        run_id = body.run_id if body.run_id and con.execute("SELECT 1 FROM run WHERE id = ?", (body.run_id,)).fetchone() else None
    con.execute("UPDATE build SET name = ?, variant = ?, run_id = ? WHERE id = ?", (name, variant, run_id, build_id)); con.commit()
    return _build_view(con, _build_row(con, build_id))


@app.put("/api/builds/{build_id}/goals/{item_id}", dependencies=[Depends(owner)])
def set_goal(build_id: int, item_id: str, body: dict) -> dict:
    con = db(); b = _build_row(con, build_id)
    if item_id not in builds.known_items(_categories_of(con, b)):
        raise HTTPException(404, "no such goal in this build")
    goals = builds.apply_goal(json.loads(b["goals"] or "{}"), item_id, body)
    con.execute("UPDATE build SET goals = ?, updated_at = ? WHERE id = ?", (json.dumps(goals), _now().isoformat(), build_id)); con.commit()
    return _build_view(con, _build_row(con, build_id))


@app.delete("/api/builds/{build_id}", dependencies=[Depends(owner)])
def delete_build(build_id: int) -> dict:
    con = db(); _build_row(con, build_id)
    con.execute("DELETE FROM overlay WHERE build_id = ?", (build_id,))
    con.execute("DELETE FROM build WHERE id = ?", (build_id,)); con.commit()
    return {"ok": True}


@app.get("/api/builds/{build_id}/overlays", dependencies=[Depends(owner)])
def build_tokens(build_id: int) -> list[dict]:
    con = db(); _build_row(con, build_id)
    return [{"id": o["id"], "kind": o["kind"], "label": o["label"], "theme": o["theme"], "motion": o["motion"], "lastSeen": o["last_seen"]}
            for o in con.execute("SELECT * FROM overlay WHERE build_id = ? ORDER BY id", (build_id,)).fetchall()]


class BuildTokenIn(BaseModel):
    theme: str = "almanac"
    motion: str = "reduced"
    label: str = ""


@app.post("/api/builds/{build_id}/overlays", status_code=201, dependencies=[Depends(owner)])
def mint_build_token(build_id: int, body: BuildTokenIn) -> dict:
    """The build as a browser source; the token is returned once."""
    con = db(); b = _build_row(con, build_id)
    token = secrets.token_urlsafe(24)
    cur = con.execute("INSERT INTO overlay (token, kind, build_id, theme, motion, label) VALUES (?, 'build', ?, ?, ?, ?)",
                      (token, build_id, body.theme if body.theme in progress.THEMES else "almanac",
                       body.motion if body.motion in progress.MOTIONS else "reduced", body.label.strip()[:80] or b["name"]))
    con.commit()
    return {"id": cur.lastrowid, "token": token, "kind": "build"}


class BuildRebindIn(BaseModel):
    build_id: int


@app.put("/api/builds/{build_id}/overlays/{token_id}", dependencies=[Depends(owner)])
def rebind_build_token(build_id: int, token_id: int, body: BuildRebindIn) -> dict:
    """Point a build overlay at another build; the stream switches without a new source in OBS."""
    con = db(); _build_row(con, build_id); _build_row(con, body.build_id)
    if con.execute("SELECT 1 FROM overlay WHERE id = ? AND build_id = ?", (token_id, build_id)).fetchone() is None:
        raise HTTPException(404, "no such overlay")
    con.execute("UPDATE overlay SET build_id = ? WHERE id = ?", (body.build_id, token_id)); con.commit()
    return {"ok": True, "id": token_id, "buildId": body.build_id}


@app.delete("/api/builds/{build_id}/overlays/{token_id}", status_code=204, dependencies=[Depends(owner)])
def revoke_build_token(build_id: int, token_id: int) -> None:
    con = db(); con.execute("DELETE FROM overlay WHERE id = ? AND build_id = ?", (token_id, build_id)); con.commit()


@app.get("/api/runs/{run_id}/overlays", dependencies=[Depends(owner)])
def list_tokens(run_id: int) -> list[dict]:
    con = db(); _run_row(con, run_id)
    return [{"id": o["id"], "kind": o["kind"], "label": o["label"], "theme": o["theme"], "motion": o["motion"],
             "routineId": o["routine_id"], "lastSeen": o["last_seen"], "layout": json.loads(o["layout"] or "[]")}
            for o in con.execute("SELECT * FROM overlay WHERE run_id = ? ORDER BY id", (run_id,)).fetchall()]


@app.post("/api/runs/{run_id}/overlays", status_code=201, dependencies=[Depends(owner)])
def mint(run_id: int, body: TokenIn) -> dict:
    con = db(); _run_row(con, run_id)
    if body.kind not in progress.GUIDE_KINDS:
        raise HTTPException(422, "kind is guide-now, guide-sigil, guide-path or guide-routine")
    token = secrets.token_urlsafe(24)
    cur = con.execute("INSERT INTO overlay (token, kind, run_id, routine_id, theme, motion, label, layout) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (token, body.kind, run_id, body.routine_id.strip()[:80], body.theme if body.theme in progress.THEMES else "almanac",
                       body.motion if body.motion in progress.MOTIONS else "reduced", body.label.strip()[:80],
                       json.dumps(progress.clean_layout(body.layout))))
    con.commit()
    return {"id": cur.lastrowid, "token": token, "kind": body.kind}


@app.delete("/api/runs/{run_id}/overlays/{token_id}", status_code=204, dependencies=[Depends(owner)])
def revoke(run_id: int, token_id: int) -> None:
    con = db(); con.execute("DELETE FROM overlay WHERE id = ? AND run_id = ?", (token_id, run_id)); con.commit()


@app.get("/api/overlay/guide")
def overlay_guide(t: str, v: str = "") -> dict:
    """
    The run as this token's element draws it. Public by token; a gone run is
    an empty frame. A source sends the version it shows as `v`; when nothing
    has changed the answer says so and computes nothing — the same contract
    as the site's, so a page works against either.
    """
    con = db()
    o = con.execute("SELECT * FROM overlay WHERE token = ?", (t,)).fetchone()
    if o is None:
        raise HTTPException(404, "no such overlay")
    # Seen-at is written at most once a minute; a source polls every two seconds.
    seen = o["last_seen"] or ""
    if not seen or (_now() - datetime.fromisoformat(seen)).total_seconds() > 60:
        con.execute("UPDATE overlay SET last_seen = ? WHERE id = ?", (_now().isoformat(), o["id"])); con.commit()
    base = {"kind": o["kind"], "theme": o["theme"], "motion": o["motion"], "run": None, "element": None, "version": ""}
    if o["kind"] == "build":
        b = con.execute("SELECT * FROM build WHERE id = ?", (o["build_id"],)).fetchone()
        if b is None:
            return base
        view = _build_view(con, b)
        base["version"] = f"{b['updated_at']}:{view['progress']['met']}"
        if v and v.replace(" ", "+") == base["version"]:
            base["unchanged"] = True
            return base
        base["element"] = _build_element(view)
        base["run"] = {"name": b["name"], "guide": b["variant"], "game": view["template"]["game"]["name"]}
        return base
    row = con.execute("SELECT * FROM run WHERE id = ?", (o["run_id"],)).fetchone()
    if row is None:
        return base
    layout = progress.clean_layout(json.loads(o["layout"] or "[]")) if o["kind"] == "guide-layout" else []
    version = row["updated_at"]
    if layout:
        ids = [int(e["build_id"]) for e in layout if e["kind"] == "build" and e.get("build_id")]
        if ids:
            stamps = con.execute(f"SELECT id, updated_at FROM build WHERE id IN ({','.join('?' * len(ids))})", ids).fetchall()
            version += ":b" + ",".join(f"{r['id']}@{r['updated_at']}" for r in stamps)
    base["version"] = version
    if v and v.replace(" ", "+") == version:
        base["unchanged"] = True
        return base
    g = _guide_row(con, row["guide_id"]); doc = json.loads(g["body"]); stored = _stored(row)
    base["run"] = {"name": stored.get("name", ""), "guide": g["title"], "game": g["game_name"]}
    if o["kind"] == "guide-layout":
        elements = progress.layout_elements(layout, stored, doc)
        for e in elements:
            if e["kind"] == "build" and e.get("build_id"):
                b = con.execute("SELECT * FROM build WHERE id = ?", (int(e["build_id"]),)).fetchone()
                e["element"] = _build_element(_build_view(con, b)) if b is not None else {}
        base["elements"] = elements
    else:
        base["element"] = progress.element(o["kind"], stored, doc, o["routine_id"])
    return base


@app.get("/overlay/{kind}")
def overlay_page(kind: str):
    """The browser sources, as plain files: no build step, cache-friendly."""
    if kind not in progress.GUIDE_KINDS and kind != "build":
        raise HTTPException(404, "no such overlay")
    return FileResponse(STATIC / f"{kind}.html", media_type="text/html")


@app.get("/overlay-elements.js")
def overlay_js():
    return FileResponse(STATIC / "overlay-elements.js", media_type="text/javascript")


@app.get("/overlay-guides.css")
def overlay_css():
    return FileResponse(STATIC / "overlay-guides.css", media_type="text/css")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (STATIC / "index.html").read_text(encoding="utf-8")
