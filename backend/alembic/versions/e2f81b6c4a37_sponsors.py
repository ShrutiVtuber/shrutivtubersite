"""Channel sponsors, with their own colours

The background and ink are columns because a sponsor's brand is theirs. This
is the one table on the site where storing a hex colour is correct rather than
a shortcut around the design tokens.

Revision ID: e2f81b6c4a37
Revises: d91a4c7e2b58
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2f81b6c4a37"
down_revision: Union[str, None] = "d91a4c7e2b58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sponsor",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("tagline", sa.String(), nullable=False, server_default=""),
        sa.Column("body_md", sa.String(), nullable=False, server_default=""),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("cta_label", sa.String(), nullable=False, server_default=""),
        sa.Column("background", sa.String(), nullable=False, server_default=""),
        sa.Column("ink", sa.String(), nullable=False, server_default=""),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("media_dark_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("since", sa.String(), nullable=False, server_default=""),
        sa.Column("until", sa.String(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_sponsor_slug", "sponsor", ["slug"], unique=True)
    op.create_index("ix_sponsor_featured", "sponsor", ["featured"])


def downgrade() -> None:
    op.drop_index("ix_sponsor_featured", table_name="sponsor")
    op.drop_index("ix_sponsor_slug", table_name="sponsor")
    op.drop_table("sponsor")
