"""Replacing the bots she pays for, and the ones she merely uses.

Revision ID: c07f2a91d4b6
Revises: e2c81ab4f057

Her four: Pingcord, Carl-bot, YAGPDB.xyz and AmariBot. They split cleanly along
the privileged-intent line, and that line — not the feature list — decides the
order.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c07f2a91d4b6"
down_revision = "e2c81ab4f057"
branch_labels = None
depends_on = None


ROWS = [
    dict(
        kind="build", position=8, owner="me", effort="a few days",
        title="Replace Pingcord — stream and social alerts",
        summary="The one she actually pays for, and the easiest to replace.",
        why="Pingcord announces going live and posts new social activity. It is "
            "the only bot in her server she pays for, and it is also the one "
            "that needs **no privileged intent at all** — announcements are "
            "outbound, so nothing has to watch messages or members.\n\n"
            "Most of it already exists. The website has a live-watcher that "
            "fires on the offline-to-live *transition*, persists the last "
            "state, says nothing on the first pass after a restart, and treats "
            "a platform error as *unknown* rather than offline. That logic was "
            "the hard part and it is written, tested and running.\n\n"
            "What is left is per-guild configuration — which channel, which "
            "platforms, what the message says — and posting it. Doing this "
            "first also means the bot announces her own streams, which is the "
            "feature that most directly serves the site.",
    ),
    dict(
        kind="build", position=60, owner="me", effort="a project, and an application to Discord",
        title="Own the stack: replace Carl-bot, YAGPDB and AmariBot",
        summary="Wanted, not urgent — and it means asking Discord for the intents we avoided.",
        why="Agreed 26 August 2026: she wants to own her stack, and this waits "
            "rather than being dropped.\n\n"
            "It is a bigger job than the feature list suggests, because these "
            "three sit on the far side of the privileged-intent line:\n\n"
            "- **Reaction roles** — free. Done as buttons or slash commands "
            "rather than by watching reactions on old messages, no intent is "
            "needed at all.\n"
            "- **Welcomes, goodbyes, join logging** — needs the **Guild "
            "Members** intent. Review at 10,000 users.\n"
            "- **Automod, keyword filters, starboard, XP from chatting** — "
            "needs **Message Content**, the most scrutinised intent Discord "
            "grants. Asking for it is a commitment, not a checkbox.\n\n"
            "So this is a deliberate decision to walk back into the intent "
            "path we deliberately walked out of. Worth doing — but as its own "
            "decision, with an application written for it, and not as a side "
            "effect of adding features one at a time.\n\n"
            "**Check what is actually being paid first.** Carl-bot and YAGPDB "
            "are free for most of what they do. If the answer is nothing, this "
            "is about ownership rather than cost, which is a fine reason and a "
            "different priority.",
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
            done=False, visible=True,
            created_at=sa.func.now(), updated_at=sa.func.now(), **row))


def downgrade() -> None:
    t = sa.table("growth_item", sa.column("title", sa.String))
    conn = op.get_bind()
    for row in ROWS:
        conn.execute(t.delete().where(t.c.title == row["title"]))
