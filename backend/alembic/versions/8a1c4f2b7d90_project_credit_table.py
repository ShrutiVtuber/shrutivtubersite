"""Project credit table: role, stack, licence, contributors

The /work design mandates a per-project credit table — Name · Role · Stack ·
Licence · Status — and calls it the thing that makes the page a portfolio of
instruments rather than an app-store listing. Three of those five had nowhere
to live: only name and status existed as columns.

Putting them in body_md was the alternative and it is worse. Prose cannot be
rendered as a table consistently, cannot be queried, and cannot be edited field
by field in the admin.

Revision ID: 8a1c4f2b7d90
Revises: 59bf91952c07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "8a1c4f2b7d90"
down_revision: Union[str, None] = "59bf91952c07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNS = ("role", "stack", "licence", "contributors")


def upgrade() -> None:
    for name in COLUMNS:
        op.add_column(
            "project",
            sa.Column(name, sa.String(), nullable=False, server_default=""),
        )


def downgrade() -> None:
    for name in reversed(COLUMNS):
        op.drop_column("project", name)
