"""Classes and workshops

A course is a class or a workshop — one table, because a workshop is a class
that happened live once. It has a date and a number of seats and is otherwise
identical, and the edited recording sold afterwards is a separate course, which
is what keeps this from needing special cases.

The load-bearing idea is that permission and progress are two tables. Access
bought with a membership ends when the membership does; access bought outright
never does; and neither has anything to do with how far somebody got. Keeping
them in one record would make "they lose the materials but not their progress"
impossible to honour.

Revision ID: b3d97f5a2e14
Revises: a17c4e8b3d92
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3d97f5a2e14"
down_revision: Union[str, None] = "a17c4e8b3d92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TS = sa.DateTime(timezone=True)


def _stamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", TS, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", TS, nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "course",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False, server_default="class"),
        sa.Column("tagline", sa.String(), nullable=False, server_default=""),
        sa.Column("body_md", sa.String(), nullable=False, server_default=""),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("tax_code", sa.String(), nullable=False, server_default="txcd_10000000"),
        sa.Column("stripe_product_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_price_id", sa.String(), nullable=False, server_default=""),
        sa.Column("starts_at", TS, nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=True),
        sa.Column("seats", sa.Integer(), nullable=True),
        sa.Column("room_name", sa.String(), nullable=False, server_default=""),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_course_slug", "course", ["slug"])
    op.create_index("ix_course_kind", "course", ["kind"])

    op.create_table(
        "course_tier",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("course.id"), nullable=False),
        sa.Column("tier_key", sa.String(), nullable=False),
        *_stamps(),
    )
    op.create_index("ix_course_tier_course_id", "course_tier", ["course_id"])
    op.create_index("ix_course_tier_tier_key", "course_tier", ["tier_key"])

    op.create_table(
        "course_module",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("course.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_course_module_course_id", "course_module", ["course_id"])

    op.create_table(
        "lesson",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("course_module.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False, server_default="video"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("body_md", sa.String(), nullable=False, server_default=""),
        sa.Column("video_provider", sa.String(), nullable=False, server_default=""),
        sa.Column("video_id", sa.String(), nullable=False, server_default=""),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("file_id", sa.Integer(), sa.ForeignKey("product_file.id"), nullable=True),
        sa.Column("free_preview", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_stamps(),
    )
    op.create_index("ix_lesson_module_id", "lesson", ["module_id"])

    op.create_table(
        "quiz_question",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lesson.id"), nullable=False),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("choices", sa.String(), nullable=False, server_default=""),
        sa.Column("answer_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("explanation", sa.String(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_quiz_question_lesson_id", "quiz_question", ["lesson_id"])

    op.create_table(
        "entitlement",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("course.id"), nullable=False),
        sa.Column("source", sa.String(), nullable=False, server_default="purchase"),
        sa.Column("tier_key", sa.String(), nullable=False, server_default=""),
        sa.Column("revoked_at", TS, nullable=True),
        *_stamps(),
    )
    op.create_index("ix_entitlement_user_id", "entitlement", ["user_id"])
    op.create_index("ix_entitlement_course_id", "entitlement", ["course_id"])
    op.create_index("ix_entitlement_source", "entitlement", ["source"])

    op.create_table(
        "enrolment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("course.id"), nullable=False),
        sa.Column("last_lesson_id", sa.Integer(), sa.ForeignKey("lesson.id"), nullable=True),
        sa.Column("completed_at", TS, nullable=True),
        *_stamps(),
    )
    op.create_index("ix_enrolment_user_id", "enrolment", ["user_id"])
    op.create_index("ix_enrolment_course_id", "enrolment", ["course_id"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lesson.id"), nullable=False),
        sa.Column("completed_at", TS, nullable=True),
        sa.Column("seconds_watched", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_lesson_progress_user_id", "lesson_progress", ["user_id"])
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])


def downgrade() -> None:
    for table in ("lesson_progress", "enrolment", "entitlement", "quiz_question",
                  "lesson", "course_module", "course_tier", "course"):
        op.drop_table(table)
