"""Discount codes

A coupon is the discount and a promotion code is the word people type. Two
things at Stripe, one row here, because she should think about one thing.

Their terms are fixed at creation — Stripe's rule, and the right one: a
discount that could be altered afterwards would change what somebody was
already promised. So a code is created and then it is either on or off.

Revision ID: a17c4e8b3d92
Revises: f5a83e2c7b91
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a17c4e8b3d92"
down_revision: Union[str, None] = "f5a83e2c7b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "discount",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("percent_off", sa.Float(), nullable=True),
        sa.Column("amount_off_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("applies_to", sa.String(), nullable=False, server_default="everything"),
        sa.Column("duration", sa.String(), nullable=False, server_default="once"),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("stripe_coupon_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_promotion_code_id", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_discount_code", "discount", ["code"])


def downgrade() -> None:
    op.drop_table("discount")
