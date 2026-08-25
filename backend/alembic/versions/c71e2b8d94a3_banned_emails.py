"""Addresses that may not register again

Banning deletes the account, so the ban has to outlive it — otherwise the same
address signs up again the next morning and nothing was done.

The address itself is not kept. A ban follows a deletion and the deletion was
the point; a readable list of just-deleted addresses would quietly rebuild what
was meant to go. The hash answers the only question ever asked of it and cannot
be read back into a mailing list. A short hint is kept so the list can be read
by a human at all, and the reason because a ban nobody can review later is one
she cannot undo fairly.

Revision ID: c71e2b8d94a3
Revises: b6d419ca73f1
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c71e2b8d94a3"
down_revision: Union[str, None] = "b6d419ca73f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "banned_email",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email_hash", sa.String(), nullable=False, unique=True),
        sa.Column("reason", sa.String(), nullable=False, server_default=""),
        sa.Column("hint", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_banned_email_email_hash", "banned_email", ["email_hash"])


def downgrade() -> None:
    op.drop_index("ix_banned_email_email_hash", table_name="banned_email")
    op.drop_table("banned_email")
