"""Swara Studio: a deleted account's posts, likes, reports, practice and songs are kept without a name; reports hide

Revision ID: p4n0k7l3m309
Revises: o3m9j6k2l298

The owner's rule of 26 Sep 2026: when an account is deleted, what others
see or count in the school is anonymised, not deleted. Listen posts,
comments, likes, reports and the practice log lose their person (user_id
NULL, ON DELETE SET NULL) and say when (`author_deleted_at` where a name
would be shown). Songs are the person's choice when they delete: kept,
credited to nobody, or deleted (`accounts._carnatic_leave`).

A like was keyed by (post, person); with no person it needs its own id.

Moderation: three reports from different accounts hide a post or comment
until she reviews it (`hidden_by = 'reports'`); restoring it sets
`reviewed_at`, and only reports made after that count again. Comments gain
the `hidden_by` posts already had.
"""
from alembic import op
import sqlalchemy as sa

revision = "p4n0k7l3m309"
down_revision = "o3m9j6k2l298"
branch_labels = None
depends_on = None

# Foreign keys to site_user this revision turns from CASCADE into SET NULL:
# (table, column, target, ondelete, nullable), as k9i6f2g7h854 lists its own.
KEPT_WITHOUT_A_NAME = [
    ("carnatic_post", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_comment", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_like", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_report", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_practice_day", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_song", "user_id", "site_user.id", "SET NULL", True),
]
ANONYMISED = ["carnatic_post", "carnatic_comment", "carnatic_song"]


def _ts(name: str) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=True)


def _relink(table: str, ondelete: str, nullable: bool) -> None:
    op.drop_constraint(f"{table}_user_id_fkey", table, type_="foreignkey")
    op.alter_column(table, "user_id", existing_type=sa.Integer(), nullable=nullable)
    op.create_foreign_key(f"{table}_user_id_fkey", table, "site_user", ["user_id"], ["id"], ondelete=ondelete)


def upgrade() -> None:
    # A like with no person needs a key of its own.
    op.drop_constraint("carnatic_like_pkey", "carnatic_like", type_="primary")
    op.add_column("carnatic_like", sa.Column("id", sa.Integer(), sa.Identity(), nullable=False))
    op.create_primary_key("carnatic_like_pkey", "carnatic_like", ["id"])
    op.create_unique_constraint("uq_carnatic_like", "carnatic_like", ["post_id", "user_id"])
    op.create_index("ix_carnatic_like_post_id", "carnatic_like", ["post_id"])
    op.create_index("ix_carnatic_like_user_id", "carnatic_like", ["user_id"])

    for table, _col, _target, ondelete, nullable in KEPT_WITHOUT_A_NAME:
        _relink(table, ondelete, nullable)
    for table in ANONYMISED:
        op.add_column(table, _ts("author_deleted_at"))

    op.add_column("carnatic_post", _ts("reviewed_at"))
    op.add_column("carnatic_comment", _ts("reviewed_at"))
    op.add_column("carnatic_comment", sa.Column("hidden_by", sa.String(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("carnatic_comment", "hidden_by")
    op.drop_column("carnatic_comment", "reviewed_at")
    op.drop_column("carnatic_post", "reviewed_at")
    for table in ANONYMISED:
        op.drop_column(table, "author_deleted_at")
    # Rows with no person cannot go back under NOT NULL: they are removed.
    for table, *_rest in KEPT_WITHOUT_A_NAME:
        op.execute(f"DELETE FROM {table} WHERE user_id IS NULL")
        _relink(table, "CASCADE", False)
    op.drop_index("ix_carnatic_like_user_id", "carnatic_like")
    op.drop_index("ix_carnatic_like_post_id", "carnatic_like")
    op.drop_constraint("uq_carnatic_like", "carnatic_like", type_="unique")
    op.drop_constraint("carnatic_like_pkey", "carnatic_like", type_="primary")
    op.drop_column("carnatic_like", "id")
    op.create_primary_key("carnatic_like_pkey", "carnatic_like", ["post_id", "user_id"])
