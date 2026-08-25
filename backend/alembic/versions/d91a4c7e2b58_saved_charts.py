"""Charts somebody kept, with or without an account

Two tokens per chart. `owner_token` is how a person gets back to their own;
`share_token` is what they hand to a friend, minted only when they ask and
nulled when they take it back. One token would make those the same string, so
sharing would mean giving away your only way in and unsharing would be
impossible.

Neither token carries birth data, which keeps the date, time and place out of
the URL and out of a browser history.

The consent columns are here because this table holds special-category data and
an ownerless chart has no account to hang a consent record on. `expires_at` is
here for the same reason: consent that cannot be renewed by asking must not be
relied on forever.

Revision ID: d91a4c7e2b58
Revises: c48e1f7b3d05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d91a4c7e2b58"
down_revision: Union[str, None] = "c48e1f7b3d05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "saved_chart",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_token", sa.String(), nullable=False),
        sa.Column("share_token", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("label", sa.String(), nullable=False, server_default=""),

        sa.Column("tradition", sa.String(), nullable=False, server_default="hellenistic"),
        sa.Column("house_system", sa.String(), nullable=False, server_default="whole_sign"),
        sa.Column("figure", sa.String(), nullable=False, server_default="wheel"),

        sa.Column("birth_date", sa.String(), nullable=False, server_default=""),
        sa.Column("birth_time", sa.String(), nullable=True),
        sa.Column("time_unknown", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("place_name", sa.String(), nullable=False, server_default=""),
        sa.Column("lat", sa.Float(), nullable=False, server_default="0"),
        sa.Column("lon", sa.Float(), nullable=False, server_default="0"),

        sa.Column("consent_version", sa.String(), nullable=False, server_default=""),
        sa.Column("consent_wording", sa.String(), nullable=False, server_default=""),
        sa.Column("consent_source", sa.String(), nullable=False, server_default=""),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("shared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    # Unique so a token collision is a database error rather than one person
    # opening another person's chart.
    op.create_index("ix_saved_chart_owner_token", "saved_chart", ["owner_token"], unique=True)
    op.create_index("ix_saved_chart_share_token", "saved_chart", ["share_token"], unique=True)
    op.create_index("ix_saved_chart_user_id", "saved_chart", ["user_id"])
    # The sweep of expired ownerless charts reads this.
    op.create_index("ix_saved_chart_expires_at", "saved_chart", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_saved_chart_expires_at", table_name="saved_chart")
    op.drop_index("ix_saved_chart_user_id", table_name="saved_chart")
    op.drop_index("ix_saved_chart_share_token", table_name="saved_chart")
    op.drop_index("ix_saved_chart_owner_token", table_name="saved_chart")
    op.drop_table("saved_chart")
