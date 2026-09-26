"""The Ledger: a company in one game, its businesses, and the weeks they ran

Revision ID: l0j7g3h8i965
Revises: k9i6f2g7h854

Three tables, private to the person who keeps them (docs/LEDGER.md).

⚠ **They go with the account from the first migration.** `ledger.user_id` is
ON DELETE CASCADE, and a business and its weeks cascade from the ledger, so
deleting an account needs nothing from `accounts.erase` to reach them — and no
later revision has to come back and add it, as k9i6f2g7h854 had to for nine
tables. `test_an_account_can_be_deleted` reads `NOBODYS_BUT_THEIRS` here.

⚠ **The week's lines are nullable, and have no server default.** Null means the
line was not written; a default of 0 would make every unwritten line a zero.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "l0j7g3h8i965"
down_revision = "k9i6f2g7h854"
branch_labels = None
depends_on = None

# Foreign keys to site_user this revision creates, all ON DELETE CASCADE.
NOBODYS_BUT_THEIRS = [("ledger", "user_id")]

MONEY_LINES = ("money_in", "goods", "wages", "rent", "ads", "deliveries")


def _ts():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]


def upgrade() -> None:
    op.create_table(
        "ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("game", sa.String(), nullable=False, server_default="big-ambitions"),
        sa.Column("version", sa.String(), nullable=False, server_default=""),
        sa.Column("difficulty", sa.String(), nullable=False, server_default="normal"),
        sa.Column("custom", JSONB(), nullable=True),
        sa.Column("in_game_day", sa.Integer(), nullable=True),
        sa.Column("courses", JSONB(), nullable=False, server_default="[]"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
    )
    op.create_index("ix_ledger_user_id", "ledger", ["user_id"])
    op.create_table(
        "ledger_business",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ledger_id", sa.Integer(), sa.ForeignKey("ledger.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plan", JSONB(), nullable=False, server_default="{}"),
        sa.Column("kept_plan", JSONB(), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
    )
    op.create_index("ix_ledger_business_ledger_id", "ledger_business", ["ledger_id"])
    op.create_table(
        "ledger_week",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("ledger_business.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("n", sa.Integer(), nullable=False),
        *(sa.Column(line, sa.Float(), nullable=True) for line in MONEY_LINES),
        sa.Column("units", sa.Integer(), nullable=True),
        sa.Column("customers", sa.Integer(), nullable=True),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        *_ts(),
        sa.UniqueConstraint("business_id", "n", name="uq_ledger_week_business_n"),
    )
    op.create_index("ix_ledger_week_business_id", "ledger_week", ["business_id"])


def downgrade() -> None:
    op.drop_table("ledger_week")
    op.drop_table("ledger_business")
    op.drop_table("ledger")
