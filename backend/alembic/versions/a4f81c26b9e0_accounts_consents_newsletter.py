"""Accounts, consents, nativities, subscribers, horoscopes, issues

Three tables here are shaped by law rather than by preference.

consent_record is APPEND-ONLY and stores the WORDING, not a reference to it.
Withdrawing writes a new row rather than editing the old one, because the
question the law asks is "what did they agree to, and when", and an overwritten
row cannot answer it. Storing the text verbatim means that if the form's
wording changes next year, the record still says what this person actually
read.

nativity.birth_time is nullable on purpose. "I don't know my birth time" is a
first-class choice, not a validation failure.

subscriber carries confirm and unsubscribe tokens so that double opt-in works
and unsubscribe needs no login — one click, per the design.

Revision ID: a4f81c26b9e0
Revises: 9c3e7b15a4d2
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a4f81c26b9e0"
down_revision: Union[str, None] = "9c3e7b15a4d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TS = dict(server_default=sa.func.now(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "site_user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=False, server_default=""),
        sa.Column("timezone", sa.String(), nullable=False, server_default=""),
        sa.Column("reading_language", sa.String(), nullable=False, server_default="en"),
        sa.Column("preferred_tradition", sa.String(), nullable=False, server_default=""),
        sa.Column("house_system", sa.String(), nullable=False, server_default=""),
        sa.Column("ayanamsa", sa.String(), nullable=False, server_default=""),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    op.create_index("ix_site_user_email", "site_user", ["email"])

    op.create_table(
        "consent_record",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("version", sa.String(), nullable=False, server_default=""),
        sa.Column("wording", sa.Text(), nullable=False, server_default=""),
        sa.Column("lawful_basis", sa.String(), nullable=False, server_default=""),
        sa.Column("source", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    op.create_index("ix_consent_record_email", "consent_record", ["email"])
    op.create_index("ix_consent_record_kind", "consent_record", ["kind"])
    op.create_index("ix_consent_record_user_id", "consent_record", ["user_id"])

    op.create_table(
        "nativity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("birth_date", sa.String(), nullable=False),
        sa.Column("birth_time", sa.String(), nullable=True),
        sa.Column("time_unknown", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("place_name", sa.String(), nullable=False, server_default=""),
        sa.Column("lat", sa.Float(), nullable=False, server_default="0"),
        sa.Column("lon", sa.Float(), nullable=False, server_default="0"),
        sa.Column("elevation", sa.Float(), nullable=False, server_default="0"),
        sa.Column("timezone", sa.String(), nullable=False, server_default=""),
        sa.Column("utc_offset_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    op.create_index("ix_nativity_user_id", "nativity", ["user_id"])

    op.create_table(
        "subscriber",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_until", sa.String(), nullable=True),
        sa.Column("wants_horoscope", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_videos", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_streams", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("wants_articles", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("cadence", sa.String(), nullable=False, server_default="monthly"),
        sa.Column("confirm_token", sa.String(), nullable=False, server_default=""),
        sa.Column("unsubscribe_token", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    for col in ("email", "user_id", "confirm_token", "unsubscribe_token"):
        op.create_index(f"ix_subscriber_{col}", "subscriber", [col])

    op.create_table(
        "horoscope",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sign", sa.String(), nullable=False),
        sa.Column("period", sa.String(), nullable=False, server_default="monthly"),
        sa.Column("covers", sa.String(), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    for col in ("sign", "period", "covers"):
        op.create_index(f"ix_horoscope_{col}", "horoscope", [col])
    op.create_unique_constraint("uq_horoscope_slot", "horoscope", ["sign", "period", "covers"])

    op.create_table(
        "issue",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("subject", sa.String(), nullable=False, server_default=""),
        sa.Column("letter_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), **TS),
        sa.Column("updated_at", sa.DateTime(timezone=True), **TS),
    )
    op.create_index("ix_issue_slug", "issue", ["slug"])


def downgrade() -> None:
    for table in ("issue", "horoscope", "subscriber", "nativity", "consent_record", "site_user"):
        op.drop_table(table)
