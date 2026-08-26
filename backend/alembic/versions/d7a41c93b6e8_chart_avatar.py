"""An avatar on a kept chart, for the share card

Uploaded by the chart's own owner, never fetched from a social account: an
avatar pulled because somebody else typed a handle puts a face on a shareable
image without its owner agreeing.

Revision ID: d7a41c93b6e8
Revises: c5e83a71d92f
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d7a41c93b6e8"
down_revision: Union[str, None] = "c5e83a71d92f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("saved_chart",
                  sa.Column("avatar_media_id", sa.Integer(),
                            sa.ForeignKey("media.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("saved_chart", "avatar_media_id")
