"""A comment can be about one reading, and a bridge message can name one

⚠ **Discord cannot nest threads.** A thread hangs off a message in a channel,
and a message inside a thread cannot have a thread of its own. That is a
platform limit, and it shapes this migration: a submission becomes one
announcement in the channel, one thread beneath it, and one message per sign
inside that thread. `practice_bridge.sign` is what turns a reply to the Taurus
message into a comment on Taurus rather than on the week.

`practice_comment.sign` is the same fact on the site's side. Empty means the
whole set — "this reads well as a series" is a real thing to say about twelve
signs, and it is not the same as saying it about Aries.

Both default to '' rather than NULL. Every existing comment really is about the
whole work, because until now there was nothing else it could be about, so ''
is the true value for all of them and not a placeholder.

Revision ID: f6b21e93c4a7
Revises: e5c93f27a1d8
"""
from alembic import op
import sqlalchemy as sa

revision = "f6b21e93c4a7"
down_revision = "e5c93f27a1d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "practice_comment",
        sa.Column("sign", sa.String(), nullable=False, server_default=""),
    )
    op.create_index("ix_practice_comment_sign", "practice_comment", ["sign"])

    op.add_column(
        "practice_bridge",
        sa.Column("sign", sa.String(), nullable=False, server_default=""),
    )
    op.create_index("ix_practice_bridge_sign", "practice_bridge", ["sign"])

    op.add_column(
        "practice_bridge",
        sa.Column("thread_id", sa.String(), nullable=False, server_default=""),
    )
    op.create_index("ix_practice_bridge_thread_id", "practice_bridge", ["thread_id"])


def downgrade() -> None:
    op.drop_index("ix_practice_bridge_thread_id", table_name="practice_bridge")
    op.drop_column("practice_bridge", "thread_id")
    op.drop_index("ix_practice_bridge_sign", table_name="practice_bridge")
    op.drop_column("practice_bridge", "sign")
    op.drop_index("ix_practice_comment_sign", table_name="practice_comment")
    op.drop_column("practice_comment", "sign")
