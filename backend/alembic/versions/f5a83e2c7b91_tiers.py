"""Memberships become something she can add

Two names in a dict and two price IDs in the environment: a third tier needed a
deploy and a fourth needed a developer. What she sells is content, not
configuration.

The two that exist are carried over with their copy intact — the wording is the
designer's and was reviewed, so it is moved rather than rewritten. Their Stripe
price IDs come across from the environment on first read, so nothing that is
already subscribed notices anything.

Revision ID: f5a83e2c7b91
Revises: e94b7c2d1a58
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f5a83e2c7b91"
down_revision: Union[str, None] = "e94b7c2d1a58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tier",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tagline", sa.String(), nullable=False, server_default=""),
        sa.Column("perks", sa.String(), nullable=False, server_default=""),
        sa.Column("cta", sa.String(), nullable=False, server_default=""),
        sa.Column("badge", sa.String(), nullable=False, server_default=""),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("interval", sa.String(), nullable=False, server_default="month"),
        sa.Column("tax_code", sa.String(), nullable=False, server_default="txcd_10000000"),
        sa.Column("stripe_product_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_price_id", sa.String(), nullable=False, server_default=""),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_tier_key", "tier", ["key"])

    # The two that exist, with the copy they already have. Visible, because they
    # already are — a migration that hid a live membership would be a migration
    # that stopped the money.
    op.execute(
        """
        INSERT INTO tier (key, name, tagline, perks, cta, badge, featured,
                          price_cents, currency, interval, visible, position,
                          created_at, updated_at)
        VALUES
        ('lamplighter', 'Lamplighter', '',
         'Members channel on Discord\nSchedule a day early\nName in the monthly credits roll',
         'Become a Lamplighter', 'Most common', true, 500, 'eur', 'month', true, 10,
         now(), now()),
        ('almanac', 'Almanac', '',
         'Everything in Lamplighter\nMonthly practice notes, signed Soror Eu. A.\nA vote on the next instrument',
         'Become an Almanac', '', false, 1100, 'eur', 'month', true, 20,
         now(), now())
        """
    )


def downgrade() -> None:
    op.drop_table("tier")
