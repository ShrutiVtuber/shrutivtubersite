"""Groups: a shared goal, contributions, no path

Revision ID: c1e7a3b8d945
Revises: b9d4e6f1c027
"""
from alembic import op
import sqlalchemy as sa

revision = "c1e7a3b8d945"
down_revision = "b9d4e6f1c027"
branch_labels = None
depends_on = None


def _ts():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]


def upgrade() -> None:
    op.create_table(
        "guide_group",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("goal", sa.String(), nullable=False, server_default=""),
        sa.Column("target", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tiers", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_ts(),
    )
    op.create_index("ix_guide_group_code", "guide_group", ["code"], unique=True)
    op.create_index("ix_guide_group_created_by", "guide_group", ["created_by"])
    op.create_table(
        "guide_group_member",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("guide_group.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        *_ts(),
    )
    op.create_index("ix_guide_group_member_group_id", "guide_group_member", ["group_id"])
    op.create_index("ix_guide_group_member_user_id", "guide_group_member", ["user_id"])
    op.create_unique_constraint("uq_group_member", "guide_group_member", ["group_id", "user_id"])
    op.create_table(
        "guide_group_contribution",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("guide_group.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
    )
    op.create_index("ix_guide_group_contribution_group_id", "guide_group_contribution", ["group_id"])
    op.create_index("ix_guide_group_contribution_user_id", "guide_group_contribution", ["user_id"])
    op.add_column("overlay_token", sa.Column("group_id", sa.Integer(), sa.ForeignKey("guide_group.id"), nullable=True))
    op.add_column("overlay_token", sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("overlay_token", "user_id")
    op.drop_column("overlay_token", "group_id")
    for t in ("guide_group_contribution", "guide_group_member", "guide_group"):
        op.drop_table(t)
