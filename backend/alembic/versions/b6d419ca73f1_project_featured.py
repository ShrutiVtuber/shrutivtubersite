"""Choosing which projects lead the landing page

The landing page took the first two projects in portfolio order, so changing
which ones a stranger meets first meant reordering the whole of /work. They are
different questions — the newest instrument is not always the best
introduction — so featuring is its own flag.

Nothing is featured to begin with. The landing page falls back to the first two
in order when nothing is chosen, which is exactly what it did before, so this
migration changes no page until somebody ticks something.

Revision ID: b6d419ca73f1
Revises: a3c85f1e207d
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b6d419ca73f1"
down_revision: Union[str, None] = "a3c85f1e207d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "project",
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_project_featured", "project", ["featured"])


def downgrade() -> None:
    op.drop_index("ix_project_featured", table_name="project")
    op.drop_column("project", "featured")
