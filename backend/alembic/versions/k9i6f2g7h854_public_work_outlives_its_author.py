"""Public work outlives its author: deleting an account can finish, and what was published stays

Revision ID: k9i6f2g7h854
Revises: j8h5e1f6g743

Two things, and both are about the same button.

⚠ **Deleting an account could not finish.** Nine tables pointed at `site_user`
with no `ondelete` and `erase()` never cleared them — a passkey, a push
subscription, a saved chart, a class bought — so `DELETE FROM site_user` raised
a foreign-key error and the whole deletion rolled back. The person was told
nothing had gone wrong and nothing had gone. The rows that are nobody's but
theirs now CASCADE, so no table added later can do that silently again without
a migration saying so.

**What somebody published is kept, without their name.** A published guide,
a reading in the practice room, a comment on one, a group others joined, a
contribution to it, a shared build: other people are following these. The
author column becomes nullable and SET NULL, and `erase()` decides what is
public (kept, anonymised) and what is private (deleted) before the user row
goes. Null reads as "somebody" everywhere a name is shown.

⚠ **An anonymised row says so.** Each of those tables gains `author_deleted_at`,
set by `erase()` in the same transaction that clears the author. A null author
with no date is a bug; a null author with one is a person who left — the
distinction `ck_practice_comment_has_an_author` was written to protect, which
now counts it as the third way a comment can have an author.
"""
from alembic import op
import sqlalchemy as sa

revision = "k9i6f2g7h854"
down_revision = "j8h5e1f6g743"
branch_labels = None
depends_on = None


# (table, column, referenced table, ondelete, becomes nullable)
KEPT_WITHOUT_A_NAME = [
    ("guide", "created_by", "site_user", "SET NULL", True),
    ("guide_version", "created_by", "site_user", "SET NULL", True),
    ("guide_version", "contributed_by", "site_user", "SET NULL", False),
    ("guide_group", "created_by", "site_user", "SET NULL", True),
    ("guide_group_contribution", "user_id", "site_user", "SET NULL", True),
    ("build", "user_id", "site_user", "SET NULL", True),
    ("build", "run_id", "guide_run", "SET NULL", False),
    ("practice_work", "user_id", "site_user", "SET NULL", True),
    ("practice_comment", "user_id", "site_user", "SET NULL", False),
    ("consent_record", "user_id", "site_user", "SET NULL", False),
    ("subscriber", "user_id", "site_user", "SET NULL", False),
    ("supporter", "user_id", "site_user", "SET NULL", False),
    ("hosting", "user_id", "site_user", "SET NULL", False),
]

NOBODYS_BUT_THEIRS = [
    ("passkey", "user_id"),
    ("push_subscription", "user_id"),
    ("nativity", "user_id"),
    ("saved_chart", "user_id"),
    ("comparison", "user_id"),
    ("entitlement", "user_id"),
    ("enrolment", "user_id"),
    ("lesson_progress", "user_id"),
    ("practice_block", "user_id"),
    ("practice_block", "blocked_id"),
    ("guide_vote", "user_id"),
    ("guide_report", "user_id"),
    ("guide_group_member", "user_id"),
    ("overlay_token", "user_id"),
]


def _refk(table: str, column: str, target: str, ondelete: str | None) -> None:
    """
    Replace the one foreign key on `table.column`, whatever it was named.

    ⚠ The constraints were created inline, so their names are whatever
    Postgres chose. Asking the database beats guessing `<table>_<col>_fkey`
    and failing on the one that was named differently.
    """
    bind = op.get_bind()
    for fk in sa.inspect(bind).get_foreign_keys(table):
        if fk["constrained_columns"] == [column]:
            op.drop_constraint(fk["name"], table, type_="foreignkey")
    op.create_foreign_key(
        f"{table}_{column}_fkey", table, target, [column], ["id"], ondelete=ondelete)


ANONYMISED = sorted({t for t, *_rest in KEPT_WITHOUT_A_NAME if t in (
    "guide", "guide_version", "guide_group", "guide_group_contribution", "build",
    "practice_work", "practice_comment")})


def upgrade() -> None:
    for table in ANONYMISED:
        op.add_column(table, sa.Column("author_deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.drop_constraint("ck_practice_comment_has_an_author", "practice_comment", type_="check")
    # A row already without an author can only have lost it to a deletion
    # made under this revision and then downgraded past: mark it, or the
    # constraint below refuses the upgrade over a person who has already gone.
    for table, author in (("guide", "created_by"), ("guide_version", "created_by"),
                          ("guide_group", "created_by"), ("guide_group_contribution", "user_id"),
                          ("build", "user_id"), ("practice_work", "user_id")):
        op.execute(f"UPDATE {table} SET author_deleted_at = now() WHERE {author} IS NULL")
    op.execute("UPDATE practice_comment SET author_deleted_at = now() "
               "WHERE user_id IS NULL AND coalesce(from_discord, '') = ''")
    op.create_check_constraint(
        "ck_practice_comment_has_an_author", "practice_comment",
        "num_nonnulls(user_id, nullif(from_discord, ''), author_deleted_at) = 1")
    for table, column, target, ondelete, nullable in KEPT_WITHOUT_A_NAME:
        if nullable:
            op.alter_column(table, column, existing_type=sa.Integer(), nullable=True)
        _refk(table, column, target, ondelete)
    for table, column in NOBODYS_BUT_THEIRS:
        _refk(table, column, "site_user", "CASCADE")


def downgrade() -> None:
    """
    ⚠ Restores the constraints, and restores NOT NULL only where no row has
    lost its author. A downgrade cannot give a deleted person their name back,
    and failing halfway is worse than leaving those columns nullable.
    """
    for table, column in NOBODYS_BUT_THEIRS:
        _refk(table, column, "site_user", None)
    op.drop_constraint("ck_practice_comment_has_an_author", "practice_comment", type_="check")
    # NOT VALID: the old rule binds every new row again, and leaves alone the
    # comments whose authors have already gone — they cannot be given back.
    op.execute(
        "ALTER TABLE practice_comment ADD CONSTRAINT ck_practice_comment_has_an_author "
        "CHECK ((user_id IS NOT NULL) <> (from_discord <> '')) NOT VALID")
    for table in ANONYMISED:
        op.drop_column(table, "author_deleted_at")
    bind = op.get_bind()
    for table, column, target, _ondelete, nullable in KEPT_WITHOUT_A_NAME:
        _refk(table, column, target, None)
        if nullable:
            orphans = bind.execute(
                sa.text(f"SELECT count(*) FROM {table} WHERE {column} IS NULL")).scalar()
            if not orphans:
                op.alter_column(table, column, existing_type=sa.Integer(), nullable=False)
