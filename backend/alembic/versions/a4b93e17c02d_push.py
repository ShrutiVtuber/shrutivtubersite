"""Browsers that asked to be told

No keys are stored: the push carries no payload and the service worker asks
this site what the notice says. See shruti/core/push.py.

Revision ID: a4b93e17c02d
Revises: f3c72d9a1e58
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a4b93e17c02d"
down_revision: Union[str, None] = "f3c72d9a1e58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "push_subscription",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("wants_live", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_writing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_push_subscription_endpoint", "push_subscription", ["endpoint"], unique=True)
    op.create_index("ix_push_subscription_user_id", "push_subscription", ["user_id"])


def downgrade() -> None:
    op.drop_table("push_subscription")
