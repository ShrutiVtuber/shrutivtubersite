#!/usr/bin/env bash
# Register newly added strings with the LIVE admin.
#
# `say("key", "default")` in a template is enough for the page to render — the
# default is right there. It is NOT enough for the string to appear in the
# admin, because the panel lists rows from the database and nothing has told
# the database that key exists.
#
# So this has to run after any deploy that adds, renames or moves one. It asks
# for the password rather than storing it, sends it straight to the login
# route, and deletes the session file on the way out. Values already written
# are never touched: the seed route updates labels, defaults and order only.
#
#   ./scripts/seed-production.sh
set -euo pipefail

BASE="${BASE:-https://shrutivtuber.com}"
EMAIL="${EMAIL:-shruti@shrutivtuber.com}"
JAR="$(mktemp)"
trap 'rm -f "$JAR"' EXIT

read -rsp "Admin password for $EMAIL: " PW
echo

code=$(curl -s -o /dev/null -w '%{http_code}' -c "$JAR" -X POST "$BASE/api/admin/login" \
  -H 'Content-Type: application/json' \
  --data-binary "$(printf '{"email":%s,"password":%s}' \
      "$(printf '%s' "$EMAIL" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
      "$(printf '%s' "$PW"    | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')")")

if [ "$code" != "200" ]; then
  echo "Sign-in failed ($code)." >&2
  exit 1
fi

VALUE=$(awk '/shruti_session/ {print $7}' "$JAR")
[ -n "$VALUE" ] || { echo "No session cookie came back." >&2; exit 1; }

ADMIN_COOKIE="shruti_session=$VALUE" BASE="$BASE" node scripts/seed-copy.mjs
