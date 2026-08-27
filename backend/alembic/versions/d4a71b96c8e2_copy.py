"""Every string on a page, editable.

Revision ID: d4a71b96c8e2
Revises: c9d24e13f5a7

Page blocks cover sections. Most of the words on this site are not sections —
they are the line under a form, the label on a button, the sentence explaining
why a field is optional. Roughly six thousand of them lived in templates, on a
site whose premise is that she edits it herself.

Nothing is seeded by this migration. The templates keep their own defaults, a
row only ever overrides one, and the seeder that fills this table reads from
the templates rather than the reverse — so an empty table renders a complete
site and this can be adopted a page at a time.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4a71b96c8e2"
down_revision = "c9d24e13f5a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "copy",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page", sa.String(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("multiline", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("default_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_copy_page", "copy", ["page"])
    op.create_index("ix_copy_key", "copy", ["key"])
    # One row per string per page. Without this a double seed silently gives a
    # page two answers for the same key and the winner is whichever the query
    # happens to return first.
    op.create_unique_constraint("uq_copy_page_key", "copy", ["page", "key"])


def downgrade() -> None:
    op.drop_constraint("uq_copy_page_key", "copy", type_="unique")
    op.drop_index("ix_copy_key", table_name="copy")
    op.drop_index("ix_copy_page", table_name="copy")
    op.drop_table("copy")
