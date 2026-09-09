"""Phones that asked to be told something

The app's half of notifications. Browsers are in push_subscription; a phone has
an FCM token and different machinery, so it gets its own table rather than a
column that means two things.

Revision identifiers, used by Alembic.
revision = "f7d02c58e19a"
down_revision = "e6c93a4b207d"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f7d02c58e19a"
down_revision = "e6c93a4b207d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_device",
        sa.Column("id", sa.Integer(), primary_key=True),
        # ⚠ Unique. A phone re-registering must UPDATE its row; duplicates mean
        # somebody told twice about the same stream.
        sa.Column("token", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("platform", sa.String(), nullable=False, server_default="android"),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=True, index=True),
        sa.Column("wants_live", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_video", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_horoscope", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("wants_writing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("wants_replies", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("app_device")
