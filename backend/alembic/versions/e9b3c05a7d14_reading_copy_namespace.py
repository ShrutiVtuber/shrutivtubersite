# SPDX-License-Identifier: AGPL-3.0-only
"""The reading's words moved from a page namespace to a component one.

The reading body became a component shared by two routes — the dated,
canonical /horoscopes/<sign>/<period>/<covers> and the undated one beside it.
Its words are therefore no longer "the words on that page": editing them
changes both, which is what a `component:` namespace means and what the admin
tells her when she opens one.

Moving the rows rather than letting them re-seed keeps anything already
edited, and keeps a dead page name out of the copy list in the admin.

Revision ID: e9b3c05a7d14
Revises: c1f92a4e77b3
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "e9b3c05a7d14"
down_revision = "c1f92a4e77b3"
branch_labels = None
depends_on = None

OLD = "horoscopes/[sign]/[period]"
NEW = "component:HoroscopeReading"


def _move(src: str, dst: str) -> None:
    """
    Move every copy row from one namespace to another.

    The delete first is not tidiness. A render between deploy and migration
    seeds the destination with defaults, and the update would then collide on
    (page, key). The row being dropped is the seeded default; the one being
    moved is hers.
    """
    bind = op.get_bind()
    bind.execute(
        text(
            "DELETE FROM copy WHERE page = :dst "
            "AND key IN (SELECT key FROM copy WHERE page = :src)"
        ),
        {"src": src, "dst": dst},
    )
    bind.execute(
        text("UPDATE copy SET page = :dst WHERE page = :src"),
        {"src": src, "dst": dst},
    )


def upgrade() -> None:
    _move(OLD, NEW)


def downgrade() -> None:
    _move(NEW, OLD)
