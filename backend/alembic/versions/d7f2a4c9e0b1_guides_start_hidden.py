"""Shruti's Guides starts hidden

Sections default to LIVE — absent means live, so a lost settings row can
never make a section vanish. That default is right for a section that has
always been there and wrong for one that is new: /guides would go up with
the deploy, empty, before she had published a single guide. Her words were
that the links appear "when it's ready".

So this writes the row that hides it, ONCE. ON CONFLICT DO NOTHING: if she
has already turned it on by the time this runs, her choice stands.

Revision ID: d7f2a4c9e0b1
Revises: c4e9b3a7d216
"""
from alembic import op

revision = "d7f2a4c9e0b1"
down_revision = "c4e9b3a7d216"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO site_setting (key, value, created_at, updated_at) "
        "VALUES ('page.guides', '0', now(), now()) "
        "ON CONFLICT (key) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DELETE FROM site_setting WHERE key = 'page.guides'")
