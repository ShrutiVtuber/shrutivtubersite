#!/usr/bin/env bash
# Import Swara Studio's course from the private course repository into the
# site's database, where Sophia edits it in the Swara Studio admin.
#
# The course (SYLLABUS.md, lessons, exercises, glossary, candidate
# recordings) is her text and lives in the private swara-studio repository,
# never here. This builds one JSON bundle from it, copies it into the
# backend container (locally with `docker compose cp`, or on the server
# over ssh when SHRUTI_HOST is set, as scripts/sync-carnatic-data.sh does),
# and runs the import there. The import creates what is new and follows the
# files for everything she hasn't edited; a lesson she edited in the admin is
# never overwritten (the admin shows "a newer file version exists"). All
# recordings arrive as candidates; nothing is public until she approves it.
#
#   ./scripts/sync-carnatic-course.sh                                     # local stack
#   SHRUTI_HOST=deploy@159.195.251.161 ./scripts/sync-carnatic-course.sh  # production
#
# SWARA_COURSE overrides where the course is read from (default: the main
# worktree of the swara-studio repository).
set -euo pipefail

if [ -z "${SWARA_COURSE:-}" ]; then
  for candidate in "$HOME/Documents/development/swara-studio-main/course" \
                   "$HOME/Documents/development/swara-studio/course"; do
    if [ -d "$candidate/lessons" ]; then SWARA_COURSE="$candidate"; break; fi
  done
fi
COURSE="${SWARA_COURSE:-$HOME/Documents/development/swara-studio-main/course}"
[ -d "$COURSE/lessons" ] || { echo "no course at $COURSE — set SWARA_COURSE" >&2; exit 1; }
[ -f "$COURSE/LICENSE.md" ] || { echo "course/LICENSE.md is missing; the course is not imported without it" >&2; exit 1; }

here="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

python3 "$here/carnatic/build_course.py" "$COURSE" "$tmp/course-import.json" || {
  echo "the course didn't build; read the problem above and fix the course before importing" >&2; exit 1; }

IMPORT="python -m shruti.carnatic_import /app/carnatic/course-import.json"
if [ -n "${SHRUTI_HOST:-}" ]; then
  KEY=${SHRUTI_KEY:-$HOME/.ssh/agents_netcup}
  DIR=${SHRUTI_DIR:-/srv/shrutivtuber/prod}
  COMPOSE="sudo -u theourgia -H docker compose -f docker-compose.yml -f docker-compose.prod.yml"
  remote="/tmp/carnatic-course-$$"
  ssh -i "$KEY" "$SHRUTI_HOST" "mkdir -p $remote"
  scp -q -i "$KEY" "$tmp/course-import.json" "$SHRUTI_HOST:$remote/"
  ssh -i "$KEY" "$SHRUTI_HOST" "cd $DIR && $COMPOSE cp $remote/course-import.json backend:/app/carnatic/ && $COMPOSE exec -T backend $IMPORT; rm -rf $remote"
else
  docker compose cp "$tmp/course-import.json" backend:/app/carnatic/ >/dev/null
  docker compose exec -T backend $IMPORT
fi
