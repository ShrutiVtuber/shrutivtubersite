"""A layout may be shared in the gallery

Revision ID: e3c9d5a1f267
Revises: d2f8b4c9e156
"""
from alembic import op
import sqlalchemy as sa

revision = "e3c9d5a1f267"
down_revision = "d2f8b4c9e156"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("overlay_token", sa.Column("shared", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("overlay_token", "shared")
