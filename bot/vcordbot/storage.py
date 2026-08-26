# SPDX-License-Identifier: AGPL-3.0-only
"""
What each server has asked for.

SQLite in the bot's own volume rather than a database beside the website's.
The plan asks that the bot have no route to site data even if it is
compromised, and a separate file on a separate volume is a stronger version of
that than a separate schema in a shared server.

The workload suits it: a handful of reads per poll, a write when a stream
starts. If that ever stops being true it is a small migration, and it will be
obvious long before it is urgent.
"""
from __future__ import annotations

import asyncio
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DB = Path("/data/vcordbot.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS guild (
    guild_id       TEXT PRIMARY KEY,
    channel_id     TEXT NOT NULL DEFAULT '',
    mention_role   TEXT NOT NULL DEFAULT '',
    template       TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS watch (
    id             INTEGER PRIMARY KEY,
    guild_id       TEXT NOT NULL,
    platform       TEXT NOT NULL,          -- twitch | youtube
    handle         TEXT NOT NULL,
    -- 'live' | 'offline' | '' — empty means never successfully checked, which
    -- is NOT the same as offline and must never produce an announcement.
    last_state     TEXT NOT NULL DEFAULT '',
    last_announced TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (guild_id, platform, handle)
);
"""


@dataclass
class Watch:
    id: int
    guild_id: str
    platform: str
    handle: str
    last_state: str
    last_announced: str


@dataclass
class Guild:
    guild_id: str
    channel_id: str
    mention_role: str
    template: str


@contextmanager
def _conn(path: Path | None = None):
    db = path or DB
    db.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(db, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        # WAL so a poll reading does not block a command writing.
        c.execute("PRAGMA journal_mode=WAL")
        yield c
        c.commit()
    finally:
        c.close()


def setup(path: Path | None = None) -> None:
    with _conn(path) as c:
        c.executescript(SCHEMA)


# ── guilds ─────────────────────────────────────────────────────────────────

def set_channel(guild_id: str, channel_id: str, path: Path | None = None) -> None:
    with _conn(path) as c:
        c.execute(
            "INSERT INTO guild (guild_id, channel_id) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET channel_id=excluded.channel_id, "
            "updated_at=datetime('now')",
            (guild_id, channel_id))


def set_template(guild_id: str, template: str, path: Path | None = None) -> None:
    with _conn(path) as c:
        c.execute(
            "INSERT INTO guild (guild_id, template) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET template=excluded.template, "
            "updated_at=datetime('now')",
            (guild_id, template))


def set_mention(guild_id: str, role_id: str, path: Path | None = None) -> None:
    with _conn(path) as c:
        c.execute(
            "INSERT INTO guild (guild_id, mention_role) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET mention_role=excluded.mention_role, "
            "updated_at=datetime('now')",
            (guild_id, role_id))


def guild(guild_id: str, path: Path | None = None) -> Guild | None:
    with _conn(path) as c:
        r = c.execute("SELECT * FROM guild WHERE guild_id=?", (guild_id,)).fetchone()
    return Guild(r["guild_id"], r["channel_id"], r["mention_role"], r["template"]) if r else None


# ── watches ────────────────────────────────────────────────────────────────

def add_watch(guild_id: str, platform: str, handle: str, path: Path | None = None) -> bool:
    """True if it was added, False if it was already there."""
    with _conn(path) as c:
        try:
            c.execute("INSERT INTO watch (guild_id, platform, handle) VALUES (?, ?, ?)",
                      (guild_id, platform, handle.strip()))
            return True
        except sqlite3.IntegrityError:
            return False


def remove_watch(guild_id: str, platform: str, handle: str, path: Path | None = None) -> bool:
    with _conn(path) as c:
        cur = c.execute("DELETE FROM watch WHERE guild_id=? AND platform=? AND handle=?",
                        (guild_id, platform, handle.strip()))
        return cur.rowcount > 0


def watches(guild_id: str | None = None, path: Path | None = None) -> list[Watch]:
    q = "SELECT * FROM watch"
    args: tuple = ()
    if guild_id:
        q += " WHERE guild_id=?"
        args = (guild_id,)
    with _conn(path) as c:
        rows = c.execute(q + " ORDER BY id", args).fetchall()
    return [Watch(r["id"], r["guild_id"], r["platform"], r["handle"],
                  r["last_state"], r["last_announced"]) for r in rows]


def record_state(watch_id: int, state: str, announced: bool = False,
                 path: Path | None = None) -> None:
    with _conn(path) as c:
        if announced:
            c.execute("UPDATE watch SET last_state=?, last_announced=datetime('now') "
                      "WHERE id=?", (state, watch_id))
        else:
            c.execute("UPDATE watch SET last_state=? WHERE id=?", (state, watch_id))


async def to_thread(fn, *args, **kwargs):
    """
    SQLite is synchronous. Run it off the loop so a slow disk cannot stall the
    interaction that has three seconds to answer.
    """
    return await asyncio.to_thread(fn, *args, **kwargs)
