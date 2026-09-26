"""Swara Studio: a published song sheet can be reported and moderated like a Listen post

Revision ID: q5o1l8m4n410
Revises: p4n0k7l3m309

A sheet is public at /carnatic/sheets/{slug}, so it gets what Listen has:
members report it, three reports from different accounts hide it until
Shruti reviews it (`hidden_by = 'reports'`), and she restores it (setting
`reviewed_at`, after which only new reports count) or removes it for good,
whatever its author chose when deleting their account.

A report is about exactly one thing: a post, a comment or now a sheet.
"""
from alembic import op
import sqlalchemy as sa

revision = "q5o1l8m4n410"
down_revision = "p4n0k7l3m309"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("carnatic_song", sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("carnatic_song", sa.Column("hidden_by", sa.String(), nullable=False, server_default=""))
    op.add_column("carnatic_song", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_carnatic_song_hidden", "carnatic_song", ["hidden"])

    op.add_column("carnatic_report", sa.Column(
        "song_id", sa.Integer(), sa.ForeignKey("carnatic_song.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_carnatic_report_song_id", "carnatic_report", ["song_id"])
    op.create_unique_constraint("uq_carnatic_report_song", "carnatic_report", ["user_id", "song_id"])
    op.drop_constraint("ck_carnatic_report_one_thing", "carnatic_report", type_="check")
    op.create_check_constraint("ck_carnatic_report_one_thing", "carnatic_report",
                               "num_nonnulls(post_id, comment_id, song_id) = 1")


def downgrade() -> None:
    op.execute("DELETE FROM carnatic_report WHERE song_id IS NOT NULL")
    op.drop_constraint("ck_carnatic_report_one_thing", "carnatic_report", type_="check")
    op.create_check_constraint("ck_carnatic_report_one_thing", "carnatic_report",
                               "(post_id IS NULL) <> (comment_id IS NULL)")
    op.drop_constraint("uq_carnatic_report_song", "carnatic_report", type_="unique")
    op.drop_index("ix_carnatic_report_song_id", "carnatic_report")
    op.drop_column("carnatic_report", "song_id")
    op.drop_index("ix_carnatic_song_hidden", "carnatic_song")
    op.drop_column("carnatic_song", "reviewed_at")
    op.drop_column("carnatic_song", "hidden_by")
    op.drop_column("carnatic_song", "hidden")
