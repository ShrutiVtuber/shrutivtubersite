"""Media remembers where it was stored

Files uploaded before R2 was configured are on local disk. Without recording
which backend a row used, switching R2 on would rewrite every existing URL to
point at a bucket that does not contain those files — every image on the site
would 404 at once, and the cause would not be obvious.

Existing rows are backfilled to 'local', which is where they are.

Revision ID: b7d2e91f4a63
Revises: a4f81c26b9e0
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7d2e91f4a63"
down_revision: Union[str, None] = "a4f81c26b9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "media",
        sa.Column("storage_backend", sa.String(), nullable=False, server_default="local"),
    )


def downgrade() -> None:
    op.drop_column("media", "storage_backend")
