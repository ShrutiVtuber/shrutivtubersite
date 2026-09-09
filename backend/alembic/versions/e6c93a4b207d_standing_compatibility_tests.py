"""Standing compatibility tests

Two things: "Are you compatible with Shruti?" — hers, permanent, a share hook —
and one another VTuber can set up against their own chart for a run their tier
decides.

⚠ A membership feature with an expiry, not a page. An expired test that keeps
answering is a feature given away; one that 404s without explanation is a VTuber
who thinks the site is broken.

Revision identifiers, used by Alembic.
revision = "e6c93a4b207d"
down_revision = "d5b82e3f1a47"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e6c93a4b207d"
down_revision = "d5b82e3f1a47"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "standing_test",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True, index=True),
        # ⚠ RESTRICT, not CASCADE. A host deleting their chart should stop the
        # test, and finding out at the moment of deletion is better than the
        # test quietly disappearing along with it.
        sa.Column("chart_id", sa.Integer(),
                  sa.ForeignKey("saved_chart.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=True, index=True),
        sa.Column("host_name", sa.String(), nullable=False, server_default=""),
        sa.Column("blurb", sa.String(), nullable=False, server_default=""),
        sa.Column("tier_at_setup", sa.String(), nullable=False, server_default=""),
        # ⚠ Null means permanent.
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("standing_test")
