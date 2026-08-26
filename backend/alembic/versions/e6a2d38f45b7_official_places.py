"""Places that are genuinely hers, so the fakes can be told apart.

Revision ID: e6a2d38f45b7
Revises: d4b16ce8a920

Seeded empty on purpose. Every row here is a claim that something is
authentically hers, and a migration is not in a position to make that claim on
her behalf — a seeded row pointing at a URL she has not confirmed would be the
exact failure this table exists to prevent.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e6a2d38f45b7"
down_revision = "d4b16ce8a920"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "official_place",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("kind", sa.String(), nullable=False, server_default="other"),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_official_place_kind", "official_place", ["kind"])


def downgrade() -> None:
    op.drop_index("ix_official_place_kind", table_name="official_place")
    op.drop_table("official_place")
