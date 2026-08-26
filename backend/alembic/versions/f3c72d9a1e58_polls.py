"""Polls, with answers fixed at creation

The answers cannot be edited once a poll exists: changing a label after people
have voted silently changes what their vote meant.

`voter` is an account id or the visit counter's daily hash — never an address.

Revision ID: f3c72d9a1e58
Revises: e2f81b6c4a37
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3c72d9a1e58"
down_revision: Union[str, None] = "e2f81b6c4a37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "poll",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False, server_default=""),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("closes_at", sa.String(), nullable=False, server_default=""),
        sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_poll_slug", "poll", ["slug"], unique=True)

    op.create_table(
        "poll_option",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("poll_id", sa.Integer(), sa.ForeignKey("poll.id"), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_poll_option_poll_id", "poll_option", ["poll_id"])

    op.create_table(
        "poll_vote",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("poll_id", sa.Integer(), sa.ForeignKey("poll.id"), nullable=False),
        sa.Column("option_id", sa.Integer(), sa.ForeignKey("poll_option.id"), nullable=False),
        sa.Column("voter", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_poll_vote_poll_id", "poll_vote", ["poll_id"])
    op.create_index("ix_poll_vote_option_id", "poll_vote", ["option_id"])
    # One vote per voter per poll, enforced by the database rather than by the
    # route remembering to check.
    op.create_index("ix_poll_vote_one_each", "poll_vote", ["poll_id", "voter"], unique=True)


def downgrade() -> None:
    op.drop_table("poll_vote")
    op.drop_table("poll_option")
    op.drop_index("ix_poll_slug", table_name="poll")
    op.drop_table("poll")
