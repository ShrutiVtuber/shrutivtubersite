"""Everyone who already has an account keeps it

⚠ **This migration exists to stop a feature locking people out.** Confirming
an address is now required before an account works — but every account made
before today was made under a rule that did not ask for it, and three of them
have `email_verified_at` NULL. Enforcing the new rule without this would refuse
them all, including the App Store reviewer's demo account, which is a rejection
on the first morning.

So: everyone here already is treated as confirmed, and the rule applies from
here on. That is the honest reading. They were not asked, so they cannot be
held to it.

⚠ No schema change. `email_verified_at` has existed since the accounts were
built and was already set by the password-reset and sign-in-link flows — the
column was there, the enforcement was not. A half-built feature made of working
halves, which is the shape this project has been bitten by before.

Revision ID: b2e57f91c4a6
Revises: a9d41c72e8b3
"""
from alembic import op
import sqlalchemy as sa

revision = "b2e57f91c4a6"
down_revision = "a9d41c72e8b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ⚠ now(), not a fixed timestamp: the value means "confirmed at", and the
    # honest answer for a grandfathered account is when it was grandfathered.
    op.execute(
        "UPDATE site_user SET email_verified_at = now() "
        "WHERE email_verified_at IS NULL"
    )


def downgrade() -> None:
    # ⚠ Deliberately nothing. Un-confirming addresses would lock out everybody
    # who has confirmed since, and there is no record of which were which. A
    # downgrade that loses people is worse than one that does nothing.
    pass
