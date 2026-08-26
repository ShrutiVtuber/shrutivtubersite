"""Share card designs, as rows rather than a dict in the code

So a new design is something she makes on a Tuesday rather than something a
developer deploys. The two that ship are seeded rows like any other.

Revision ID: f04b28d9c761
Revises: e91c04ab7d35
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f04b28d9c761"
down_revision: Union[str, None] = "e91c04ab7d35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "card_design",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("background", sa.String(), nullable=False, server_default="#F6F2EF"),
        sa.Column("ink", sa.String(), nullable=False, server_default="#26304A"),
        sa.Column("soft", sa.String(), nullable=False, server_default="#4A5470"),
        sa.Column("faint", sa.String(), nullable=False, server_default="#6E7890"),
        sa.Column("line", sa.String(), nullable=False, server_default="#DCD6DC"),
        sa.Column("accent", sa.String(), nullable=False, server_default="#A85A76"),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("scrim", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_card_design_key", "card_design", ["key"], unique=True)

    # The two that ship. Seeded here rather than in a script so a fresh
    # database is never left with no design at all — the card has to render
    # on the day the site goes up.
    op.bulk_insert(
        sa.table(
            "card_design",
            sa.column("key"), sa.column("name"),
            sa.column("background"), sa.column("ink"), sa.column("soft"),
            sa.column("faint"), sa.column("line"), sa.column("accent"),
            sa.column("position"), sa.column("visible"),
        ),
        [
            {"key": "light", "name": "Paper", "background": "#F6F2EF",
             "ink": "#26304A", "soft": "#4A5470", "faint": "#6E7890",
             "line": "#DCD6DC", "accent": "#A85A76", "position": 0, "visible": True},
            {"key": "dark", "name": "Night", "background": "#121829",
             "ink": "#EEF0F8", "soft": "#B0B8CC", "faint": "#8A94AC",
             "line": "#303A54", "accent": "#D694AC", "position": 1, "visible": True},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_card_design_key", table_name="card_design")
    op.drop_table("card_design")
