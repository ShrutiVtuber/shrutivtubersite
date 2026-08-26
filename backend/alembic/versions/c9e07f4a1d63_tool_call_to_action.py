"""One invitation at the foot of every free instrument.

Revision ID: c9e07f4a1d63
Revises: b5d24e70f931

The instruments are the part of this site a stranger reaches first, and they
ask for nothing. That is what makes an invitation credible — so there is
exactly one, it sits at the FOOT of the tool after it has done its job, and
nothing above it is withheld.

The copy is a row so she can rewrite it everywhere at once, or untick it and
have no invitation at all.

**It promises only what exists.** An account keeps charts and collab groups
today; it does not remember your place or your reckoning, tempting as that line
is — `user.timezone` is stored and no instrument reads it. Claiming otherwise
on a page whose whole argument is that it shows its working would be the
expensive kind of small lie.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c9e07f4a1d63"
down_revision = "b5d24e70f931"
branch_labels = None
depends_on = None

BODY = (
    "Everything here is free and stays free — no account, no advertising, "
    "nothing kept about you.\n\n"
    "An account is for the things worth keeping: a chart you cast stays yours "
    "behind your own link, a collab plan stops living in a browser tab, and "
    "the monthly letter is where new instruments get announced before "
    "anywhere else."
)


def upgrade() -> None:
    t = sa.table(
        "section",
        sa.column("page", sa.String), sa.column("key", sa.String),
        sa.column("kind", sa.String), sa.column("position", sa.Integer),
        sa.column("visible", sa.Boolean), sa.column("eyebrow", sa.String),
        sa.column("title", sa.String), sa.column("body_md", sa.String),
        sa.column("link_url", sa.String), sa.column("link_label", sa.String),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()
    already = conn.execute(
        sa.select(t.c.key).where(t.c.page == "tools-cta")
    ).first()
    if already:
        return
    conn.execute(t.insert().values(
        page="tools-cta", key="signup", kind="prose", position=0,
        # Visible from the start, unlike most sections: an invitation that
        # ships switched off is one nobody remembers to switch on.
        visible=True,
        eyebrow="Free, and staying that way",
        title="Keep what you make here",
        body_md=BODY,
        link_url="/signup", link_label="Make an account",
        created_at=sa.func.now(), updated_at=sa.func.now(),
    ))


def downgrade() -> None:
    t = sa.table("section", sa.column("page", sa.String))
    op.get_bind().execute(t.delete().where(t.c.page == "tools-cta"))
