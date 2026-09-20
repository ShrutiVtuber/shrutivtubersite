"""Planned builds: a build may stand on a plan instead of a template

Revision ID: i7g4d0e5f632
Revises: h6f3c9d4e521
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "i7g4d0e5f632"
down_revision = "h6f3c9d4e521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("build", "template_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("build", sa.Column("game_id", sa.Integer(), sa.ForeignKey("guide_game.id"), nullable=True))
    op.add_column("build", sa.Column("plan", JSONB(), nullable=False, server_default="{}"))
    op.add_column("build", sa.Column("categories", JSONB(), nullable=False, server_default="[]"))
    op.create_index("ix_build_game_id", "build", ["game_id"])


def downgrade() -> None:
    op.drop_index("ix_build_game_id", table_name="build")
    op.drop_column("build", "categories")
    op.drop_column("build", "plan")
    op.drop_column("build", "game_id")
    op.execute("DELETE FROM build WHERE template_id IS NULL")
    op.alter_column("build", "template_id", existing_type=sa.Integer(), nullable=False)
