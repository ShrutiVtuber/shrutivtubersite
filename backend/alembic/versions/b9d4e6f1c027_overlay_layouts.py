"""An overlay token may carry a layout: several elements in one browser source

Revision ID: b9d4e6f1c027
Revises: a8c3d9e2f014
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b9d4e6f1c027"
down_revision = "a8c3d9e2f014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("overlay_token", sa.Column("layout", postgresql.JSONB(), nullable=False, server_default="[]"))


def downgrade() -> None:
    op.drop_column("overlay_token", "layout")
