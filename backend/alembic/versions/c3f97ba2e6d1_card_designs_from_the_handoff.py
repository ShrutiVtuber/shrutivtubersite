"""The three card designs from the design pass, and a line to describe each.

Revision ID: c3f97ba2e6d1
Revises: b2e58c14a7d9

The two shipped designs were a first pass — "Paper" and "Night", made to prove
the table worked. The design handoff replaces them with three that were drawn
at true 1200x630 and judged at the size the card actually travels.

Colour roles in the handoff are named for what they draw rather than for a
palette slot, and they map onto the existing columns exactly:

    verdict -> ink        names -> soft        count -> accent
    marker  -> faint      note  -> faint (identical in all three designs)

`line` takes the note colour: the handoff draws the two hairlines as the note
colour at 38% alpha, which is one colour, not two.

**The keys stay `light` and `dark`.** The handoff calls them dawn and dusk, and
those are now their names — but `comparison.card_theme` stores the key against
every comparison already made, and renaming would silently orphan them onto the
default. A key is plumbing; a name is what she sees.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c3f97ba2e6d1"
down_revision = "b2e58c14a7d9"
branch_labels = None
depends_on = None


DESIGNS = [
    dict(
        key="light", name="Dawn", position=10,
        background="#F8F6F3", ink="#26304A", soft="#4A5470",
        accent="#A85A76", faint="#6E7890", line="#6E7890",
        scrim=False, backdrop_asset="",
        blurb="Paper and ink. Holds up on a white timeline and a black one.",
    ),
    dict(
        key="dark", name="Dusk", position=20,
        background="#121829", ink="#E9E6F0", soft="#B3B9D2",
        accent="#E0A4BC", faint="#8B93AF", line="#8B93AF",
        scrim=False, backdrop_asset="",
        blurb="The other juncture of the same sky — not an inversion of the first.",
    ),
    dict(
        key="rose-horizon", name="Rose horizon", position=30,
        background="#0B1322", ink="#FBF7F8", soft="#F2E7EC",
        accent="#F0C3D2", faint="#D6C6D0", line="#D6C6D0",
        scrim=True, backdrop_asset="card-backdrop-horizon.png",
        blurb="A painted sky behind a scrim, so busy artwork can still carry type.",
    ),
]


def upgrade() -> None:
    op.add_column("card_design", sa.Column("blurb", sa.String(), nullable=False, server_default=""))
    # A backdrop that SHIPS with the application rather than being uploaded.
    # `media_id` still covers anything she adds herself; this covers the one
    # that is part of the design and has to exist on a fresh install.
    op.add_column("card_design",
                  sa.Column("backdrop_asset", sa.String(), nullable=False, server_default=""))

    cd = sa.table(
        "card_design",
        sa.column("key", sa.String), sa.column("name", sa.String),
        sa.column("background", sa.String), sa.column("ink", sa.String),
        sa.column("soft", sa.String), sa.column("faint", sa.String),
        sa.column("line", sa.String), sa.column("accent", sa.String),
        sa.column("scrim", sa.Boolean), sa.column("blurb", sa.String),
        sa.column("backdrop_asset", sa.String), sa.column("position", sa.Integer),
        sa.column("visible", sa.Boolean),
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()
    existing = {r[0] for r in conn.execute(sa.select(cd.c.key))}
    for row in DESIGNS:
        values = dict(row, visible=True)
        key = values.pop("key")
        if key in existing:
            conn.execute(cd.update().where(cd.c.key == key).values(**values))
        else:
            conn.execute(cd.insert().values(
                key=key, created_at=sa.func.now(), updated_at=sa.func.now(), **values))


def downgrade() -> None:
    op.drop_column("card_design", "backdrop_asset")
    op.drop_column("card_design", "blurb")
