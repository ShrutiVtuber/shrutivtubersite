"""Blocking a person in the practice room

⚠ **Apple's guideline 1.2.** An app carrying other people's writing must offer
a way to filter objectionable material, a way to report it, published contact
details, AND the ability to block an abusive user. The first three were built
with the room; this is the fourth, and without it the iOS submission is
rejected on a rule rather than on anything anybody can see in the app.

A block is one reader's decision about their own room. Nobody is told, nothing
is hidden from anybody else, and it is not a strike — it sits beside the report
queue rather than inside it.

⚠ Cuts both ways: it hides their writing from you and stops them commenting on
yours. One direction alone would leave the person you blocked still able to
reach you, which is the thing the button is for.

Revision ID: a9d41c72e8b3
Revises: f6b21e93c4a7
"""
from alembic import op
import sqlalchemy as sa

revision = "a9d41c72e8b3"
down_revision = "f6b21e93c4a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "practice_block",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("blocked_id", sa.Integer(),
                  sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_practice_block_user_id", "practice_block", ["user_id"])
    op.create_index(
        "ix_practice_block_blocked_id", "practice_block", ["blocked_id"])
    # ⚠ Unique on the pair. Pressing block twice is not two blocks, and without
    # this the second press quietly adds a duplicate row that every unblock
    # then fails to fully undo — the person stays hidden and nothing explains
    # why.
    op.create_unique_constraint(
        "uq_practice_block_pair", "practice_block", ["user_id", "blocked_id"])


def downgrade() -> None:
    op.drop_constraint("uq_practice_block_pair", "practice_block",
                       type_="unique")
    op.drop_index("ix_practice_block_blocked_id", table_name="practice_block")
    op.drop_index("ix_practice_block_user_id", table_name="practice_block")
    op.drop_table("practice_block")
