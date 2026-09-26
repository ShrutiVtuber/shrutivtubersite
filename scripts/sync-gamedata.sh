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
# as scripts/deploy.sh). Every research/<game>/ledger.json (the Ledger's
# packs, served as files) goes with them as ledger-<game>.json.
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

# The Ledger's packs are not loaded into the database: each is one JSON file,
# research/<game>/ledger.json, served as it is by GET /api/ledger/data. They
# travel beside the database as ledger-<game>.json. A pack that is not valid
# JSON stops the sync, as a build problem does.
ledgers=()
for f in "$RESEARCH"/*/ledger.json; do
  [ -f "$f" ] || continue
  name="$(basename "$(dirname "$f")")"
  case "$name" in _*) continue ;; esac
  python3 -c 'import json, sys; json.load(open(sys.argv[1]))' "$f" 2>/dev/null \
    || { echo "  $name: ledger.json is not valid JSON — not published" >&2; exit 1; }
  cp "$f" "$tmp/ledger-$name.json"
  chmod 644 "$tmp/ledger-$name.json"       # readable by the container's user, like the database
  ledgers+=("ledger-$name.json")
done

( cd "$TRACKER/server" && "${PYTHON:-.venv/bin/python}" - "$tmp" "$sum" ${ledgers[@]+"${ledgers[@]}"} <<'PY'
import json, sys, datetime, os, hashlib
from shrutisguides.gamedata import GameData
tmp, digest, ledger_files = sys.argv[1], sys.argv[2], sys.argv[3:]
data = GameData(os.path.join(tmp, "gamedata.sqlite3"))
manifest = {
    "file": f"gamedata-{digest}.sqlite3", "url": f"/gamedata/gamedata-{digest}.sqlite3", "digest": digest,
    "bytes": os.path.getsize(os.path.join(tmp, "gamedata.sqlite3")),
    "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "games": [{"id": g["id"], "name": g["name"], "patch": g["patch"], "season": g["season"], "researched_at": g["researched_at"],
               "records": sum(g["counts"].values())} for g in data.games()],
    "ledgers": [],
    "license": "LicenseRef-All-Rights-Reserved (compilation); facts are facts",
}
for name in ledger_files:
    path = os.path.join(tmp, name)
    with open(path, "rb") as f:
        raw = f.read()
    game = json.loads(raw).get("game") or {}
    manifest["ledgers"].append({"file": name, "game": name[len("ledger-"):-len(".json")], "name": game.get("name"),
                                "version": game.get("version"), "build": game.get("build"), "gathered": game.get("gathered"),
                                "bytes": len(raw), "digest": hashlib.sha256(raw).hexdigest()[:16]})
with open(os.path.join(tmp, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
os.chmod(os.path.join(tmp, "manifest.json"), 0o644)
print("games:", ", ".join(f"{g['name']} ({g['records']})" for g in manifest["games"]))
print("ledgers:", ", ".join(l["file"] for l in manifest["ledgers"]) or "none")
PY
)

if [ -n "${SHRUTI_HOST:-}" ]; then
  KEY=${SHRUTI_KEY:-$HOME/.ssh/agents_netcup}
  DIR=${SHRUTI_DIR:-/srv/shrutivtuber/prod}
  COMPOSE="sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml"
  ledger_cp="" ledger_rm=""               # one copy per ledger pack, then its temporary file goes
  for l in ${ledgers[@]+"${ledgers[@]}"}; do
    ledger_cp="$ledger_cp && $COMPOSE cp /tmp/$l backend:/app/gamedata/"
    ledger_rm="$ledger_rm /tmp/$l"
  done
  scp -q -i "$KEY" "$tmp/gamedata-$sum.sqlite3" "$tmp/gamedata.sqlite3" "$tmp/manifest.json" \
    ${ledgers[@]+"${ledgers[@]/#/$tmp/}"} "$SHRUTI_HOST:/tmp/"
  ssh -i "$KEY" "$SHRUTI_HOST" "cd $DIR && $COMPOSE cp /tmp/gamedata-$sum.sqlite3 backend:/app/gamedata/ \
    && $COMPOSE cp /tmp/gamedata.sqlite3 backend:/app/gamedata/$ledger_cp \
    && $COMPOSE cp /tmp/manifest.json backend:/app/gamedata/ \
    && rm -f /tmp/gamedata-$sum.sqlite3 /tmp/gamedata.sqlite3 /tmp/manifest.json$ledger_rm"
else
  docker compose cp "$tmp/gamedata-$sum.sqlite3" backend:/app/gamedata/ >/dev/null
  docker compose cp "$tmp/gamedata.sqlite3" backend:/app/gamedata/ >/dev/null
  for l in ${ledgers[@]+"${ledgers[@]}"}; do
    docker compose cp "$tmp/$l" backend:/app/gamedata/ >/dev/null
  done
  docker compose cp "$tmp/manifest.json" backend:/app/gamedata/ >/dev/null
fi
echo "synced gamedata-$sum.sqlite3 ($(du -h "$tmp/gamedata.sqlite3" | cut -f1))${ledgers[@]+ and ${ledgers[*]}}"
