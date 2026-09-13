"""Overlay hosting: a kind of tier, and a standing arrangement per account

Revision ID: g5e2b8c3d410
Revises: f4d1a7b2c389
"""
from alembic import op
import sqlalchemy as sa

revision = "g5e2b8c3d410"
down_revision = "f4d1a7b2c389"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tier", sa.Column("kind", sa.String(), nullable=False, server_default="support"))
    op.create_index("ix_tier_kind", "tier", ["kind"])
    op.create_table(
        "hosting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("email", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_customer_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_subscription_id", sa.String(), nullable=False, server_default=""),
        sa.Column("status", sa.String(), nullable=False, server_default=""),
        sa.Column("tier", sa.String(), nullable=False, server_default=""),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    for col in ("user_id", "email", "stripe_customer_id", "stripe_subscription_id"):
        op.create_index(f"ix_hosting_{col}", "hosting", [col])


def downgrade() -> None:
    op.drop_table("hosting")
    op.drop_index("ix_tier_kind", table_name="tier")
    op.drop_column("tier", "kind")
