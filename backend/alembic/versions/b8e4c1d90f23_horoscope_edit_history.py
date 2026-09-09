"""Horoscope edit history

She asked to be able to correct a published reading — a spelling, a wrong word —
and for the correction to be "subtly marked so people can see and track the edit
history". A reading nobody may fix grows typos; a reading that can be silently
rewritten is not a record of what she said that week.

Revision identifiers, used by Alembic.
revision = "b8e4c1d90f23"
down_revision = "a7d3f18c2e40"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b8e4c1d90f23"
down_revision = "a7d3f18c2e40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "horoscope",
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "horoscope_revision",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("horoscope_id", sa.Integer(),
                  sa.ForeignKey("horoscope.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        # ⚠ The words BEFORE the edit that replaced them. The current words stay
        # on the horoscope row, so reading one is never a join.
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("replaced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("horoscope_revision")
    op.drop_column("horoscope", "edited_at")
