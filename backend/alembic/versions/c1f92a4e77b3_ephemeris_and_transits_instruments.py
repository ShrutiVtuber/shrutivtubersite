# SPDX-License-Identifier: AGPL-3.0-only
"""two instruments: the ephemeris and transits

A tool page with no row is headed by its own slug and has no description at
all, so the row is not decoration — it is where the name, the summary and the
"how it is reckoned" passage live. `a1c74e9d3b52` made the table the source of
truth for that; this adds the two pages built since.

Both are seeded VISIBLE, because unlike the placeholders in `seed.py` these
have pages behind them today. A visible row with no page puts a card on /tools
that leads to a 404, which is the failure the tests guard against in the other
direction.

Idempotent on the slug: these rows were inserted by hand before this migration
existed, and re-running must not duplicate or overwrite the wording if it has
since been edited in the admin.

**Every not-null column without a default is supplied here.** `created_at`,
`updated_at`, `body_md`, `faq_md` and `locale` are enforced by the table and
not filled in by `bulk_insert` — the model's Python defaults never run, because
this goes to the database as SQL and never through the model at all.

That is also why the first version of this migration passed locally and failed
on production: locally both rows already existed, so the idempotence guard
skipped the insert and the insert was never actually executed. A migration
whose only test is a database that does not need it has not been tested.

Revision ID: c1f92a4e77b3
Revises: b8e4d1f70a35
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "c1f92a4e77b3"
down_revision = "b8e4d1f70a35"
branch_labels = None
depends_on = None

ROWS = [
    dict(
        slug="ephemeris",
        name="The ephemeris",
        glyph="☰",
        category="Reckonings",
        summary="A month of the sky as a table — a column per body, a row per "
                "day, the way the craft has been learned since the tables were "
                "printed.",
        landing_blurb="The sky as a table, not a wheel.",
        reckoned="Positions are computed against the Swiss Ephemeris for one "
                 "instant on each date — midnight Universal Time by default, or "
                 "noon, because printed ephemerides come both ways and the Moon "
                 "is some seven degrees apart between them. Longitude is given "
                 "in degrees and minutes of the sign. Declination is given "
                 "because longitude alone cannot show a parallel or a body out "
                 "of bounds. The day's ingresses, stations, lunations and "
                 "eclipses sit beside their row, where a printed page puts them.",
        position=25,
    ),
    dict(
        slug="events",
        name="Transits",
        glyph="◈",
        category="Reckonings",
        summary="Every ingress, station, lunation, eclipse, exact configuration "
                "and void window in a period — with the wheel, read from any of "
                "the twelve rising signs.",
        landing_blurb="Every moment in a period, read from any rising sign.",
        reckoned="Times are found by root-finding rather than by sampling, and "
                 "given to the second: an ingress at 23:47 Universal Time falls "
                 "on a different day either side of the Atlantic, so the "
                 "day-level answer can only be derived from the exact instant. "
                 "Choosing a rising sign changes one number, the whole-sign "
                 "house each event falls in — the sky itself does not move. "
                 "Signs in aversion to the rising sign are marked, since a "
                 "planet in the 2nd, 6th, 8th or 12th cannot see the Ascendant. "
                 "Void windows use the thirty-degree rule, kenodromia.",
        position=26,
    ),
]


def upgrade() -> None:
    tool = sa.table(
        "tool",
        sa.column("slug", sa.String), sa.column("name", sa.String),
        sa.column("summary", sa.String), sa.column("glyph", sa.String),
        sa.column("category", sa.String), sa.column("reckoned", sa.Text),
        sa.column("landing_blurb", sa.String), sa.column("position", sa.Integer),
        sa.column("visible", sa.Boolean), sa.column("body_md", sa.Text),
        sa.column("faq_md", sa.Text), sa.column("native", sa.String),
        sa.column("locale", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    existing = set(
        op.get_bind().execute(sa.text("SELECT slug FROM tool")).scalars().all()
    )
    now = datetime.now(timezone.utc)
    fresh = [
        dict(row, visible=True, body_md="", faq_md="", native="", locale="en",
             created_at=now, updated_at=now)
        for row in ROWS if row["slug"] not in existing
    ]
    if fresh:
        op.bulk_insert(tool, fresh)


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM tool WHERE slug IN ('ephemeris', 'events')"))
