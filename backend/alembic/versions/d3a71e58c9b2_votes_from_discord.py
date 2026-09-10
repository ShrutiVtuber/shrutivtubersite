# SPDX-License-Identifier: AGPL-3.0-only
"""A vote from Discord, from somebody with no account

Half the room reads in the channel. A bridge that carries readings out and
comments in, but not votes, makes the highest-voted list a measurement of which
half of the audience happened to be in the app — which is the one number she
picks readings from.

⚠ **A Discord voter has no site account**, so `user_id` becomes nullable and
`from_discord` carries who Discord says it was. The uniqueness that makes one
vote one vote has to hold on both halves, so there are two partial indexes
rather than one.

⚠ **Never merged with a site account.** Somebody who votes in Discord and also
has an account can vote twice, and that is the honest answer: the bridge cannot
know they are the same person, and inventing a link between a Discord id and an
email is a claim about somebody the app cannot support.

Revision identifiers, used by Alembic.
revision = "d3a71e58c9b2"
down_revision = "c8f2a91b4d67"
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d3a71e58c9b2"
down_revision = "c8f2a91b4d67"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "practice_vote",
        sa.Column("from_discord", sa.String(), nullable=False,
                  server_default=""),
    )
    op.alter_column("practice_vote", "user_id", nullable=True)

    # ⚠ A CONSTRAINT, not an index: d5b82e3f1a47 made it with UniqueConstraint,
    # so it must be dropped as one. Dropping the index name instead fails, and
    # a NULLable user_id under a still-live (work_id, user_id) constraint would
    # let one Discord voter's NULLs pile up unpredictably across databases.
    op.drop_constraint("ux_practice_vote_once", "practice_vote", type_="unique")

    op.create_index(
        "ux_practice_vote_work_user", "practice_vote",
        ["work_id", "user_id"], unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "ux_practice_vote_work_discord", "practice_vote",
        ["work_id", "from_discord"], unique=True,
        postgresql_where=sa.text("from_discord <> ''"),
    )

    # ⚠ Which Discord message is which work. Without it a reaction is a number
    # on a message nothing can attribute, and a reply is a comment on nothing.
    op.create_table(
        "practice_bridge",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(),
                  sa.ForeignKey("practice_work.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("message_id", sa.String(), nullable=False),
        sa.Column("channel_id", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ux_practice_bridge_message", "practice_bridge",
                    ["message_id"], unique=True)
    op.create_index("ix_practice_bridge_work", "practice_bridge", ["work_id"])


def downgrade() -> None:
    op.drop_table("practice_bridge")
    op.drop_index("ux_practice_vote_work_discord", table_name="practice_vote")
    op.drop_index("ux_practice_vote_work_user", table_name="practice_vote")
    op.create_unique_constraint(
        "ux_practice_vote_once", "practice_vote", ["work_id", "user_id"])
    op.alter_column("practice_vote", "user_id", nullable=False)
    op.drop_column("practice_vote", "from_discord")
