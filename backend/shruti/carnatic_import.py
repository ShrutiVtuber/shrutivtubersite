# SPDX-License-Identifier: AGPL-3.0-only
"""Import Swara Studio's course bundle into the database.

    python -m shruti.carnatic_import /app/carnatic/course-import.json

The bundle is built from the private course repository by
scripts/carnatic/build_course.py and copied in by
scripts/sync-carnatic-course.sh. The first import creates; later imports
follow the files except where Sophia has edited a lesson, exercise or term
in the admin, which they never overwrite (core/carnatic_course.py). The
bundle file is deleted afterwards: the course text lives in the database,
not in a file left lying in a volume.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


async def main(path: str) -> int:
    from shruti.core.carnatic_course import import_bundle
    from shruti.core.db import SessionLocal

    bundle = json.loads(Path(path).read_text(encoding="utf-8"))
    async with SessionLocal() as session:
        summary = await import_bundle(session, bundle)
    print(json.dumps(summary, indent=1))
    try:
        Path(path).unlink()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        sys.exit(2)
    sys.exit(asyncio.run(main(sys.argv[1])))
