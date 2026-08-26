"""Two kept charts read against each other, and the reading somebody wrote

Both sides are references rather than copies: deleting a chart must take its
birth data out of every comparison built on it, not leave a copy behind.

Revision ID: c5e83a71d92f
Revises: b8d21f5c9e40
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c5e83a71d92f"
down_revision: Union[str, None] = "b8d21f5c9e40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comparison",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_token", sa.String(), nullable=False),
        sa.Column("share_token", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        # ondelete CASCADE: a chart being forgotten must take the comparisons
        # built on it with it. Anything else keeps a pointer to a moment
        # somebody asked to have deleted.
        sa.Column("left_id", sa.Integer(),
                  sa.ForeignKey("saved_chart.id", ondelete="CASCADE"), nullable=False),
        sa.Column("right_id", sa.Integer(),
                  sa.ForeignKey("saved_chart.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("reading_md", sa.String(), nullable=False, server_default=""),
        sa.Column("tradition", sa.String(), nullable=False, server_default="hellenistic"),
        sa.Column("orb", sa.Float(), nullable=False, server_default="6"),
        sa.Column("shared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_comparison_owner_token", "comparison", ["owner_token"], unique=True)
    op.create_index("ix_comparison_share_token", "comparison", ["share_token"], unique=True)
    op.create_index("ix_comparison_user_id", "comparison", ["user_id"])


def downgrade() -> None:
    op.drop_table("comparison")
