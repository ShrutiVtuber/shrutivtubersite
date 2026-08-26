"""An account remembers where you are.

Revision ID: d1a68f30b57e
Revises: c9e07f4a1d63

Planetary hours, the solar and lunar stations and all three calendars need a
horizon, and every one of them defaulted to Athens. A signed-in visitor in
Toronto was therefore re-typing their own city on every page and on every
visit, while their account stored a timezone that no instrument ever read.

This is the most useful thing an account can remember on this site, and it is
the thing the invitation on those pages now says it does — the copy and the
behaviour arriving together on purpose, because the alternative was writing the
copy first and hoping.

Deliberately not used by the natal chart. That place is where somebody was
born: the same shape, a different fact, and defaulting it to where they live
now would quietly cast the wrong chart.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d1a68f30b57e"
down_revision = "c9e07f4a1d63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_user", sa.Column("place_name", sa.String(), nullable=False,
                                         server_default=""))
    op.add_column("site_user", sa.Column("place_lat", sa.Float(), nullable=True))
    op.add_column("site_user", sa.Column("place_lon", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("site_user", "place_lon")
    op.drop_column("site_user", "place_lat")
    op.drop_column("site_user", "place_name")
