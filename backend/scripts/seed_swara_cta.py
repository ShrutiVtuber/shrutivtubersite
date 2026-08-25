#!/usr/bin/env python3
"""
The "become a Swara" invitation on the landing page.

Seeded as an editable block rather than written into the template, because it
is the copy most likely to be tuned — an invitation is a thing you reword until
it sounds right, and needing a developer for that is how it ends up never being
reworded.

Idempotent. Leaves an edited block alone.
"""
from __future__ import annotations

import argparse
import asyncio

from sqlmodel import select

from shruti.core.db import SessionLocal
from shruti.models import Section

PAGE = "home"
KEY = "support-cta"

EYEBROW = "Swaras"
TITLE = "Become a Swara"
BODY = (
    "The streams are free and the instruments are open source, and they stay "
    "that way. Swaras are the people who keep the bench lit — the ephemeris "
    "server, the art, and the hours the software takes."
)
LINK_LABEL = "Support the work"
LINK_URL = "/support"


async def main(force: bool) -> None:
    async with SessionLocal() as session:
        row = (
            await session.execute(
                select(Section).where(Section.page == PAGE, Section.key == KEY)
            )
        ).scalar_one_or_none()

        if row is None:
            session.add(
                Section(
                    page=PAGE, key=KEY, kind="prose", position=5,
                    eyebrow=EYEBROW, title=TITLE, body_md=BODY,
                    link_label=LINK_LABEL, link_url=LINK_URL,
                    # Visible: the band draws its own default wording either
                    # way, so a hidden row would only mean the words on the
                    # page are not the words she can edit.
                    visible=True,
                )
            )
            print("  created")
        elif force or not row.body_md:
            row.eyebrow, row.title, row.body_md = EYEBROW, TITLE, BODY
            row.link_label, row.link_url = LINK_LABEL, LINK_URL
            print("  updated")
        else:
            print("  already there and edited — left alone (--force to overwrite)")

        await session.commit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    asyncio.run(main(ap.parse_args().force))
