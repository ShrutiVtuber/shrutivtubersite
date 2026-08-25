"""Media gets a name and tags

Uploading gave a file a content hash and nothing else, so the library was a
wall of thumbnails labelled by the first fourteen characters of a SHA-256.
Finding anything meant recognising it by sight.

The filename stays the hash. That is what dedupes an image uploaded twice and
what keeps a URL stable forever, and neither should be given up to make a name
readable — so the name is a column beside it, and renaming touches nothing but
the row.

Revision ID: a3c85f1e207d
Revises: f2a71d4c9e08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3c85f1e207d"
down_revision: Union[str, None] = "f2a71d4c9e08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("media", sa.Column("title", sa.String(), nullable=False, server_default=""))
    op.add_column("media", sa.Column("tags", sa.String(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("media", "tags")
    op.drop_column("media", "title")
