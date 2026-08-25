#!/usr/bin/env bash
# Walk the site at fourteen widths and report anything that overflows.
#
# The failure this catches is the one that was actually shipped: content wider
# than the window, so the page scrolls sideways and looks broken. It is not a
# thing a build, a typecheck or a unit test can see — it needs a browser and a
# viewport — and it is not a thing anybody spots by resizing, because a layout
# can be right at the two widths you happen to try and wrong between them.
#
#   ./scripts/check-widths.sh                     the public pages
#   ./scripts/check-widths.sh /admin,/admin/shop  whatever you name
#
# Needs the stack running. Pass an admin session cookie so it gets past the
# holding page:
#
#   ADMIN_COOKIE=$(...) ./scripts/check-widths.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PUBLIC="/,/about,/work,/classes,/shop,/support,/today,/schedule,/videos"
PUBLIC="$PUBLIC,/horoscopes,/contact,/journal,/press,/fan-works,/newsletter"
PUBLIC="$PUBLIC,/privacy,/terms"

WORK="${TMPDIR:-/tmp}/shruti-widths"
mkdir -p "$WORK"
cp scripts/check-widths.mjs "$WORK/scan.mjs"

IMAGE=mcr.microsoft.com/playwright:v1.49.0-noble

# The client only; the browsers are already in the image.
if [[ ! -d "$WORK/node_modules/playwright-core" ]]; then
  docker run --rm -v "$WORK:/w" -w /w "$IMAGE" \
    npm install playwright-core@1.49.0 --silent --no-audit --no-fund
fi

exec docker run --rm --network host -v "$WORK:/w" -w /w \
  -e ADMIN_COOKIE="${ADMIN_COOKIE:-}" \
  -e BASE="${BASE:-http://127.0.0.1:8200}" \
  -e PAGES="${1:-$PUBLIC}" \
  "$IMAGE" node scan.mjs
