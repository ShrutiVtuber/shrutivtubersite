#!/usr/bin/env python3
"""
Seed the page sections with the design bundle's authored copy.

WHAT THIS DOES AND DOES NOT DO, because the line matters.

The design bundle's prose was written by the designer and reviewed with the
client, so reproducing it is the handoff's mandate ("copy is reproduced
verbatim — the wording is part of the design"). It goes into the database as
editable sections rather than being hard-coded into templates, so the admin can
change any of it without a deploy.

It deliberately does NOT seed:

  * profile field values — birthday, height, debut date, fan name. The bundle's
    are sample values, and the readme is explicit that no oshi mark exists and
    one must not be invented. These stay absent until supplied.
  * credits — illustrator, rigger, 3D model. Real people's names are not
    something to invent.
  * schedule entries — faking a stream is the one thing the brief calls out by
    name ("never fake liveness").

Those surfaces render their designed absent states instead, which is what the
absent states are for.

Idempotent: re-running updates the body of a section it already seeded rather
than duplicating it. A section the admin has since edited is left alone unless
--force is given.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select                                    # noqa: E402
from shruti.core.db import SessionLocal                          # noqa: E402
from shruti.models import Section                                # noqa: E402

# (page, key, kind, position, eyebrow, title, body_md)
SECTIONS: list[tuple[str, str, str, int, str, str, str]] = [
    (
        "about", "intro", "prose", 10, "About", "Shruti",
        "I stream the building of software for magickal and astrological "
        "practice — not a variety stream with an occult skin, but the actual "
        "work: ephemeris math, calendar systems, divination engines, and the "
        "unglamorous plumbing that makes a grimoire searchable.\n\n"
        "Three initiatory lineages, held at once: Hellenic theurgy under Hekate "
        "and the Attic lunisolar calendar; Śākta Tantra, initiated into the "
        "Mahāvidyā — tarpaṇam and mantra japa; and Thelema, under the O.T.O. "
        "They are not an aesthetic blend. They converge on one thing, and the "
        "software is built around it: the twilight junctures, *sandhyā* — dawn "
        "and dusk.\n\n"
        "Μιλάω αγγλικά και ελληνικά στα streams· τα σχόλια στον κώδικα είναι "
        "δίγλωσσα κι αυτά.",
    ),
    (
        "about", "two-names", "prose", 20, "", "The two names",
        "**Shruti** — Shruti Swara — is my real name, and the name everything "
        "public lives under. I am part Indian and part Greek: the Sanskrit name "
        "and the Greek theurgy are not two themes in tension — they are one "
        "person. श्रुति, *“that which is heard”*.\n\n"
        "**Soror Eu. A.** is a magickal motto, and it signs the magickal work: "
        "journal entries about practice, and the software written as practice. "
        "Two instruments, the same hand — you will find it on bylines and "
        "nowhere else.",
    ),
    (
        "work", "intro", "prose", 10, "The work",
        "A portfolio of instruments",
        "The proof behind the brand: real software for real practice. Each one "
        "is running, open where it can be, and built on stream.",
    ),
    (
        "support", "intro", "prose", 10, "Support",
        "If the work is useful to you",
        "Everything here is free to use and most of it is open source. If you "
        "want to help it keep going, there are a few ways — none of them "
        "gate anything.",
    ),
    (
        "press", "intro", "prose", 10, "Press",
        "Media kit",
        "Everything a collaborator or journalist needs, in one place. "
        "**Audience figures on this page are indicative — live numbers on "
        "request.**",
    ),
    (
        "contact", "intro", "prose", 10, "Contact",
        "Two routes",
        "Business enquiries go to one address and everything else to another, "
        "so neither buries the other.",
    ),
]


async def main(force: bool) -> None:
    created = updated = skipped = 0
    async with SessionLocal() as session:
        for page, key, kind, position, eyebrow, title, body in SECTIONS:
            row = (
                await session.execute(
                    select(Section).where(Section.page == page, Section.key == key)
                )
            ).scalar_one_or_none()

            if row is None:
                session.add(
                    Section(
                        page=page, key=key, kind=kind, position=position,
                        eyebrow=eyebrow, title=title, body_md=body,
                        # Seeded copy ships VISIBLE. The model defaults to
                        # hidden so nothing half-done goes live by accident,
                        # but this is finished, reviewed copy.
                        visible=True,
                    )
                )
                created += 1
            elif force or row.body_md == "":
                row.eyebrow, row.title, row.body_md = eyebrow, title, body
                row.kind, row.position = kind, position
                updated += 1
            else:
                skipped += 1

        await session.commit()

    print(f"  seeded: {created} created, {updated} updated, {skipped} left alone")
    if skipped and not force:
        print("  (already edited — pass --force to overwrite)")
    print("  NOT seeded, by design: profile field values, credits, schedule.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="overwrite sections that have been edited since seeding")
    asyncio.run(main(ap.parse_args().force))
