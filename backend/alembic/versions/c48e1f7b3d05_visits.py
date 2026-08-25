"""Counting visits without following anybody

One row per page opened or tool used. No cookie, and no identifier that
outlives a day: `visitor` is a hash of address, browser string, today's date
and a server secret, so the same person is one number today and another
tomorrow and the number cannot be turned back into an address.

That is what makes "how much is each tool used" answerable without tracking
anybody — and why it needs no consent banner, because nothing stored
identifies a person.

Revision ID: c48e1f7b3d05
Revises: b3d97f5a2e14
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c48e1f7b3d05"
down_revision: Union[str, None] = "b3d97f5a2e14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "visit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("event", sa.String(), nullable=False, server_default=""),
        sa.Column("props", sa.String(), nullable=False, server_default=""),
        sa.Column("visitor", sa.String(), nullable=False),
        sa.Column("referrer", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_visit_day", "visit", ["day"])
    op.create_index("ix_visit_path", "visit", ["path"])
    op.create_index("ix_visit_event", "visit", ["event"])
    op.create_index("ix_visit_visitor", "visit", ["visitor"])
    # The one query the admin actually runs.
    op.create_index("ix_visit_day_path", "visit", ["day", "path"])


def downgrade() -> None:
    op.drop_table("visit")
