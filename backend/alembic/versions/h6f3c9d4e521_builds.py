"""Builds: a template of goals per game, and each person's build against it

Revision ID: h6f3c9d4e521
Revises: g5e2b8c3d410
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "h6f3c9d4e521"
down_revision = "g5e2b8c3d410"
branch_labels = None
depends_on = None


def _ts():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]


def upgrade() -> None:
    op.create_table(
        "build_template",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("guide_game.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False, server_default=""),
        sa.Column("categories", JSONB(), nullable=False, server_default="[]"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
    )
    op.create_index("ix_build_template_game_id", "build_template", ["game_id"])
    op.create_table(
        "build",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("build_template.id"), nullable=False),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("guide_run.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("variant", sa.String(), nullable=False, server_default=""),
        sa.Column("goals", JSONB(), nullable=False, server_default="{}"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )
    op.create_index("ix_build_user_id", "build", ["user_id"])
    op.create_index("ix_build_template_id", "build", ["template_id"])
    op.add_column("overlay_token", sa.Column("build_id", sa.Integer(), sa.ForeignKey("build.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("overlay_token", "build_id")
    op.drop_table("build")
    op.drop_table("build_template")
