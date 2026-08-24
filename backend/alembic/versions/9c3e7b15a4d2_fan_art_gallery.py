"""Fan art gallery

The /fan-works surface had no table behind it. Artist credit is a required
column rather than free text in a caption, because the design makes it the
loudest element on the card and a gallery that loses attribution is worse than
no gallery at all.

Defaults to invisible: submissions are reviewed before they appear.

Revision ID: 9c3e7b15a4d2
Revises: 8a1c4f2b7d90
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9c3e7b15a4d2"
down_revision: Union[str, None] = "8a1c4f2b7d90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fan_art",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artist", sa.String(), nullable=False),
        sa.Column("artist_url", sa.String(), nullable=False, server_default=""),
        sa.Column("platform", sa.String(), nullable=False, server_default=""),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("fan_art")
