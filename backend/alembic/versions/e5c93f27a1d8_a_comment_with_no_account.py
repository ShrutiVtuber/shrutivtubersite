# SPDX-License-Identifier: AGPL-3.0-only
"""A comment from Discord has no account behind it

⚠ `practice_comment.user_id` was NOT NULL, which is right for everything the
site itself accepts and wrong for the one thing the bridge carries. Somebody
replying in the channel has not signed up, agreed to anything, or been made
bannable — there is no row in site_user to point at, and inventing one would
be a claim about a person this app cannot support.

The model already carried `from_discord` and the endpoint already set it; the
column was the half that had not caught up, so every bridged reply failed with
a not-null violation and a 500.

Revision identifiers, used by Alembic.
revision = "e5c93f27a1d8"
down_revision = "d3a71e58c9b2"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e5c93f27a1d8"
down_revision = "d3a71e58c9b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("practice_comment", "user_id", nullable=True)
    # ⚠ Exactly one of the two, always. A row with neither an account nor a
    # Discord name is a comment nobody can attribute, and it would render as
    # "somebody" for ever with no way to tell whether that is a bug.
    op.create_check_constraint(
        "ck_practice_comment_has_an_author",
        "practice_comment",
        "(user_id IS NOT NULL) <> (from_discord <> '')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_practice_comment_has_an_author", "practice_comment",
                       type_="check")
    op.alter_column("practice_comment", "user_id", nullable=False)
