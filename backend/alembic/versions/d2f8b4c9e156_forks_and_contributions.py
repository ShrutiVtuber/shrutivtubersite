"""Forks remember their origin; a version may be somebody else's contribution

Revision ID: d2f8b4c9e156
Revises: c1e7a3b8d945
"""
from alembic import op
import sqlalchemy as sa

revision = "d2f8b4c9e156"
down_revision = "c1e7a3b8d945"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("guide", sa.Column("forked_from_id", sa.Integer(), nullable=True))
    op.create_index("ix_guide_forked_from_id", "guide", ["forked_from_id"])
    op.add_column("guide_version", sa.Column("contributed_by", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True))
    op.create_index("ix_guide_version_contributed_by", "guide_version", ["contributed_by"])
    op.add_column("guide_version", sa.Column("against_id", sa.Integer(), nullable=True))
    op.add_column("guide_version", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("guide_version", "accepted_at")
    op.drop_column("guide_version", "against_id")
    op.drop_index("ix_guide_version_contributed_by", table_name="guide_version")
    op.drop_column("guide_version", "contributed_by")
    op.drop_index("ix_guide_forked_from_id", table_name="guide")
    op.drop_column("guide", "forked_from_id")
