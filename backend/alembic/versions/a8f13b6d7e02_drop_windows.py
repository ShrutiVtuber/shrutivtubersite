"""Two ways to sell: always open, and a drop with a window.

Revision ID: a8f13b6d7e02
Revises: f7c93de1b408

She prints her own things, so the usual constraint is inverted: there is no
minimum order and nothing has to be committed to in advance. That makes two
selling models both worth having, and she wants both.

  - **Always open.** Batch-printed, sitting on a shelf, or made to order with a
    lead time. No window; `stock` means what it always did, unless it is made
    to order, in which case there is no shelf to run out of.
  - **A drop.** Open for a fortnight around a birthday or an outfit reveal,
    then gone. A window is an optional pair of dates rather than a different
    kind of product, so one table and one shop page serve both.

`lead_time` is prose rather than a number of days because the honest answer to
"when will it arrive" is usually a range with a caveat on it.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a8f13b6d7e02"
down_revision = "f7c93de1b408"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product", sa.Column("made_to_order", sa.Boolean(), nullable=False,
                                       server_default=sa.false()))
    op.add_column("product", sa.Column("lead_time", sa.String(), nullable=False,
                                       server_default=""))
    op.add_column("product", sa.Column("opens_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("product", sa.Column("closes_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("product", "closes_at")
    op.drop_column("product", "opens_at")
    op.drop_column("product", "lead_time")
    op.drop_column("product", "made_to_order")
