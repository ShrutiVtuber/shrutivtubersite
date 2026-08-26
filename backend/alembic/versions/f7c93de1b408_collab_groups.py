"""Saved groups for the collab planner — the thing an account buys.

Revision ID: f7c93de1b408
Revises: e6a2d38f45b7

The planner needs no backend: the plan is the URL, which is what makes it
shareable and what makes it useful to somebody who arrived from a link. This is
the one part a URL cannot do — remembering a group across devices — which makes
it the honest thing to attach to an account. Signing in removes a chore rather
than unlocking a feature.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f7c93de1b408"
down_revision = "e6a2d38f45b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collab_group",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("participants", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_collab_group_user_id", "collab_group", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_collab_group_user_id", table_name="collab_group")
    op.drop_table("collab_group")
