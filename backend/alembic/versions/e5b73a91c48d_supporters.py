"""Supporters

Stripe is the ledger. This table holds the minimum needed to answer, without a
round trip on every page load, whether someone has an active subscription and
which Stripe customer they are. `user_id` is nullable because a one-off gift
needs no account, and requiring one to give money would lose most of the gifts.

Revision ID: e5b73a91c48d
Revises: d3f16c8b52a4
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5b73a91c48d"
down_revision: Union[str, None] = "d3f16c8b52a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "supporter",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("email", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_customer_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_subscription_id", sa.String(), nullable=False, server_default=""),
        sa.Column("status", sa.String(), nullable=False, server_default=""),
        sa.Column("tier", sa.String(), nullable=False, server_default=""),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_supporter_user_id", "supporter", ["user_id"])
    op.create_index("ix_supporter_email", "supporter", ["email"])
    op.create_index("ix_supporter_customer", "supporter", ["stripe_customer_id"])
    op.create_index("ix_supporter_subscription", "supporter", ["stripe_subscription_id"])


def downgrade() -> None:
    op.drop_table("supporter")
