"""The sky at the moment a journal entry was published

Theourgia stamps every record with what the world was doing when it was made,
and a journal of practice deserves the same. The entries live in BeeRanked;
this table holds only what BeeRanked cannot know.

Stored rather than recomputed on read, for two reasons. Rendering an index
should not cast twelve charts — and, more importantly, the sky captured is the
sky of the moment described. Re-casting later would quietly replace it with a
different one, which would make the record untrustworthy.

Revision ID: c9a04e1b78f2
Revises: b7d2e91f4a63
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9a04e1b78f2"
down_revision: Union[str, None] = "b7d2e91f4a63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "journal_sky",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False, server_default="0"),
        sa.Column("lon", sa.Float(), nullable=False, server_default="0"),
        sa.Column("place_name", sa.String(), nullable=False, server_default=""),
        sa.Column("reading", sa.Text(), nullable=False, server_default=""),
        sa.Column("summary", sa.String(), nullable=False, server_default=""),
        sa.Column("failure_reason", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_journal_sky_slug", "journal_sky", ["slug"])


def downgrade() -> None:
    op.drop_table("journal_sky")
