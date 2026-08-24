#!/usr/bin/env python3
"""
Furnish the pages that are still bare, with placeholders that cannot be
mistaken for facts.

**The convention is the design bundle's own.** Its imprint ships as
`[street, no.]` and `GEMI [000000000000]` — square brackets, visible, obviously
awaiting a real value. Everything seeded here uses the same convention, so
walking the site shows the shape of every block while nothing on it reads as
true.

THREE THINGS ARE STILL NOT SEEDED, and each for a reason that is not
squeamishness:

  - **Schedule entries.** A placeholder stream is a person turning up at nine
    on a Thursday for nothing. "Never fake liveness" is the brief's phrase and
    it means this.
  - **Fan works.** The design makes the artist credit the loudest text on the
    card. Inventing entries means attributing work to people who do not exist.
  - **Videos.** They are pulled from Twitch and YouTube; a seeded back
    catalogue would be a claim about what has been streamed.

Those three keep their designed empty states, which is what those states are
for.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select                                    # noqa: E402
from shruti.core.db import SessionLocal                          # noqa: E402
from shruti.models import Credit, ProfileField, Section          # noqa: E402

# The §03 field vocabulary. Values bracketed, because a birthday is a fact
# about a person and this file does not know it.
PROFILE = [
    ("Birthday", "[to be set]", 10),
    ("Height", "[to be set]", 20),
    ("Debut", "[to be set]", 30),
    ("Fan name", "[to be chosen]", 40),
    # Not bracketed: this one is stated outright in the brief and in her own
    # words, and rendering her as Greek-only is the failure the brief names.
    ("Traditions", "Hellenic · Śākta · Thelemic", 50),
    ("Oshi mark", "— (to be chosen)", 60),
    ("Stream tag", "[to be chosen]", 70),
    ("Fan-art tag", "[to be chosen]", 80),
]

CREDITS = [
    ("Illustrator", "[not yet commissioned]", "", 10),
    ("Rigger", "[not yet commissioned]", "", 20),
    ("3D model", "[planned]", "", 30),
    ("Logo", "[to be credited]", "", 40),
    ("BGM", "[to be credited]", "", 50),
]

SECTIONS = [
    ("about", "lore", 30, "Lore", """
*A separate voice from the description above, and deliberately so.*

[This block is the character's voice rather than the practitioner's — the
design keeps them visually distinct because conflating them is the failure this
page exists to avoid. Replace this with the lore in your own words; the block
above stays as the practitioner's account.]
"""),
    ("work", "what-follows", 20, "What follows", """
The next instrument is chosen on stream. What is running now is on this page;
what is being built is on the schedule.

[Replace with a note on what is being built next, or hide this block from the
admin until there is one.]
"""),
    ("press", "collaborations", 20, "Past collaborations", """
[No collaborations to list yet. This block is here so the shape of the page is
visible — hide it from the admin until there is something to put in it, or
replace this text with the first one.]
"""),
    ("contact", "response", 20, "What to expect", """
Replies come from hello@shrutivtuber.com, usually within two working days.
Business mail may take one more.

Anything sent through the form is stored before it is sent, so a failed
delivery never loses what you wrote.
"""),
    ("support", "where-it-goes", 20, "Where it goes", """
The ephemeris server, art commissions, and the hours the software takes.

[Replace with the specifics when you want to be concrete about it — a figure
or a list reads better here than a category.]
"""),
    ("guidelines", "questions", 20, "Edge cases", """
If something is not covered here, ask. The answer is usually yes, and a
question costs less than an apology.
"""),
]


async def main(force: bool) -> None:
    made = {"profile": 0, "credits": 0, "sections": 0}
    async with SessionLocal() as session:
        existing_fields = {
            f.label for f in (await session.execute(select(ProfileField))).scalars()
        }
        for label, value, position in PROFILE:
            if label in existing_fields and not force:
                continue
            session.add(ProfileField(label=label, value=value, position=position, visible=True))
            made["profile"] += 1

        existing_credits = {
            c.role for c in (await session.execute(select(Credit))).scalars()
        }
        for role, name, url, position in CREDITS:
            if role in existing_credits and not force:
                continue
            session.add(Credit(role=role, name=name, url=url, position=position, visible=True))
            made["credits"] += 1

        for page, key, position, title, body in SECTIONS:
            row = (
                await session.execute(
                    select(Section).where(Section.page == page, Section.key == key)
                )
            ).scalar_one_or_none()
            if row is not None and not force:
                continue
            if row is None:
                session.add(Section(
                    page=page, key=key, kind="prose", position=position,
                    title=title, body_md=body.strip(), visible=True,
                ))
            else:
                row.title, row.body_md = title, body.strip()
            made["sections"] += 1

        await session.commit()

    print(f"  profile fields {made['profile']}, credits {made['credits']}, "
          f"sections {made['sections']}")
    print("  Placeholders are bracketed, following the design's own imprint")
    print("  convention, so nothing on the site reads as true.")
    print("  NOT seeded: schedule, fan works, videos — faking those would be a")
    print("  claim about the world rather than about copy.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    asyncio.run(main(ap.parse_args().force))
