"""Passkeys

WebAuthn credentials, for readers and for the operator.

A passkey is a keypair held by the device or the platform keychain, so signing
in with one tells Apple or Google nothing about this site and hands this site no
third-party identity to store. On a site whose posture is minimal data sharing,
federated OAuth would have been the odd choice.

One row per credential: a person reasonably has the phone, the laptop, and a
hardware key in a drawer.

Revision ID: d3f16c8b52a4
Revises: c9a04e1b78f2
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d3f16c8b52a4"
down_revision: Union[str, None] = "c9a04e1b78f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "passkey",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("site_user.id"), nullable=True),
        sa.Column("is_operator", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("credential_id", sa.String(), nullable=False, unique=True),
        sa.Column("public_key", sa.Text(), nullable=False, server_default=""),
        sa.Column("sign_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transports", sa.String(), nullable=False, server_default=""),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_passkey_credential_id", "passkey", ["credential_id"])
    op.create_index("ix_passkey_user_id", "passkey", ["user_id"])
    op.create_index("ix_passkey_is_operator", "passkey", ["is_operator"])


def downgrade() -> None:
    op.drop_table("passkey")
