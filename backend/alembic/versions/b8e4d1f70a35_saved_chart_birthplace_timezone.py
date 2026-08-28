# SPDX-License-Identifier: AGPL-3.0-only
"""saved_chart: the birthplace timezone

Without it a saved chart cannot be re-cast correctly. The birth time was
entered as a local wall clock, and the ephemeris reads a datetime with no
offset as UTC — so every chart drawn from these rows was cast for the wrong
instant, by as little as an hour for London and as much as eight for Los
Angeles. The planets barely move; the ascendant moves a whole sign or more.

Empty for existing rows, deliberately. Nothing here guesses a zone from
coordinates: doing so would silently redraw somebody's saved chart into a
different one, which is a worse failure than saying the zone is not known and
asking them to reopen it. The pages flag those rows.

Revision ID: b8e4d1f70a35
Revises: d4a71b96c8e2
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b8e4d1f70a35"
down_revision = "d4a71b96c8e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "saved_chart",
        sa.Column("timezone", sa.String(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("saved_chart", "timezone")
