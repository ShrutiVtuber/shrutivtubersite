"""Supporters choose the name she reads out

Her note: "when someone makes a donation or purchases a membership we need to
make sure that they have a place to supply their name to be read on stream (if
they want a custom name). This is only for monthly supporters - one offs are not
read on stream."

Revision identifiers, used by Alembic.
revision = "c4a71f2b8d05"
down_revision = "b8e4c1d90f23"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c4a71f2b8d05"
down_revision = "b8e4c1d90f23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "supporter",
        sa.Column("stream_name", sa.String(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("supporter", "stream_name")
