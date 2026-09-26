"""Swara Studio v2: the course, recordings, per-person practice, and rooms on the practice model

Revision ID: r6q2m9n5o521
Revises: q5o1l8m4n410

The course (units, lessons and their revisions, exercises, glossary) and
the recordings registry are imported from the private course repository
and edited in the Swara Studio admin; each row remembers the file version
it was last in step with, so an import never overwrites Sophia's edits.

Per person: lesson state, attempts, bests, review cards and raga guesses,
all theirs alone (ON DELETE CASCADE, NOBODYS_BUT_THEIRS).

The practice model is generalised (LISTENING.md §4d option 2): a `room`
and `subject` on practice_work ('horoscope' for everything that exists),
a practice_part table for the parts of a Carnatic piece or analysis, and
practice_rubric for rubric answers (kept without a name, like comments).
Practice works are already kept anonymised when an account goes, which
is Sophia's rule for pieces and analyses too.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "r6q2m9n5o521"
down_revision = "q5o1l8m4n410"
branch_labels = None
depends_on = None

NOBODYS_BUT_THEIRS = [
    ("carnatic_lesson_state", "user_id"),
    ("carnatic_attempt", "user_id"),
    ("carnatic_best", "user_id"),
    ("carnatic_card", "user_id"),
    ("carnatic_guess", "user_id"),
]
# Kept without a name when the account goes.
KEPT_WITHOUT_A_NAME = [
    ("practice_rubric", "user_id", "site_user.id", "SET NULL", True),
    ("carnatic_recording", "suggested_by", "site_user.id", "SET NULL", True),
]


def _ts():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]


def _j(name, default="{}", nullable=False):
    return sa.Column(name, JSONB(), nullable=nullable, server_default=None if nullable else default)


def _user(ondelete="CASCADE", nullable=False):
    return sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id", ondelete=ondelete), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "carnatic_unit",
        sa.Column("n", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("level", sa.String(), nullable=False, server_default=""),
        sa.Column("intro", sa.String(), nullable=False, server_default=""),
        _j("lessons", "[]"),
        *_ts(),
    )
    op.create_table(
        "carnatic_lesson",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("lang", sa.String(), primary_key=True, server_default="en"),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("unit", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        _j("front"),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("base_hash", sa.String(), nullable=False, server_default=""),
        sa.Column("admin_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("edited_by", sa.String(), nullable=False, server_default=""),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("file_hash", sa.String(), nullable=False, server_default=""),
        _j("file_front", nullable=True),
        sa.Column("file_body", sa.Text(), nullable=True),
        sa.Column("file_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
        sa.UniqueConstraint("slug", "lang", name="uq_carnatic_lesson_slug"),
    )
    op.create_index("ix_carnatic_lesson_slug", "carnatic_lesson", ["slug"])
    op.create_index("ix_carnatic_lesson_unit", "carnatic_lesson", ["unit"])
    op.create_index("ix_carnatic_lesson_status", "carnatic_lesson", ["status"])
    op.create_table(
        "carnatic_lesson_revision",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("lang", sa.String(), nullable=False, server_default="en"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        _j("front"),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(), nullable=False, server_default="admin"),
        sa.Column("by", sa.String(), nullable=False, server_default=""),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("meaning_change", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("ix_carnatic_lesson_revision_lesson_id", "carnatic_lesson_revision", ["lesson_id"])
    op.create_table(
        "carnatic_exercise",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("unit", sa.Integer(), nullable=False),
        sa.Column("lesson", sa.String(), nullable=False, server_default=""),
        sa.Column("kind", sa.String(), nullable=False, server_default="quiz"),
        _j("data"),
        sa.Column("base_hash", sa.String(), nullable=False, server_default=""),
        sa.Column("admin_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("file_hash", sa.String(), nullable=False, server_default=""),
        _j("file_data", nullable=True),
        *_ts(),
    )
    for col in ("unit", "lesson", "kind"):
        op.create_index(f"ix_carnatic_exercise_{col}", "carnatic_exercise", [col])
    op.create_table(
        "carnatic_glossary",
        sa.Column("slug", sa.String(), primary_key=True),
        sa.Column("term", sa.String(), nullable=False, server_default=""),
        sa.Column("definition", sa.String(), nullable=False, server_default=""),
        sa.Column("lesson", sa.String(), nullable=False, server_default=""),
        _j("aliases", "[]"),
        sa.Column("base_hash", sa.String(), nullable=False, server_default=""),
        sa.Column("admin_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("file_hash", sa.String(), nullable=False, server_default=""),
        _j("file_data", nullable=True),
        *_ts(),
    )
    op.create_table(
        "carnatic_recording",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False, server_default="candidate"),
        *[sa.Column(c, sa.String(), nullable=False, server_default="")
          for c in ("provider", "url", "title", "channel", "uploader_kind", "instrument", "composition",
                    "composer", "form", "raga", "tala", "listen_for", "duration", "reason", "base_hash")],
        _j("artists", "[]"), _j("page_says"), _j("flags", "[]"), _j("raw"),
        _j("clips", "[]"), _j("sections", "[]"), _j("beat_map", nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("oembed_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("suggested_by", sa.Integer(), sa.ForeignKey("site_user.id", ondelete="SET NULL"), nullable=True),
        _j("suggestion", nullable=True),
        sa.Column("admin_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_ts(),
    )
    for col in ("status", "form", "raga", "suggested_by"):
        op.create_index(f"ix_carnatic_recording_{col}", "carnatic_recording", [col])
    op.create_table(
        "carnatic_raga_flag",
        sa.Column("raga", sa.String(), primary_key=True),
        sa.Column("synth_ok", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        *_ts(),
    )
    # The ragas EAR_TRAINING.md §3 drills only from recordings.
    op.execute(
        "INSERT INTO carnatic_raga_flag (raga, synth_ok, note) VALUES "
        + ", ".join(f"('{r}', false, 'EAR_TRAINING.md §3')" for r in (
            "todi", "sahana", "begada", "anandabhairavi", "varali", "saveri", "kanada", "atana"))
    )

    op.create_table(
        "carnatic_lesson_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        _j("position", nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_carnatic_lesson_state"),
    )
    op.create_table(
        "carnatic_attempt",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("seconds", sa.Integer(), nullable=False, server_default="0"),
        _j("result"),
        sa.UniqueConstraint("user_id", "client_id", name="uq_carnatic_attempt_client"),
    )
    op.create_table(
        "carnatic_best",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("skill", sa.String(), nullable=False, server_default=""),
        _j("best"), _j("previous", nullable=True),
        sa.Column("achieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "item_id", "skill", name="uq_carnatic_best"),
    )
    op.create_table(
        "carnatic_card",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("box", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_due", sa.DateTime(timezone=True), nullable=True),
        _j("recent", "[]"),
        sa.UniqueConstraint("user_id", "key", name="uq_carnatic_card"),
    )
    op.create_table(
        "carnatic_guess",
        sa.Column("id", sa.Integer(), primary_key=True),
        _user(),
        sa.Column("recording_id", sa.String(), nullable=False),
        sa.Column("guess", sa.String(), nullable=False, server_default=""),
        sa.Column("confidence", sa.String(), nullable=False, server_default=""),
        sa.Column("phrases", sa.String(), nullable=False, server_default=""),
        sa.Column("right", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
    )
    for table in ("carnatic_lesson_state", "carnatic_attempt", "carnatic_best", "carnatic_card", "carnatic_guess"):
        op.create_index(f"ix_{table}_user_id", table, ["user_id"])
    op.create_index("ix_carnatic_attempt_item_id", "carnatic_attempt", ["item_id"])
    op.create_index("ix_carnatic_attempt_kind", "carnatic_attempt", ["kind"])
    op.create_index("ix_carnatic_card_next_due", "carnatic_card", ["next_due"])
    op.create_index("ix_carnatic_guess_recording_id", "carnatic_guess", ["recording_id"])
    op.create_index("ix_carnatic_lesson_state_lesson_id", "carnatic_lesson_state", ["lesson_id"])

    # The practice model, generalised.
    op.add_column("practice_work", sa.Column("room", sa.String(), nullable=False, server_default="horoscope"))
    op.add_column("practice_work", sa.Column("subject", sa.String(), nullable=False, server_default=""))
    op.create_index("ix_practice_work_room", "practice_work", ["room"])
    op.create_index("ix_practice_work_subject", "practice_work", ["subject"])
    op.create_table(
        "practice_part",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(), sa.ForeignKey("practice_work.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        _j("data"),
    )
    op.create_index("ix_practice_part_work_id", "practice_part", ["work_id"])
    op.create_index("ix_practice_part_key", "practice_part", ["key"])
    op.create_table(
        "practice_rubric",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(), sa.ForeignKey("practice_work.id", ondelete="CASCADE"), nullable=False),
        _user("SET NULL", True),
        _j("answers"),
        *_ts(),
        sa.UniqueConstraint("work_id", "user_id", name="uq_practice_rubric"),
    )
    op.create_index("ix_practice_rubric_work_id", "practice_rubric", ["work_id"])
    op.create_index("ix_practice_rubric_user_id", "practice_rubric", ["user_id"])


def downgrade() -> None:
    op.drop_table("practice_rubric")
    op.drop_table("practice_part")
    op.execute("DELETE FROM practice_work WHERE room <> 'horoscope'")
    op.drop_index("ix_practice_work_subject", "practice_work")
    op.drop_index("ix_practice_work_room", "practice_work")
    op.drop_column("practice_work", "subject")
    op.drop_column("practice_work", "room")
    for table in ("carnatic_guess", "carnatic_card", "carnatic_best", "carnatic_attempt", "carnatic_lesson_state",
                  "carnatic_raga_flag", "carnatic_recording", "carnatic_glossary", "carnatic_exercise",
                  "carnatic_lesson_revision", "carnatic_lesson", "carnatic_unit"):
        op.drop_table(table)
