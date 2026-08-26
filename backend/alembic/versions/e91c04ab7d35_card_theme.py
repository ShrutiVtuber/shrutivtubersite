"""Which palette a comparison's share card is drawn in

Stored rather than passed as a query parameter: the card's address goes into
og:image and a social scraper fetches exactly what that says, so the choice has
to be part of the page rather than of the request.

Revision ID: e91c04ab7d35
Revises: d7a41c93b6e8
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e91c04ab7d35"
down_revision: Union[str, None] = "d7a41c93b6e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("comparison",
                  sa.Column("card_theme", sa.String(), nullable=False,
                            server_default="light"))


def downgrade() -> None:
    op.drop_column("comparison", "card_theme")
