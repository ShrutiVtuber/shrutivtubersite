"""Runs: one person's progress through one guide

Progress is keyed by step id in JSON columns, so a new version of the guide
never deletes any of it. Only what a person SET is stored; locked, available
and current are computed by the shared engine on every read.

Revision ID: f5b2c8d1a734
Revises: e3a1b5c7d902
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f5b2c8d1a734"
down_revision = "e3a1b5c7d902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guide_run",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guide_id", sa.Integer(), sa.ForeignKey("guide.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("variant", sa.String(), nullable=False, server_default=""),
        sa.Column("checkin", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("steps", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("routines", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("tracks", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("later", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("link_overrides", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("last_done", sa.String(), nullable=False, server_default=""),
        sa.Column("last_done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_guide_run_guide_id", "guide_run", ["guide_id"])
    op.create_index("ix_guide_run_user_id", "guide_run", ["user_id"])


def downgrade() -> None:
    op.drop_table("guide_run")
