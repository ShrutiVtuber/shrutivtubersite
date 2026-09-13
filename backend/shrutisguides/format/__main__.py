# SPDX-License-Identifier: AGPL-3.0-only
"""
    python -m shrutisguides.format validate GUIDE.json [more...]
    python -m shrutisguides.format import-markdown SPEC.md --out GUIDE.json

Exit status is the number of guides with problems, so CI can run it on every
example and fail on any.
"""
from __future__ import annotations

import sys

from . import import_markdown as importer
from .validate import validate_file


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    command, rest = argv[0], argv[1:]
    if command == "validate":
        bad = 0
        for path in rest:
            problems = validate_file(path)
            if problems:
                bad += 1
                print(f"{path}: {len(problems)} problem(s)")
                for p in problems:
                    print(f"  {p}")
            else:
                print(f"{path}: ok")
        return bad
    if command == "import-markdown":
        return importer.main(rest)
    print(f"unknown command {command!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
