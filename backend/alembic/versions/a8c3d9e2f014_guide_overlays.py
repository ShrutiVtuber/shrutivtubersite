"""Guide overlays: a token may show a run, in a theme

Revision ID: a8c3d9e2f014
Revises: f5b2c8d1a734
"""
from alembic import op
import sqlalchemy as sa

revision = "a8c3d9e2f014"
down_revision = "f5b2c8d1a734"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("overlay_token", sa.Column("run_id", sa.Integer(), sa.ForeignKey("guide_run.id"), nullable=True))
    op.add_column("overlay_token", sa.Column("routine_id", sa.String(), nullable=False, server_default=""))
    op.add_column("overlay_token", sa.Column("theme", sa.String(), nullable=False, server_default="almanac"))
    op.create_index("ix_overlay_token_run_id", "overlay_token", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_overlay_token_run_id", table_name="overlay_token")
    op.drop_column("overlay_token", "theme")
    op.drop_column("overlay_token", "routine_id")
    op.drop_column("overlay_token", "run_id")
