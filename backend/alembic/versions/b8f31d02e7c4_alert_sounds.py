"""Her own sounds, one per kind of alert.

Revision ID: b8f31d02e7c4
Revises: a4e7d1c68b03

Per kind rather than a single "sounds on" switch, because the useful version of
this is a different noise for a gift than for a follow.

Nothing is seeded. A kind with no row is silent, deliberately: a default sound
she did not choose would play on her stream without her having heard it first.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b8f31d02e7c4"
down_revision = "a4e7d1c68b03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alert_sound",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False, server_default=""),
        sa.Column("gain_db", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    # One sound per kind. Unique rather than a first-match-wins query, so a
    # double submit cannot leave two rows and a coin toss over which plays.
    op.create_index("ix_alert_sound_kind", "alert_sound", ["kind"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_alert_sound_kind", table_name="alert_sound")
    op.drop_table("alert_sound")
