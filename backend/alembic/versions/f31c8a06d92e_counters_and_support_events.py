"""Counters, the events that fill them, and the overlay tokens that show them.

Revision ID: f31c8a06d92e
Revises: d8b3c05e7f21

The shape that matters: **events are recorded once and counters are views over
them.** A counter holds no running total, so creating one today counts what
already happened, changing its sources needs no recomputation, and a
double-delivered webhook cannot corrupt a total that does not exist.

`(source, external_id)` is unique because Stripe retries webhooks and Twitch
retries EventSub deliveries, both by design. Without it a goal bar drifts
upward every time a delivery is retried, which is the sort of wrong that looks
like generosity.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f31c8a06d92e"
down_revision = "d8b3c05e7f21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "support_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False, server_default=""),
        sa.Column("amount_minor", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("who", sa.String(), nullable=False, server_default=""),
        sa.Column("message", sa.String(), nullable=False, server_default=""),
        sa.Column("message_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("announced", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_support_event_source", "support_event", ["source"])
    op.create_index("ix_support_event_external_id", "support_event", ["external_id"])
    op.create_index("ix_support_event_occurred_at", "support_event", ["occurred_at"])
    op.create_index("ix_support_event_announced", "support_event", ["announced"])
    # The idempotency guarantee itself, and deliberately NOT a partial index.
    #
    # It began as `unique ... where external_id <> ''`, so manually recorded
    # events with no platform id could repeat. Postgres will only use a partial
    # index for ON CONFLICT if the statement repeats the predicate exactly, and
    # SQLAlchemy emits that predicate as a bound parameter, which never matches
    # a literal one. The result is not a slow path or a missed dedupe — every
    # insert fails outright.
    #
    # The fix is to remove the case that wanted a predicate: every event gets
    # an id, and one is generated for anything that arrives without. Simpler,
    # and every row is then addressable.
    op.create_index(
        "ux_support_event_source_external", "support_event",
        ["source", "external_id"], unique=True)

    op.create_table(
        "counter",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, server_default=""),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("unit", sa.String(), nullable=False, server_default="money"),
        sa.Column("target", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("sources", sa.String(), nullable=False, server_default=""),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ux_counter_slug", "counter", ["slug"], unique=True)

    op.create_table(
        "overlay_token",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("counter_id", sa.Integer(),
                  sa.ForeignKey("counter.id", ondelete="SET NULL"), nullable=True),
        sa.Column("motion", sa.String(), nullable=False, server_default="reduced"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ux_overlay_token", "overlay_token", ["token"], unique=True)
    op.create_index("ix_overlay_token_kind", "overlay_token", ["kind"])


def downgrade() -> None:
    op.drop_table("overlay_token")
    op.drop_table("counter")
    op.drop_table("support_event")
