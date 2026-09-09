# SPDX-License-Identifier: AGPL-3.0-only
"""The writing desk gets a typographic glyph rather than an emoji.

✍ U+270D WRITING HAND is a Dingbat with **emoji presentation by default**, so
it renders as a colour pictograph on almost every platform. Every other
instrument's mark is a monochrome symbol from Miscellaneous Symbols, Geometric
Shapes or Greek — ☉ ☰ ◈ ☾ ◐ ✶ ● Σ — and the one emoji among them looked
exactly like what it was.

☿ Mercury is the scribe's planet, sits in the same Unicode block as the moons
and the sun already in the set, and has no emoji presentation.

Revision ID: a7d3f18c2e40
Revises: f2c81a49e6b7
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "a7d3f18c2e40"
down_revision = "f2c81a49e6b7"
branch_labels = None
depends_on = None


def _set(glyph: str, previous: str) -> None:
    # Only while it is still what was seeded. If she has chosen a different
    # mark in the admin, that is her choice and this must not walk over it.
    op.get_bind().execute(
        text("UPDATE tool SET glyph = :new WHERE slug = :slug AND glyph = :old"),
        {"new": glyph, "old": previous, "slug": "horoscope-writing"},
    )


def upgrade() -> None:
    _set("☿", "✍")


def downgrade() -> None:
    _set("✍", "☿")
