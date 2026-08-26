"""Mark what has shipped, and hand back the part that is hers.

Revision ID: d8b3c05e7f21
Revises: c07f2a91d4b6

A list that does not move is a list nobody reads. Three build rows are done;
the Pingcord one hands over a step that only she can take, because the build
being finished is not the same as the subscription being cancelled.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d8b3c05e7f21"
down_revision = "c07f2a91d4b6"
branch_labels = None
depends_on = None

DONE = [
    "A collab timezone planner",
    "A canonical \"these are my real stores\" page",
    "Replace Pingcord — stream and social alerts",
]

HANDOVER = dict(
    kind="do", position=7, owner="you", effort="a week of doing nothing",
    title="Run vcordbot beside Pingcord for a week, then cancel",
    summary="The parallel week is the step people skip.",
    why="vcordbot announces streams now. That is not the same as it being safe "
        "to cancel Pingcord.\n\n"
        "Set it up — `/announce here`, then `/announce watch` — and leave "
        "Pingcord running. When your next stream fires **both**, you know. A "
        "gap found while the old one is still there is an inconvenience; a gap "
        "found afterwards is a silent server on the day it mattered.\n\n"
        "One thing to expect: a stream already running when you add a watch is "
        "**not** announced. The bot has nothing to compare against, and "
        "announcing would mean shouting about something six hours old every "
        "time it restarted. So test it across a real going-live, not by "
        "starting the bot mid-stream and wondering why it is quiet.",
)


def upgrade() -> None:
    t = sa.table(
        "growth_item",
        sa.column("kind", sa.String), sa.column("title", sa.String),
        sa.column("summary", sa.String), sa.column("why", sa.Text),
        sa.column("effort", sa.String), sa.column("owner", sa.String),
        sa.column("position", sa.Integer), sa.column("visible", sa.Boolean),
        sa.column("done", sa.Boolean),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()
    for title in DONE:
        conn.execute(t.update().where(t.c.title == title)
                     .values(done=True, updated_at=sa.func.now()))

    existing = {r[0] for r in conn.execute(sa.select(t.c.title))}
    if HANDOVER["title"] not in existing:
        conn.execute(t.insert().values(
            done=False, visible=True,
            created_at=sa.func.now(), updated_at=sa.func.now(), **HANDOVER))


def downgrade() -> None:
    t = sa.table("growth_item", sa.column("title", sa.String), sa.column("done", sa.Boolean))
    conn = op.get_bind()
    for title in DONE:
        conn.execute(t.update().where(t.c.title == title).values(done=False))
    conn.execute(t.delete().where(t.c.title == HANDOVER["title"]))
