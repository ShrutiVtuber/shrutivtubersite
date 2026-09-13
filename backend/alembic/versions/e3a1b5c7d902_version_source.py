"""A guide version remembers which tool wrote it

desk | agent | file. Her review queue marks an agent's draft, and the rule
that nothing an agent does publishes is only checkable if the origin is kept.
Existing rows are the desk's.

Revision ID: e3a1b5c7d902
Revises: d7f2a4c9e0b1
"""
from alembic import op
import sqlalchemy as sa

revision = "e3a1b5c7d902"
down_revision = "d7f2a4c9e0b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("guide_version", sa.Column("source", sa.String(), nullable=False, server_default="desk"))


def downgrade() -> None:
    op.drop_column("guide_version", "source")
