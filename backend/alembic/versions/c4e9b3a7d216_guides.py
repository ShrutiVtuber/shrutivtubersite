"""Shruti's Guides: games, guides, their versions, votes and reports

A guide's content is one JSON document in the shared format; the site keeps
what surrounds it. Versions carry the state, so a published guide can have a
draft beside it and a sent-back draft leaves the live one alone.

⚠ JSONB, not JSON: the first JSON column in this database. JSONB is what
Postgres indexes and queries; plain JSON is stored as text and re-parsed on
every read.

⚠ Blocks are NOT here. `practice_block` is one person blocking another, and a
block is a block whatever they were reading — the guide catalogue filters by
it directly rather than growing a second table that would drift.

Revision ID: c4e9b3a7d216
Revises: b2e57f91c4a6
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c4e9b3a7d216"
down_revision = "b2e57f91c4a6"
branch_labels = None
depends_on = None


def _timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "guide_game",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("variants", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("art_media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_guide_game_slug", "guide_game", ["slug"], unique=True)

    op.create_table(
        "guide",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("guide_game.id"), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("published_version_id", sa.Integer(), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("featured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hidden_by", sa.String(), nullable=False, server_default=""),
        *_timestamps(),
    )
    op.create_index("ix_guide_game_id", "guide", ["game_id"])
    op.create_index("ix_guide_slug", "guide", ["slug"])
    op.create_index("ix_guide_created_by", "guide", ["created_by"])
    op.create_index("ix_guide_published_version_id", "guide", ["published_version_id"])
    op.create_index("ix_guide_featured", "guide", ["featured"])
    op.create_unique_constraint("uq_guide_game_slug", "guide", ["game_id", "slug"])

    op.create_table(
        "guide_version",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guide_id", sa.Integer(), sa.ForeignKey("guide.id"), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("body", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("state", sa.String(), nullable=False, server_default="draft"),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_guide_version_guide_id", "guide_version", ["guide_id"])
    op.create_index("ix_guide_version_state", "guide_version", ["state"])
    op.create_index("ix_guide_version_created_by", "guide_version", ["created_by"])
    op.create_unique_constraint("uq_guide_version_number", "guide_version", ["guide_id", "number"])

    op.create_table(
        "guide_vote",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guide_id", sa.Integer(), sa.ForeignKey("guide.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_guide_vote_guide_id", "guide_vote", ["guide_id"])
    op.create_index("ix_guide_vote_user_id", "guide_vote", ["user_id"])
    # ⚠ One vote per person per guide, in the database. Two taps on a slow
    # connection are two requests, and a check-then-insert counts both.
    op.create_unique_constraint("uq_guide_vote", "guide_vote", ["guide_id", "user_id"])

    op.create_table(
        "guide_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guide_id", sa.Integer(), sa.ForeignKey("guide.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("reason", sa.String(), nullable=False, server_default="other"),
        sa.Column("detail", sa.String(), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", sa.String(), nullable=False, server_default=""),
        *_timestamps(),
    )
    op.create_index("ix_guide_report_guide_id", "guide_report", ["guide_id"])
    op.create_index("ix_guide_report_user_id", "guide_report", ["user_id"])
    op.create_index("ix_guide_report_reason", "guide_report", ["reason"])
    # ⚠ One report per person per guide, or one determined person is a takedown.
    op.create_unique_constraint("uq_guide_report", "guide_report", ["guide_id", "user_id"])


def downgrade() -> None:
    for table in ("guide_report", "guide_vote", "guide_version", "guide", "guide_game"):
        op.drop_table(table)
