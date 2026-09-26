"""Swara Studio: settings, progress, practice time, songs, Listen, reviews and app sign-in codes

Revision ID: n2l8i5j1k187
Revises: m1k7h4i0j076

The Carnatic music school at /carnatic (models/carnatic.py). The school's
FACTS are not here: they are files built from the private research by
scripts/sync-carnatic-data.sh. These tables hold what people chose and made,
and which script names and flagged facts a reviewer has checked.

⚠ **Everything that is a person's goes with their account, from the first
migration.** Every foreign key to site_user is ON DELETE CASCADE and is named
in `NOBODYS_BUT_THEIRS`, which `test_an_account_can_be_deleted` reads; a like
and a comment cascade from their post too.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "n2l8i5j1k187"
down_revision = "m1k7h4i0j076"
branch_labels = None
depends_on = None

# Foreign keys to site_user this revision creates, all ON DELETE CASCADE.
NOBODYS_BUT_THEIRS = [
    ("carnatic_profile", "user_id"),
    ("carnatic_progress", "user_id"),
    ("carnatic_practice_day", "user_id"),
    ("carnatic_song", "user_id"),
    ("carnatic_post", "user_id"),
    ("carnatic_like", "user_id"),
    ("carnatic_comment", "user_id"),
    ("carnatic_device_link", "user_id"),
]


def _ts():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]


def _user(**kw):
    return sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id", ondelete="CASCADE"), nullable=False, **kw)


def upgrade() -> None:
    op.create_table(
        "carnatic_profile",
        _user(primary_key=True),
        sa.Column("settings", JSONB(), nullable=False, server_default="{}"),
        *_ts(),
    )
    op.create_table(
        "carnatic_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("speeds", JSONB(), nullable=False, server_default="[]"),
        *_ts(),
        sa.UniqueConstraint("user_id", "item_id", name="uq_carnatic_progress_item"),
    )
    op.create_index("ix_carnatic_progress_user_id", "carnatic_progress", ["user_id"])
    op.create_table(
        "carnatic_practice_day",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sessions", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
        sa.UniqueConstraint("user_id", "day", name="uq_carnatic_practice_day"),
    )
    op.create_index("ix_carnatic_practice_day_user_id", "carnatic_practice_day", ["user_id"])
    op.create_table(
        "carnatic_song",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("raga", sa.String(), nullable=False, server_default=""),
        sa.Column("tala", sa.String(), nullable=False, server_default=""),
        sa.Column("body", JSONB(), nullable=False, server_default="{}"),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )
    op.create_index("ix_carnatic_song_user_id", "carnatic_song", ["user_id"])
    op.create_index("ix_carnatic_song_slug", "carnatic_song", ["slug"], unique=True)
    op.create_index("ix_carnatic_song_published", "carnatic_song", ["published"])
    op.create_table(
        "carnatic_post",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("song_id", sa.Integer(), sa.ForeignKey("carnatic_song.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("instrument", sa.String(), nullable=False, server_default=""),
        sa.Column("raga", sa.String(), nullable=False, server_default=""),
        sa.Column("tala", sa.String(), nullable=False, server_default=""),
        sa.Column("player", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hidden_by", sa.String(), nullable=False, server_default=""),
        *_ts(),
    )
    op.create_index("ix_carnatic_post_user_id", "carnatic_post", ["user_id"])
    op.create_index("ix_carnatic_post_hidden", "carnatic_post", ["hidden"])
    op.create_table(
        "carnatic_like",
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("carnatic_post.id", ondelete="CASCADE"), primary_key=True),
        _user(primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
    )
    op.create_table(
        "carnatic_comment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("carnatic_post.id", ondelete="CASCADE"), nullable=False),
        _user(),
        sa.Column("body", sa.String(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_ts(),
    )
    op.create_index("ix_carnatic_comment_post_id", "carnatic_comment", ["post_id"])
    op.create_index("ix_carnatic_comment_user_id", "carnatic_comment", ["user_id"])
    op.create_table(
        "carnatic_review",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("reviewed_by", sa.String(), nullable=False, server_default=""),
        *_ts(),
    )
    op.create_table(
        "carnatic_device_link",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("code_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("method", sa.String(), nullable=False, server_default=""),
        sa.Column("device_name", sa.String(), nullable=False, server_default=""),
        sa.Column("user_agent", sa.String(), nullable=False, server_default=""),
        *_ts(),
    )
    op.create_index("ix_carnatic_device_link_user_id", "carnatic_device_link", ["user_id"])
    op.create_index("ix_carnatic_device_link_token_hash", "carnatic_device_link", ["token_hash"])
    op.create_index("ix_carnatic_device_link_code_hash", "carnatic_device_link", ["code_hash"])


def downgrade() -> None:
    for table in ("carnatic_device_link", "carnatic_review", "carnatic_comment", "carnatic_like",
                  "carnatic_post", "carnatic_song", "carnatic_practice_day", "carnatic_progress",
                  "carnatic_profile"):
        op.drop_table(table)
