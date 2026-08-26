"""Tools become content: the instruments' copy moves into the database.

Revision ID: a1c74e9d3b52
Revises: f04b28d9c761

The `tool` table existed, the admin could edit it, and no page on the site read
a single row of it. Six rows were seeded when the site was designed and then
left behind: all hidden, names that no longer matched the pages
("Planetary hours, right now"), one instrument that was never built
(geomantic-shield), and four that were built afterwards and never added.

Meanwhile every tool page carried its own name, subtitle, one-line description
and the whole "how it is reckoned" passage as literals in the .astro file. So
the copy for nine instruments lived in the one place she could not edit, and
the admin screen that appeared to edit it changed nothing at all.

The landing page kept a THIRD copy of the same nine — its own shorter,
punchier line per instrument, written for a stranger skimming rather than
for somebody already on the tool. That is a different job, not a
duplicate, so it becomes its own column rather than being flattened into
the summary. Two fields, one row, both hers to edit.

This makes the table the source of truth and fills it with exactly what the
pages said on the day it was written — the seed below was generated from them
rather than retyped, because retyping four hundred words of prose nine times is
how a migration quietly rewrites somebody's writing.

The literals come out of the pages in the same change.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a1c74e9d3b52"
down_revision = "f04b28d9c761"
branch_labels = None
depends_on = None


INSTRUMENTS = [
    dict(
        slug="planetary-hours", name="Planetary hours", native="",
        landing_blurb="The day divided by its own light, so an hour is only sixty minutes twice a year.",
        glyph="☉", category="Time", position=10,
        summary="The day divided by its own light: twelve hours from sunrise to sunset and twelve more from sunset to sunrise, so an hour is only sixty minutes twice a year.",
        reckoned="Sunrise to sunset is divided into twelve equal parts and sunset to the next sunrise into twelve more, so day-hours and night-hours are the same length only at the equinoxes. The first hour of the day belongs to the ruler of the weekday, and the rest follow the Chaldean order — Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon — running continuously through the night into the next dawn.",
    ),
    dict(
        slug="solar-stations", name="Solar stations", native="",
        landing_blurb="Sunrise, noon, sunset and midnight for a month ahead, exportable to your calendar.",
        glyph="☉", category="Time", position=20,
        summary="Sunrise, noon, sunset and midnight — the structural skeleton of a daily rite. The tool computes the times; which deity belongs to which station is yours to choose or ignore.",
        reckoned="",
    ),
    dict(
        slug="lunar-stations", name="Lunar stations", native="",
        landing_blurb="Moonrise, culmination, moonset and nadir — with the phase beside them.",
        glyph="☾", category="Time", position=30,
        summary="Moonrise, culmination, moonset and nadir — with the Moon's phase beside them. The Moon rises about fifty minutes later each day and skips a civil day regularly; where a station does not occur, the table says so.",
        reckoned="",
    ),
    dict(
        slug="pancanga", name="Pañcāṅga", native="पञ्चाङ्ग",
        landing_blurb="The five limbs of the day, each with the moment it ends.",
        glyph="◐", category="Calendars", position=40,
        summary="The five limbs of the day — tithi, vāra, nakṣatra, yoga and karaṇa — each with the moment it ends.",
        reckoned="The five limbs are measured from the Sun and Moon, not from a table. A tithi is the Moon gaining twelve degrees on the Sun; a nakṣatra is one of twenty-seven equal divisions of the sidereal circle; a yoga is their summed longitudes; a karaṇa is half a tithi, so two of them usually fall in one day. Only the vāra is tied to the horizon, and it begins at sunrise — which is why the sunrise rule above moves the whole day rather than one number.",
    ),
    dict(
        slug="hindu-calendar", name="Hindu calendar", native="पञ्चाङ्ग · वर्ष",
        landing_blurb="The lunisolar year, its months and its festivals — amānta or pūrṇimānta, your choice.",
        glyph="☾", category="Calendars", position=50,
        summary="The lunisolar year: its months with their Gregorian spans, the eras that count it, and the festivals each month carries.",
        reckoned="A lunar month is one lunation, and the year is twelve of them — about eleven days short of the solar year. When a lunar month contains no solar transition an intercalary month is inserted, adhika māsa, and the year runs to thirteen. The rarer opposite, kṣaya māsa, removes one. Festivals never fall in an adhika month: they wait for the nija month that follows, and that rule is authentic rather than a simplification.",
    ),
    dict(
        slug="attic-calendar", name="Attic calendar", native="Ἀττικός",
        landing_blurb="The month of Athens, opened at the noumenia and counted backwards through its last third.",
        glyph="☽", category="Calendars", position=60,
        summary="The lunisolar month of Athens, kept current: opened at the noumenia, running full or hollow, and counted backwards through its last third.",
        reckoned="A month opens at the noumenia and runs thirty days (full) or twenty-nine (hollow), which emerges from where the next conjunction falls rather than from a table. The first two thirds count forward; the last counts backwards by how many days remain, and the final day — ἕνη καὶ νέα, 'old and new' — belongs to both months at once. Twelve such months fall about eleven days short of the solar year, so a thirteenth is inserted seven times in nineteen, after Poseideon.",
    ),
    dict(
        slug="natal-chart", name="Natal chart", native="",
        landing_blurb="A figure for a moment and a place, Hellenistic or Vedic — and honest about an unknown birth time.",
        glyph="✶", category="Figures", position=70,
        summary="A figure for a moment and a place. The tables are the reading; the wheel is drawn from the same numbers.",
        reckoned="Positions come from Swiss Ephemeris and are shown as computed, not rounded first and not interpreted. Which zodiac they are read against, and which houses they are placed in, is the choice above — the two traditions sit about twenty-four degrees apart, which is enough to move the Sun a whole sign for the same birth.",
    ),
    dict(
        slug="sigil-generator", name="Sigil generator", native="",
        landing_blurb="Intent reduced and drawn, every step shown. Also on your machine only.",
        glyph="●", category="Figures", position=80,
        summary="Intent, reduced and drawn. Every step of the reduction is shown, and the figure is the same every time for the same letters.",
        reckoned="A statement of intent is put into capitals, stripped to letters, then reduced — vowels struck unless you keep them, then repeats struck — leaving a set of letters. Each letter has a fixed position on a circle, and the figure is the path through them in order, marked at its start and crossed at its end. Because the positions are fixed, the same letters always give the same figure.",
    ),
    dict(
        slug="isopsephy", name="Isopsephy", native="Ἰσοψηφία",
        landing_blurb="Letter-reckoning in six scripts. Runs on your machine; nothing typed leaves it.",
        glyph="Σ", category="Letters", position=90,
        summary="Letter-reckoning in six scripts, each by its own table. Matches are only ever found inside one system.",
        reckoned="Each script is summed under its own table and nothing is converted between them. Greek keeps the numeral-only letters — digamma 6, koppa 90, sampi 900 — because omitting them silently produces wrong sums for many words. Hebrew finals take ordinary values. Arabic uses abjad order, which is not alphabet order. Coptic follows the Greek scheme plus soou, fai and shai; the demotic-derived letters carry no value, which is a fact about the system rather than an omission.",
    ),
]


def upgrade() -> None:
    op.add_column("tool", sa.Column("glyph", sa.String(), nullable=False, server_default="✶"))
    op.add_column("tool", sa.Column("native", sa.String(), nullable=False, server_default=""))
    op.add_column("tool", sa.Column("category", sa.String(), nullable=False, server_default=""))
    op.add_column("tool", sa.Column("reckoned", sa.Text(), nullable=False, server_default=""))
    op.add_column("tool", sa.Column("landing_blurb", sa.String(), nullable=False, server_default=""))

    tool = sa.table(
        "tool",
        sa.column("slug", sa.String), sa.column("name", sa.String),
        sa.column("native", sa.String), sa.column("glyph", sa.String),
        sa.column("category", sa.String), sa.column("summary", sa.String),
        sa.column("reckoned", sa.Text), sa.column("landing_blurb", sa.String),
        sa.column("position", sa.Integer),
        sa.column("visible", sa.Boolean), sa.column("locale", sa.String),
        sa.column("body_md", sa.String),
        # TimestampMixin makes both NOT NULL with no server default, so an
        # INSERT that does not name them fails. Only new rows need them.
        sa.column("created_at", sa.DateTime), sa.column("updated_at", sa.DateTime),
    )
    conn = op.get_bind()
    existing = {r[0] for r in conn.execute(sa.select(tool.c.slug))}

    for row in INSTRUMENTS:
        values = dict(row, visible=True)
        slug = values.pop("slug")
        if slug in existing:
            conn.execute(tool.update().where(tool.c.slug == slug).values(**values))
        else:
            conn.execute(tool.insert().values(
                slug=slug, locale="en", body_md="",
                created_at=sa.func.now(), updated_at=sa.func.now(), **values))

    # Designed, never built. Left in place rather than deleted — it is a record
    # of an intention — but hidden, because a visible row with no page behind it
    # puts a link on /tools that 404s.
    conn.execute(
        tool.update().where(tool.c.slug == "geomantic-shield").values(visible=False)
    )


def downgrade() -> None:
    op.drop_column("tool", "landing_blurb")
    op.drop_column("tool", "reckoned")
    op.drop_column("tool", "category")
    op.drop_column("tool", "native")
    op.drop_column("tool", "glyph")
