#!/usr/bin/env bash
# Check that no watermark on the printable chart covers anything readable.
#
#   TOKEN=<owner token> ADMIN_COOKIE=<session> ./scripts/check-print.sh
#
# Needs the stack running. Exits non-zero if a mark touches the chart, a
# heading, a paragraph, a table cell or the footer.
set -euo pipefail
cd "$(dirname "$0")/.."

WORK="${TMPDIR:-/tmp}/shruti-print"
mkdir -p "$WORK"
cp scripts/check-print.mjs "$WORK/scan.mjs"

docker run --rm --network host \
  -v "$WORK:/w" -w /w \
  -e BASE="${BASE:-http://127.0.0.1:8200}" \
  -e TOKEN="${TOKEN:?TOKEN is required — the owner token of a chart to print}" \
  -e ADMIN_COOKIE="${ADMIN_COOKIE:-}" \
  mcr.microsoft.com/playwright:v1.49.0-noble \
  sh -c 'npm i --silent playwright-core@1.49.0 >/dev/null 2>&1 && node scan.mjs'
