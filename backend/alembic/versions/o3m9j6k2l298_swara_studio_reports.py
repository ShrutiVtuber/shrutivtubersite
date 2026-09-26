"""Swara Studio: members can report a Listen post or comment

Revision ID: o3m9j6k2l298
Revises: n2l8i5j1k187

The app posts to Listen as the website does, so both need the same way to
flag something for the operator. A report hides nothing on its own: the
review queue's Moderation tab lists reported items first and hiding stays
her decision.

⚠ A report is the reporter's row: its foreign key to site_user is ON DELETE
CASCADE and named in `NOBODYS_BUT_THEIRS`, which
`test_an_account_can_be_deleted` reads. It also cascades from the post or
comment it is about.
"""
from alembic import op
import sqlalchemy as sa

revision = "o3m9j6k2l298"
down_revision = "n2l8i5j1k187"
branch_labels = None
depends_on = None

# Foreign keys to site_user this revision creates, all ON DELETE CASCADE.
NOBODYS_BUT_THEIRS = [
    ("carnatic_report", "user_id"),
]


def upgrade() -> None:
    op.create_table(
        "carnatic_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("carnatic_post.id", ondelete="CASCADE"), nullable=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("carnatic_comment.id", ondelete="CASCADE"), nullable=True),
        sa.Column("reason", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "post_id", name="uq_carnatic_report_post"),
        sa.UniqueConstraint("user_id", "comment_id", name="uq_carnatic_report_comment"),
        sa.CheckConstraint("(post_id IS NULL) <> (comment_id IS NULL)", name="ck_carnatic_report_one_thing"),
    )
    op.create_index("ix_carnatic_report_user_id", "carnatic_report", ["user_id"])
    op.create_index("ix_carnatic_report_post_id", "carnatic_report", ["post_id"])
    op.create_index("ix_carnatic_report_comment_id", "carnatic_report", ["comment_id"])


def downgrade() -> None:
    op.drop_table("carnatic_report")
