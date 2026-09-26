#!/usr/bin/env bash
# Build Swara Studio's data files from the private research repository and
# put them where the site serves them from.
#
# The research (research/ragas, tala, lessons, instruments, web) is a
# compilation of facts about Carnatic music with its sources and confidence
# levels; as a compilation it is All Rights Reserved and it lives in the
# private swara-studio repository, never here. This script turns it into a
# handful of JSON files, names the set by its digest, writes a manifest, and
# copies them into the `carnatic` volume — locally with `docker compose cp`,
# or on the server over ssh when SHRUTI_HOST is set (the same host and key
# as scripts/deploy.sh).
#
#   ./scripts/sync-carnatic-data.sh                 # local stack
#   SHRUTI_HOST=deploy@159.195.251.161 ./scripts/sync-carnatic-data.sh   # production
#
# SWARA_RESEARCH overrides where the research is read from. By default it is
# the `research` worktree of the swara-studio repository (research edits are
# committed there, on the research branch, apart from the app's checkout),
# falling back to the main checkout.
set -euo pipefail

if [ -z "${SWARA_RESEARCH:-}" ]; then
  for candidate in "$HOME/Documents/development/swara-studio-research/research" \
                   "$HOME/Documents/development/swara-studio/research"; do
    if [ -d "$candidate" ]; then SWARA_RESEARCH="$candidate"; break; fi
  done
fi
RESEARCH="${SWARA_RESEARCH:-$HOME/Documents/development/swara-studio-research/research}"
[ -d "$RESEARCH" ] || { echo "no research at $RESEARCH — set SWARA_RESEARCH" >&2; exit 1; }
[ -f "$RESEARCH/LICENSE-DATA.md" ] || { echo "research/LICENSE-DATA.md is missing; the data is not published without it" >&2; exit 1; }

here="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

summary="$(python3 "$here/carnatic/build_data.py" "$RESEARCH" "$tmp")" || {
  echo "the build reported problems; read them above and fix the research before publishing" >&2; exit 1; }

python3 - "$tmp" "$summary" "$RESEARCH" <<'PY'
import json, sys, datetime, os, subprocess
tmp, summary, research = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
try:
    commit = subprocess.run(["git", "-C", research, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", research, "status", "--porcelain", "--", "."],
                                capture_output=True, text=True).stdout.strip())
except Exception:
    commit, dirty = "", False
manifest = {
    "format": summary["format"],
    "digest": summary["digest"],
    "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "research": {"commit": commit, "uncommitted_changes": dirty},
    "files": summary["files"],
    "counts": summary["counts"],
    "license": "LicenseRef-All-Rights-Reserved (compilation); facts are facts",
}
with open(os.path.join(tmp, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
for name in os.listdir(tmp):
    os.chmod(os.path.join(tmp, name), 0o644)   # the container's user is not ours; readable by anyone
print("carnatic data:", ", ".join(f"{x['name']} ({x['bytes'] // 1024} KB)" for x in manifest["files"]))
print("counts:", manifest["counts"], "research", commit or "(not a git checkout)", "with uncommitted changes" if dirty else "")
PY

files=(manifest.json)
for f in "$tmp"/*.json; do
  name="$(basename "$f")"
  [ "$name" = manifest.json ] || files+=("$name")
done

if [ -n "${SHRUTI_HOST:-}" ]; then
  KEY=${SHRUTI_KEY:-$HOME/.ssh/agents_netcup}
  DIR=${SHRUTI_DIR:-/srv/shrutivtuber/prod}
  COMPOSE="sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml"
  remote="/tmp/carnatic-$$"
  ssh -i "$KEY" "$SHRUTI_HOST" "mkdir -p $remote"
  scp -q -i "$KEY" "${files[@]/#/$tmp/}" "$SHRUTI_HOST:$remote/"
  # The data files first and the manifest last, so a reader never sees a
  # manifest naming a digest whose files have not arrived.
  cps=""
  for f in "${files[@]}"; do
    [ "$f" = manifest.json ] && continue
    cps="$cps && $COMPOSE cp $remote/$f backend:/app/carnatic/"
  done
  ssh -i "$KEY" "$SHRUTI_HOST" "cd $DIR && true$cps && $COMPOSE cp $remote/manifest.json backend:/app/carnatic/ && rm -rf $remote"
else
  for f in "${files[@]}"; do
    [ "$f" = manifest.json ] && continue
    docker compose cp "$tmp/$f" backend:/app/carnatic/ >/dev/null
  done
  docker compose cp "$tmp/manifest.json" backend:/app/carnatic/ >/dev/null
fi
echo "synced carnatic data $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["digest"])' "$tmp/manifest.json")"
