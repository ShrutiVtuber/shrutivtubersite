"""Two projects worth naming before they are built.

Revision ID: e2c81ab4f057
Revises: d1a68f30b57e

The Discord bot and the OBS overlay set. Both are hers, both are separate
projects, and both carry decisions that are easy to lose if they live only in a
conversation — so they go in the list she reads, with the reasoning attached.

The bot's two constraints in particular are the kind that get quietly reversed
six months later by somebody who does not know why they were made.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e2c81ab4f057"
down_revision = "d1a68f30b57e"
branch_labels = None
depends_on = None


ROWS = [
    dict(
        title="An OBS overlay toolset, driven from the site",
        summary="Donation goals, alerts and counters, rendered as browser sources and configured here.",
        effort="a project, not a task", owner="me", position=40,
        why="Her own words: *\"an obs overlay etc set of tools that we can query from the site to have our own donation goals, etc etc that goes through stripe.\"*\\n\\nThe shape that makes this worth building rather than buying: the site already has Stripe, accounts, media and an admin. An overlay is a URL that OBS opens as a browser source, so the hard parts — payments, storage, configuration, auth — are all things this stack already does. What is new is a real-time channel to the browser source and a set of small, well-drawn overlay pages.\\n\\nUse it herself first, the same way as the commission tracker. **This is a separate feature from the Discord bot** and should not be folded into it, though they would share the same event stream.",
    ),
    dict(
        title="The Discord bot — a bot other VTubers can add to their own servers",
        summary="One subscription replacing several, and she uses it herself.",
        effort="a project", owner="me", position=5,
        why="Her framing, which is the whole business case: *\"VTubers have to pay a lot of different services to get what they actually need. If our discord bot could handle it for them in one place with one payment that would be amazing — and I would use it as well which would be helpful to reduce my vtuber costs.\"*\\n\\nTwo decisions already made and not to be revisited lightly:\\n\\n1. **Read-only against the site.** It must never write. A bot with write access means Discord can create things on the site, and the blast radius of a compromised bot token becomes the whole site rather than one server.\\n2. **Automated messages get labelled.** Flagged by the German MStV research — probably not her jurisdiction, but the principle is cheap to honour and future-proofs against the direction every jurisdiction is moving.",
    ),
]


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
    existing = {r[0] for r in conn.execute(sa.select(t.c.title))}
    for row in ROWS:
        if row["title"] in existing:
            continue
        conn.execute(t.insert().values(
            kind="build", done=False, visible=True,
            created_at=sa.func.now(), updated_at=sa.func.now(), **row))


def downgrade() -> None:
    t = sa.table("growth_item", sa.column("title", sa.String))
    conn = op.get_bind()
    for row in ROWS:
        conn.execute(t.delete().where(t.c.title == row["title"]))
