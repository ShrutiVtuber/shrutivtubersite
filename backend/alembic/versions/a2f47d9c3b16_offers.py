"""Offers: sponsor deals and discounts, shown in the app

Her monetisation path for a free app. She makes an offer in the admin, Stripe
makes it real where it is hers, and it appears in the app on its own.

⚠ An offer that has ended must stop showing. One that keeps showing is a
discount she has to honour or refuse in public.

Revision identifiers, used by Alembic.
revision = "a2f47d9c3b16"
down_revision = "f7d02c58e19a"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a2f47d9c3b16"
down_revision = "f7d02c58e19a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offer",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("blurb", sa.String(), nullable=False, server_default=""),
        sa.Column("kind", sa.String(), nullable=False, server_default="shop",
                  index=True),
        # ⚠ SET NULL, not CASCADE. Deleting a discount should leave the offer
        # visible-but-broken so she notices, rather than silently removing a
        # thing she announced on stream.
        sa.Column("discount_id", sa.Integer(),
                  sa.ForeignKey("discount.id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("sponsor_id", sa.Integer(),
                  sa.ForeignKey("sponsor.id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("code", sa.String(), nullable=False, server_default=""),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        # Null means no end.
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("members_only", sa.Boolean(), nullable=False,
                  server_default=sa.false()),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("offer")
