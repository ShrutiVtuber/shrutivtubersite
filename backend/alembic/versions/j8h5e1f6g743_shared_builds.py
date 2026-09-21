"""Shared builds: a code to read one out, and a copy of your own

Revision ID: j8h5e1f6g743
Revises: i7g4d0e5f632
"""
from alembic import op
import sqlalchemy as sa

revision = "j8h5e1f6g743"
down_revision = "i7g4d0e5f632"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("build", sa.Column("share_code", sa.String(), nullable=True))
    op.add_column("build", sa.Column("shared_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("build", sa.Column("forked_from_id", sa.Integer(), nullable=True))
    op.create_index("ix_build_share_code", "build", ["share_code"], unique=True)
    op.create_index("ix_build_forked_from_id", "build", ["forked_from_id"])


def downgrade() -> None:
    op.drop_index("ix_build_forked_from_id", table_name="build")
    op.drop_index("ix_build_share_code", table_name="build")
    op.drop_column("build", "forked_from_id")
    op.drop_column("build", "shared_at")
    op.drop_column("build", "share_code")
