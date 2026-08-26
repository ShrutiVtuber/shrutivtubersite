"""Modern formats beside the original.

Revision ID: c9d24e13f5a7
Revises: b8f31d02e7c4

Recorded rather than guessed. A <source> pointing at a file that does not exist
is a broken image, not a graceful fallback — so the page has to know what was
actually written, before the browser asks.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c9d24e13f5a7"
down_revision = "b8f31d02e7c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("media", sa.Column("variants", sa.String(), nullable=False,
                                     server_default=""))


def downgrade() -> None:
    op.drop_column("media", "variants")
