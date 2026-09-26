"""The Ledger on stream: the business on screen, the live plan, and ledger overlays

Revision ID: m1k7h4i0j076
Revises: l0j7g3h8i965

Three things the overlays read (docs/LEDGER.md, "The Ledger on stream"):

- `ledger.on_screen_business_id`: which business the stream is about. ON
  DELETE SET NULL, so deleting that business leaves the ledger with nothing on
  screen rather than refusing the delete.
- `ledger.live_plan`, `live_updated_at`, `live_change`: the plan on stream.
  The planner may stream a plan that was never kept, so the plan itself is
  stored here (`{"plan": {...}, "name": "..."}`), not a business id. One per
  ledger, overwritten; null when the switch is off.
- `overlay_token.ledger_id`: an overlay minted from a ledger. ON DELETE
  CASCADE: a ledger that goes takes its overlays with it, and so does the
  account, because the ledger cascades from `site_user`.

⚠ No foreign key to `site_user` is added here, so `NOBODYS_BUT_THEIRS` is
empty: everything new goes with the account through `ledger`.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "m1k7h4i0j076"
down_revision = "l0j7g3h8i965"
branch_labels = None
depends_on = None

NOBODYS_BUT_THEIRS: list[tuple[str, str]] = []


def upgrade() -> None:
    op.add_column("ledger", sa.Column(
        "on_screen_business_id", sa.Integer(),
        sa.ForeignKey("ledger_business.id", ondelete="SET NULL", name="fk_ledger_on_screen_business"),
        nullable=True))
    op.add_column("ledger", sa.Column("live_plan", JSONB(), nullable=True))
    op.add_column("ledger", sa.Column("live_updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ledger", sa.Column("live_change", JSONB(), nullable=True))
    op.add_column("overlay_token", sa.Column(
        "ledger_id", sa.Integer(),
        sa.ForeignKey("ledger.id", ondelete="CASCADE", name="fk_overlay_token_ledger"),
        nullable=True))
    op.create_index("ix_overlay_token_ledger_id", "overlay_token", ["ledger_id"])


def downgrade() -> None:
    op.drop_index("ix_overlay_token_ledger_id", table_name="overlay_token")
    op.drop_column("overlay_token", "ledger_id")
    op.drop_column("ledger", "live_change")
    op.drop_column("ledger", "live_updated_at")
    op.drop_column("ledger", "live_plan")
    op.drop_column("ledger", "on_screen_business_id")
