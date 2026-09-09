"""Horoscope practice: works, readings, votes and comments

Somewhere for people learning to write horoscopes to put one in front of others,
be told what they think, and improve — and for her to pick the best to read on
stream.

⚠ A WORK is the unit, not a reading. Twelve signs for a week is one piece of
work and is voted on as one; a single reading is a work holding one.

Revision identifiers, used by Alembic.
revision = "d5b82e3f1a47"
down_revision = "c4a71f2b8d05"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d5b82e3f1a47"
down_revision = "c4a71f2b8d05"
branch_labels = None
depends_on = None


def _stamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    op.create_table(
        "practice_work",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("period", sa.String(), nullable=False, server_default="weekly"),
        sa.Column("covers", sa.String(), nullable=False, server_default=""),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        # ⚠ Null means draft. Every query that serves other people filters here.
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_stamps(),
    )
    op.create_index("ix_practice_work_period", "practice_work", ["period"])
    op.create_index("ix_practice_work_covers", "practice_work", ["covers"])
    # One draft per person per period — the desk saves into it as they write,
    # and a second would mean their words silently splitting in two.
    op.create_index(
        "ux_practice_draft", "practice_work",
        ["user_id", "period", "covers"],
        unique=True, postgresql_where=sa.text("submitted_at IS NULL"),
    )

    op.create_table(
        "practice_reading",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(),
                  sa.ForeignKey("practice_work.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("sign", sa.String(), nullable=False, index=True),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        *_stamps(),
        sa.UniqueConstraint("work_id", "sign", name="ux_practice_reading_sign"),
    )

    op.create_table(
        "practice_vote",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(),
                  sa.ForeignKey("practice_work.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        *_stamps(),
        # ⚠ In the database, not in a check-then-insert. Two taps on a slow
        # connection are two requests and would otherwise count twice.
        sa.UniqueConstraint("work_id", "user_id", name="ux_practice_vote_once"),
    )

    op.create_table(
        "practice_comment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(),
                  sa.ForeignKey("practice_work.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_stamps(),
    )


def downgrade() -> None:
    op.drop_table("practice_comment")
    op.drop_table("practice_vote")
    op.drop_table("practice_reading")
    op.drop_index("ux_practice_draft", table_name="practice_work")
    op.drop_table("practice_work")
