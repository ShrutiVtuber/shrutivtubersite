# SPDX-License-Identifier: AGPL-3.0-only
"""
    python -m shrutisguides.gamedata build <research dir> <database>   build the database from the packs
    python -m shrutisguides.gamedata report <database>                 what a database holds
"""
from __future__ import annotations

import sys
from pathlib import Path

from .load import build_database
from .query import GameData


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[0] == "build":
        report = build_database(Path(argv[1]), Path(argv[2]), argv[3:] or None)
        sys.stdout.write(report.text())
        return 1 if report.problems else 0
    if len(argv) == 2 and argv[0] == "report":
        data = GameData(argv[1])
        if not data.exists():
            sys.stdout.write(f"no database at {argv[1]}\n")
            return 1
        for g in data.games():
            total = sum(g["counts"].values())
            sys.stdout.write(f"{g['id']}: {g['name']} · {g['patch']} · {g['season']} · researched {g['researched_at']} · {total} records\n")
            for kind, n in sorted(g["counts"].items()):
                sys.stdout.write(f"  {kind:<15} {n:>6}\n")
            if g["problems"]:
                sys.stdout.write(f"  problems noted at load: {len(g['problems'])}\n")
        return 0
    sys.stdout.write(__doc__ or "")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
