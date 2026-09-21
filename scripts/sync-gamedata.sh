#!/usr/bin/env bash
# Build the game database from the guides repository's research packs and
# put it where the site and Caddy serve it from.
#
# The packs (research/<game>/*.json) are facts about games, compiled with
# their sources recorded; as a compilation they are All Rights Reserved and
# they live in the private guides repository, never here. This script turns
# them into one SQLite file, names it by its digest, writes a manifest, and
# copies both into the `gamedata` volume — locally with `docker compose cp`,
# or on the server over ssh when SHRUTI_HOST is set (the same host and key
# as scripts/deploy.sh).
#
#   ./scripts/sync-gamedata.sh                 # local stack
#   SHRUTI_HOST=deploy@159.195.251.161 ./scripts/sync-gamedata.sh   # production
set -euo pipefail

TRACKER="${TRACKER:-$HOME/Documents/development/shrutisgametracker}"
RESEARCH="$TRACKER/research"
[ -d "$RESEARCH" ] || { echo "no research packs at $RESEARCH — set TRACKER" >&2; exit 1; }
[ -f "$RESEARCH/LICENSE-DATA.md" ] || { echo "research/LICENSE-DATA.md is missing; the packs are not published without it" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Every game folder must carry both a sources and a coverage note, or it is
# not published: a fact without its source is a claim.
for dir in "$RESEARCH"/*/; do
  name="$(basename "$dir")"
  case "$name" in _*) continue ;; esac
  ls "$dir"/sources-*.md >/dev/null 2>&1 || { echo "  $name: no sources-*.md — not published" >&2; exit 1; }
  ls "$dir"/coverage-*.md >/dev/null 2>&1 || { echo "  $name: no coverage-*.md — not published" >&2; exit 1; }
done

( cd "$TRACKER/server" && "${PYTHON:-.venv/bin/python}" -m shrutisguides.gamedata build "$RESEARCH" "$tmp/gamedata.sqlite3" ) || {
  echo "the build reported problems; read them above and fix the packs before publishing" >&2; exit 1; }

chmod 644 "$tmp/gamedata.sqlite3"          # the container's user is not ours; the file must be readable by anyone
sum="$(sha256sum "$tmp/gamedata.sqlite3" | cut -c1-16)"
mv "$tmp/gamedata.sqlite3" "$tmp/gamedata-$sum.sqlite3"
cp "$tmp/gamedata-$sum.sqlite3" "$tmp/gamedata.sqlite3"          # the backend opens this name; Caddy serves the digest name
( cd "$TRACKER/server" && "${PYTHON:-.venv/bin/python}" - "$tmp" "$sum" <<'PY'
import json, sys, datetime, os
from shrutisguides.gamedata import GameData
tmp, digest = sys.argv[1], sys.argv[2]
data = GameData(os.path.join(tmp, "gamedata.sqlite3"))
manifest = {
    "file": f"gamedata-{digest}.sqlite3", "url": f"/gamedata/gamedata-{digest}.sqlite3", "digest": digest,
    "bytes": os.path.getsize(os.path.join(tmp, "gamedata.sqlite3")),
    "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "games": [{"id": g["id"], "name": g["name"], "patch": g["patch"], "season": g["season"], "researched_at": g["researched_at"],
               "records": sum(g["counts"].values())} for g in data.games()],
    "license": "LicenseRef-All-Rights-Reserved (compilation); facts are facts",
}
with open(os.path.join(tmp, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
os.chmod(os.path.join(tmp, "manifest.json"), 0o644)
print("games:", ", ".join(f"{g['name']} ({g['records']})" for g in manifest["games"]))
PY
)

if [ -n "${SHRUTI_HOST:-}" ]; then
  KEY=${SHRUTI_KEY:-$HOME/.ssh/agents_netcup}
  DIR=${SHRUTI_DIR:-/srv/shrutivtuber/prod}
  scp -q -i "$KEY" "$tmp/gamedata-$sum.sqlite3" "$tmp/gamedata.sqlite3" "$tmp/manifest.json" "$SHRUTI_HOST:/tmp/"
  ssh -i "$KEY" "$SHRUTI_HOST" "cd $DIR && sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml cp /tmp/gamedata-$sum.sqlite3 backend:/app/gamedata/ \
    && sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml cp /tmp/gamedata.sqlite3 backend:/app/gamedata/ \
    && sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml cp /tmp/manifest.json backend:/app/gamedata/ \
    && rm -f /tmp/gamedata-$sum.sqlite3 /tmp/gamedata.sqlite3 /tmp/manifest.json"
else
  docker compose cp "$tmp/gamedata-$sum.sqlite3" backend:/app/gamedata/ >/dev/null
  docker compose cp "$tmp/gamedata.sqlite3" backend:/app/gamedata/ >/dev/null
  docker compose cp "$tmp/manifest.json" backend:/app/gamedata/ >/dev/null
fi
echo "synced gamedata-$sum.sqlite3 ($(du -h "$tmp/gamedata.sqlite3" | cut -f1))"
