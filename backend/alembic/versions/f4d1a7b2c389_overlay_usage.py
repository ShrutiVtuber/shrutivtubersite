"""Minutes an overlay was on air, per day

Revision ID: f4d1a7b2c389
Revises: e3c9d5a1f267
"""
from alembic import op
import sqlalchemy as sa

revision = "f4d1a7b2c389"
down_revision = "e3c9d5a1f267"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "overlay_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("overlay_token.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_overlay_usage_token_id", "overlay_usage", ["token_id"])
    op.create_index("ix_overlay_usage_day", "overlay_usage", ["day"])
    op.create_unique_constraint("uq_overlay_usage_day", "overlay_usage", ["token_id", "day"])


def downgrade() -> None:
    op.drop_table("overlay_usage")
