"""Two moments per journal entry, not one

An entry has two skies worth recording and they answer different questions.
When it went up is discoverable — BeeRanked stamps the publication time into
the page it syncs, so it can be captured without being asked. When she started
writing it is not: BeeRanked records no creation time and exposes none through
its API, so that moment is hers to record or it does not exist. It is often the
more interesting one, because a piece begun under a Mars hour was begun under a
Mars hour whatever day it was finally published.

So the key becomes (slug, kind) rather than slug alone. Existing rows are
publication records — that is all the table could hold until now — so they take
the default and nothing is lost.

Revision ID: f2a71d4c9e08
Revises: e5b73a91c48d
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a71d4c9e08"
down_revision: Union[str, None] = "e5b73a91c48d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "journal_sky",
        sa.Column("kind", sa.String(), nullable=False, server_default="published"),
    )
    op.create_index("ix_journal_sky_kind", "journal_sky", ["kind"])

    # The old constraint said one sky per entry, which is what is changing.
    op.drop_constraint("journal_sky_slug_key", "journal_sky", type_="unique")
    op.create_unique_constraint(
        "journal_sky_slug_kind_key", "journal_sky", ["slug", "kind"]
    )


def downgrade() -> None:
    # Going back means one row per entry again, so anything but the publication
    # record has to go or the unique constraint cannot be rebuilt.
    op.execute("DELETE FROM journal_sky WHERE kind <> 'published'")
    op.drop_constraint("journal_sky_slug_kind_key", "journal_sky", type_="unique")
    op.create_unique_constraint("journal_sky_slug_key", "journal_sky", ["slug"])
    op.drop_index("ix_journal_sky_kind", table_name="journal_sky")
    op.drop_column("journal_sky", "kind")
