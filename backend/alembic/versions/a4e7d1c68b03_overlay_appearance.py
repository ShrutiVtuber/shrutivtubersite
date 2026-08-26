"""Which ramp an overlay draws in.

Revision ID: a4e7d1c68b03
Revises: f31c8a06d92e

Almanac or Grimoire. On the overlay row rather than the counter, for the same
reason motion is: one counter can be shown on two machines or in two scenes,
and they may want different ones. The handoff's §2 sketch puts it on the
counter; its §5 sets it per canvas, and §5 is the one the drawing follows.

It was briefly inferred from whether the overlay's label began with the word
"grimoire", which is the kind of thing that works in a demo and quietly renames
somebody's overlay into a different appearance.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a4e7d1c68b03"
down_revision = "f31c8a06d92e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("overlay_token", sa.Column(
        "appearance", sa.String(), nullable=False, server_default="almanac"))


def downgrade() -> None:
    op.drop_column("overlay_token", "appearance")
