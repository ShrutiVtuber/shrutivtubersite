"""Swara Studio: recordings she adds herself, and a slot's link can be swapped

Revision ID: s7r3n0o6p632
Revises: r6q2m9n5o521

A recording id is a slot the lessons, exercises and embeds point at. She
can now paste a link to add one in the Studio, and replace the video in a
slot while keeping its id: the old links are kept in `link_history`. The
provider's thumbnail and whether it allows embedding (from oEmbed) are kept
for the queue.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "s7r3n0o6p632"
down_revision = "r6q2m9n5o521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("carnatic_recording", sa.Column("link_history", JSONB(), nullable=False, server_default="[]"))
    op.add_column("carnatic_recording", sa.Column("thumbnail", sa.String(), nullable=False, server_default=""))
    op.add_column("carnatic_recording", sa.Column("embeddable", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("carnatic_recording", "embeddable")
    op.drop_column("carnatic_recording", "thumbnail")
    op.drop_column("carnatic_recording", "link_history")
