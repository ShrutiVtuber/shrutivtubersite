# SPDX-License-Identifier: AGPL-3.0-only
"""
Register the horoscope writing desk as an instrument.

A tool's card, name, summary and the passage explaining how it is reckoned all
live in the `tool` row — ToolLayout reads them from there, so the page carries
no title of its own. That is deliberate: a prop would be a second place to
write the same words, and this way she edits them in the admin like every
other instrument.

Idempotent. Run it again after a deploy and it updates the row rather than
refusing or duplicating.

    docker compose exec -T backend python scripts/seed_horoscope_tool.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select                                    # noqa: E402
from shruti.core.db import SessionLocal                          # noqa: E402
from shruti.models import Tool                                   # noqa: E402

SLUG = "horoscope-writing"

FIELDS = dict(
    name="Write a horoscope",
    summary=(
        "The sky for a period, rotated to a sign, with the events that fall "
        "inside it — and somewhere to write. For practice; the readings on "
        "this site stay hers."
    ),
    glyph="✍",
    # Its own group. It is not a calculator: everything else here answers a
    # question, and this one hands you the material and waits.
    category="Writing",
    # After the figures and the letters, because it is the one you reach for
    # once you can already read the rest.
    position=100,
    visible=True,
    reckoned=(
        "Nothing here is computed about your words. The sky is: the wheel is "
        "the chart for the first day of the period, whole sign, rotated so "
        "the sign you are writing for begins it — the same rotation the "
        "published readings use. The list beside it is every ingress, "
        "station, lunation and eclipse inside the period, from the same "
        "ephemeris the rest of the site uses.\n\n"
        "A quiet period is a real answer. When nothing ingresses or stations, "
        "the list says so rather than reaching further out for something to "
        "put in it."
    ),
)


async def main() -> int:
    async with SessionLocal() as session:
        row = (
            await session.execute(select(Tool).where(Tool.slug == SLUG))
        ).scalar_one_or_none()

        if row is None:
            session.add(Tool(slug=SLUG, **FIELDS))
            what = "added"
        else:
            # Only what the template offers. Anything she has rewritten in the
            # admin is hers, and this must not walk over it — so a field is
            # updated only while it still matches what was seeded.
            for key, value in FIELDS.items():
                if getattr(row, key) in ("", None):
                    setattr(row, key, value)
            what = "already there; filled any blanks"

        await session.commit()
    print(f"{SLUG}: {what}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
