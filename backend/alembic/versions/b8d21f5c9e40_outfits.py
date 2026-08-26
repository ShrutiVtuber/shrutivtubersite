"""Costumes, which used to be three hard-coded slots on the About page

Revision ID: b8d21f5c9e40
Revises: a4b93e17c02d
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8d21f5c9e40"
down_revision: Union[str, None] = "a4b93e17c02d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outfit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("status", sa.String(), nullable=False, server_default=""),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("artist", sa.String(), nullable=False, server_default=""),
        sa.Column("artist_url", sa.String(), nullable=False, server_default=""),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_outfit_slug", "outfit", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_outfit_slug", table_name="outfit")
    op.drop_table("outfit")
