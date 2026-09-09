#!/usr/bin/env bash
# Copy theourgia's language packs into the site's pack volume.
#
# Isopsephy in the app needs two things per language: the letter values and a
# corpus to find matches in. Both already exist as theourgia packs, and they
# are REUSED rather than reinvented — a second copy of the Greek Milesian table
# is a second place for it to be wrong.
#
# ⚠ They are copied, not proxied. Pointing the site at theourgia at request
# time would mean the app's isopsephy stops working whenever theourgia is
# down, which is a strange way for one of her projects to break another.
# Drift is prevented by this being a script with digests rather than by a
# person remembering to copy files.
#
# ⚠ They are All Rights Reserved and are NOT committed. The app's repository
# is public and AGPL; the packs cannot live in it, and the volume is where
# they belong.
#
#   ./scripts/sync-packs.sh                 # from the local theourgia checkout
#   THEOURGIA=/path/to/theourgia ./scripts/sync-packs.sh
set -euo pipefail

THEOURGIA="${THEOURGIA:-$HOME/Documents/development/theourgia}"
DIST="$THEOURGIA/packs/dist"

[ -d "$DIST" ] || { echo "no packs at $DIST — set THEOURGIA" >&2; exit 1; }

# Only what isopsephy uses. The rest of theourgia's packs are rites, calendars
# and divination systems, and shipping them here would mean this site serving
# content it has no page for.
WANTED=(
  theourgia-numbers-greek-v2.mbf
  theourgia-numbers-hebrew-v1.mbf
  theourgia-numbers-arabic-v1.mbf
  theourgia-numbers-coptic-v1.mbf
  theourgia-numbers-sanskrit-v1.mbf
  theourgia-words-greek-diorisis-v2.mbf
  theourgia-words-hebrew-wlc-v2.mbf
  theourgia-words-hebrew-wikidata-v2.mbf
  theourgia-words-arabic-ayaspell-v2.mbf
  theourgia-words-sanskrit-wikidata-v2.mbf
  theourgia-words-sepher-sephiroth-v2.mbf
)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

missing=0
for f in "${WANTED[@]}"; do
  if [ -f "$DIST/$f" ]; then
    cp "$DIST/$f" "$tmp/$f"
  else
    echo "  missing from theourgia: $f" >&2
    missing=$((missing + 1))
  fi
done
[ "$missing" -eq 0 ] || { echo "$missing pack(s) missing; nothing copied" >&2; exit 1; }

# A digest beside each file, so a later run can say what changed and a reader
# can check they got the bytes theourgia built.
( cd "$tmp" && sha256sum ./*.mbf > SHA256SUMS )

docker compose cp "$tmp/." backend:/app/packs/ >/dev/null
echo "synced $(ls "$tmp"/*.mbf | wc -l) packs, $(du -sh "$tmp" | cut -f1)"
docker compose exec -T backend sh -c 'cd /app/packs && sha256sum -c SHA256SUMS 2>&1 | tail -3'
