# SPDX-License-Identifier: AGPL-3.0-only
"""One OPEN report per person, not one for ever

⚠ The first index said one report per person per thing, permanently. That
closes a real hole and opens another: once she has ruled, the people who
reported can never report that thing again — and a work can be EDITED after a
dismissal. Whoever already spoke up is exactly the person most likely to notice
it turning into something worse, and they were the ones locked out.

So the uniqueness is on OPEN reports only. One at a time from each person; once
she has decided, the slate is clear and the room can speak again.

Revision identifiers, used by Alembic.
revision = "c8f2a91b4d67"
down_revision = "b7e41c92d8a3"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c8f2a91b4d67"
down_revision = "b7e41c92d8a3"
branch_labels = None
depends_on = None

OPEN = "reviewed_at IS NULL"


def upgrade() -> None:
    op.drop_index("ux_practice_report_work_user", table_name="practice_report")
    op.drop_index("ux_practice_report_comment_user",
                  table_name="practice_report")
    op.drop_index("ux_practice_report_work_discord",
                  table_name="practice_report")

    op.create_index(
        "ux_practice_report_work_user", "practice_report",
        ["work_id", "user_id"], unique=True,
        postgresql_where=sa.text(
            f"work_id IS NOT NULL AND user_id IS NOT NULL AND {OPEN}"),
    )
    op.create_index(
        "ux_practice_report_comment_user", "practice_report",
        ["comment_id", "user_id"], unique=True,
        postgresql_where=sa.text(
            f"comment_id IS NOT NULL AND user_id IS NOT NULL AND {OPEN}"),
    )
    op.create_index(
        "ux_practice_report_work_discord", "practice_report",
        ["work_id", "from_discord"], unique=True,
        postgresql_where=sa.text(
            f"work_id IS NOT NULL AND from_discord <> '' AND {OPEN}"),
    )


def downgrade() -> None:
    op.drop_index("ux_practice_report_work_user", table_name="practice_report")
    op.drop_index("ux_practice_report_comment_user",
                  table_name="practice_report")
    op.drop_index("ux_practice_report_work_discord",
                  table_name="practice_report")
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
    op.create_index(
        "ux_practice_report_work_discord", "practice_report",
        ["work_id", "from_discord"], unique=True,
        postgresql_where=sa.text("work_id IS NOT NULL AND from_discord <> ''"),
    )
