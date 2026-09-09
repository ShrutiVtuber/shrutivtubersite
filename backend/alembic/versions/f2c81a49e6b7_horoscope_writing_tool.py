# SPDX-License-Identifier: AGPL-3.0-only
"""The horoscope writing desk becomes an instrument.

A tool's name, summary, glyph and the passage explaining how it is reckoned
live in its `tool` row — ToolLayout reads them from there, which is why the
page carries no title of its own and why she can edit all of it in the admin
like every other instrument.

Seeded by a migration rather than by a script somebody runs, because that is
how a fresh install gets its rows. A standalone script is one more thing to
remember, and forgetting it leaves a page headed by its own slug with no
description at all.

Revision ID: f2c81a49e6b7
Revises: e9b3c05a7d14
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "f2c81a49e6b7"
down_revision = "e9b3c05a7d14"
branch_labels = None
depends_on = None

SLUG = "horoscope-writing"

SUMMARY = (
    "The sky for a period, rotated to a sign, with the events that fall "
    "inside it — and somewhere to write. For practice; the readings on this "
    "site stay hers."
)

RECKONED = (
    "Nothing here is computed about your words. The sky is: the wheel is the "
    "chart for the first day of the period, whole sign, rotated so the sign "
    "you are writing for begins it — the same rotation the published readings "
    "use. The list beside it is every ingress, station, lunation and eclipse "
    "inside the period, from the same ephemeris the rest of the site uses.\n\n"
    "A quiet period is a real answer. When nothing ingresses or stations, the "
    "list says so rather than reaching further out for something to put in it."
)


def upgrade() -> None:
    # Guarded, so running it against a database that already has the row —
    # one seeded by hand while the page was being built — is not an error.
    op.get_bind().execute(
        text(
            """
            INSERT INTO tool
              (slug, name, summary, body_md, locale, glyph, native, category,
               reckoned, landing_blurb, faq_md,
               position, visible, created_at, updated_at)
            VALUES
              (:slug, :name, :summary, '', :locale, :glyph, '', :category,
               :reckoned, '', '',
               :position, TRUE, NOW(), NOW())
            ON CONFLICT (slug) DO NOTHING
            """
        ),
        {
            "slug": SLUG,
            "name": "Write a horoscope",
            "summary": SUMMARY,
            "glyph": "✍",
            # Its own group: everything else here answers a question, and this
            # one hands you the material and waits.
            "category": "Writing",
            "reckoned": RECKONED,
            # After the figures and the letters — it is the one reached for
            # once the rest can already be read.
            "position": 100,
            # ⚠ Every NOT NULL column is named, not only the interesting ones.
            # `locale`, `landing_blurb` and `faq_md` are not on the model's
            # face and have no defaults, and the insert failed on `locale`
            # alone — a NotNullViolation is the loudest of the failures this
            # table can give, which is the only good thing about it.
            "locale": "en",
        },
    )


def downgrade() -> None:
    op.get_bind().execute(
        text("DELETE FROM tool WHERE slug = :slug"), {"slug": SLUG}
    )
