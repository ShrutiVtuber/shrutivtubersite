#!/usr/bin/env bash
# Build the site image, and say plainly whether it built.
#
# Written because `docker compose build | grep -c error` reports zero on a
# FAILED build whose message does not happen to match — which is how a stray
# brace in a stylesheet went unnoticed while several changes appeared to deploy
# and did not. Docker's exit code is the truth; grep never was.
#
# A first attempt at this checked for "Server built in" instead, which is
# wrong the other way: a cached build never prints it and would be called a
# failure.
set -uo pipefail
cd "$(dirname "$0")/.."

out="$(docker compose --profile web build site 2>&1)"
code=$?

if [[ $code -ne 0 ]]; then
  sed 's/\x1b\[[0-9;]*m//g' <<<"$out" | grep -vE "^ ---> |Using cache|^Step " | tail -20
  echo
  echo "the site did NOT build" >&2
  exit "$code"
fi

if grep -q "Server built in" <<<"$out"; then
  sed 's/\x1b\[[0-9;]*m//g' <<<"$out" | grep -E "Server built in" | tail -1
else
  echo "built (nothing changed — every layer was cached)"
fi
