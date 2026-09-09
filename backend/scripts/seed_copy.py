# SPDX-License-Identifier: AGPL-3.0-only
"""
Register template strings with the admin, straight against the database.

`/api/admin/copy/seed` does this over HTTP and needs an admin session — which
means a password, which means whoever runs a deploy has to hold one. Reading
the templates needs no authority at all, so the extraction happens with
`node scripts/seed-copy.mjs --json` and the result is applied here, on the
machine that already owns the database.

The rules are the endpoint's, and the important one is that **a value she has
written is never touched**:

  * a key that does not exist is inserted, seeded WITH its default as the
    value, so the panel shows the words that are on the site rather than an
    empty box she has to fill before the page reads right;
  * a row still holding exactly its old default is following the template, so
    when the template changes the value follows. Without this, editing a line
    in a template silently does nothing — the row seeded with the old words
    wins and nothing says why;
  * the moment the two differ she has edited it, and this stops touching it.

Usage, from the repo root on the server:

    node scripts/seed-copy.mjs --json | \\
      docker compose exec -T backend python scripts/seed_copy.py

Safe to run repeatedly: the same templates seeded twice are the same rows.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select                                    # noqa: E402
from shruti.core.db import SessionLocal                          # noqa: E402
from shruti.models import Copy                                   # noqa: E402


async def main() -> int:
    payload = json.load(sys.stdin)

    pages = added = updated = seen = 0
    async with SessionLocal() as session:
        for entry in payload:
            page = entry["page"]
            items = entry["items"]
            if not items:
                continue
            pages += 1
            seen += len(items)

            known = {
                r.key: r
                for r in (
                    await session.execute(select(Copy).where(Copy.page == page))
                ).scalars().all()
            }

            for item in items:
                row = known.get(item["key"])
                if row is None:
                    session.add(Copy(
                        page=page, key=item["key"], label=item["label"],
                        value=item["default"], default_value=item["default"],
                        position=item["position"], multiline=item["multiline"],
                    ))
                    added += 1
                    continue

                if row.value == row.default_value and row.value != item["default"]:
                    row.value = item["default"]
                    updated += 1

                row.label = item["label"] or row.label
                row.default_value = item["default"]
                row.position = item["position"]
                row.multiline = item["multiline"]

        await session.commit()

    print(f"{pages} pages, {seen} strings, {added} newly registered, "
          f"{updated} tracking a changed template")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
