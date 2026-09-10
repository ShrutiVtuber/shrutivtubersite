# SPDX-License-Identifier: AGPL-3.0-only
"""Reports, suspensions, and why a thing is hidden

People now post writing that other people read, so the room needs a way to say
something should not be there — and a way for that to act before she wakes up.

⚠ **Three reports hide a thing automatically, and that is a stopgap, not a
verdict.** The row is a queue entry: she sees every one and either agrees or
puts it straight back. Leaving something up for eight hours because it arrived
at 3am is the failure that actually matters; a wrongly hidden reading is
visible again in a tap.

⚠ **One report per person per thing**, enforced here rather than checked in
Python. Otherwise one determined person is a takedown on their own, and the
auto-hide becomes a weapon instead of a stopgap.

⚠ **`hidden_by` exists because `hidden` cannot answer "why".** A takedown by
three strangers is provisional and waiting for her; a decision of hers is
settled; an author withdrawing their own work is neither. They are undone
differently and a boolean cannot tell them apart.

Revision identifiers, used by Alembic.
revision = "b7e41c92d8a3"
down_revision = "a2f47d9c3b16"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b7e41c92d8a3"
down_revision = "a2f47d9c3b16"
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
    op.add_column(
        "practice_work",
        sa.Column("hidden_by", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "practice_comment",
        sa.Column("hidden_by", sa.String(), nullable=False, server_default=""),
    )
    # A comment bridged in from Discord has no account behind it. It carries the
    # name Discord gave it and is marked as what it is, rather than being
    # silently attributed to somebody real.
    op.add_column(
        "practice_comment",
        sa.Column("from_discord", sa.String(), nullable=False,
                  server_default=""),
    )

    op.create_table(
        "practice_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Exactly one of these. A report is about a work OR a comment.
        sa.Column("work_id", sa.Integer(),
                  sa.ForeignKey("practice_work.id", ondelete="CASCADE"),
                  nullable=True),
        sa.Column("comment_id", sa.Integer(),
                  sa.ForeignKey("practice_comment.id", ondelete="CASCADE"),
                  nullable=True),
        # Null for a reporter from Discord, who has no site account.
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("from_discord", sa.String(), nullable=False,
                  server_default=""),
        sa.Column("reason", sa.String(), nullable=False, server_default="other"),
        sa.Column("detail", sa.String(), nullable=False, server_default=""),
        # ⚠ Set when SHE has looked, never by the auto-hide. A report that hid
        # something and was never reviewed is exactly the state this makes
        # visible.
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", sa.String(), nullable=False, server_default=""),
        *_stamps(),
        sa.CheckConstraint(
            "(work_id IS NOT NULL) <> (comment_id IS NOT NULL)",
            name="ck_practice_report_one_subject",
        ),
    )
    op.create_index("ix_practice_report_work", "practice_report", ["work_id"])
    op.create_index("ix_practice_report_comment", "practice_report",
                    ["comment_id"])
    op.create_index("ix_practice_report_reason", "practice_report", ["reason"])
    # ⚠ The queue's own index: unreviewed first is the only order anybody wants
    # to read this table in.
    op.create_index("ix_practice_report_open", "practice_report",
                    ["reviewed_at"])

    # One report per person per thing. Two taps on a slow connection are two
    # requests, and a check-then-insert would count both — the same reason the
    # votes table is unique in the database rather than in Python.
    op.create_index(
        "ux_practice_report_work_user", "practice_report",
        ["work_id", "user_id"], unique=True,
        postgresql_where=sa.text("work_id IS NOT NULL AND user_id IS NOT NULL"),
    )
    op.create_index(
        "ux_practice_report_comment_user", "practice_report",
        ["comment_id", "user_id"], unique=True,
        postgresql_where=sa.text(
            "comment_id IS NOT NULL AND user_id IS NOT NULL"),
    )
    # And the same for a reporter from Discord, keyed on who Discord says they
    # are. Without this the bridge is a way round the limit.
    op.create_index(
        "ux_practice_report_work_discord", "practice_report",
        ["work_id", "from_discord"], unique=True,
        postgresql_where=sa.text("work_id IS NOT NULL AND from_discord <> ''"),
    )

    op.create_table(
        "practice_strike",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("site_user.id", ondelete="CASCADE"),
                  nullable=False),
        # ⚠ NULL MEANS INDEFINITE, not "not suspended". Read it the other way
        # and every permanent suspension lifts itself silently.
        sa.Column("until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(), nullable=False, server_default=""),
        sa.Column("lifted_at", sa.DateTime(timezone=True), nullable=True),
        *_stamps(),
    )
    op.create_index("ix_practice_strike_user", "practice_strike", ["user_id"])


def downgrade() -> None:
    op.drop_table("practice_strike")
    op.drop_table("practice_report")
    op.drop_column("practice_comment", "from_discord")
    op.drop_column("practice_comment", "hidden_by")
    op.drop_column("practice_work", "hidden_by")
