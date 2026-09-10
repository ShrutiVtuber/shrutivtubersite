#!/usr/bin/env bash
# Deploy shrutivtuber.com.
#
# Everything the runbook says, in an order that refuses to continue when a step
# has not actually worked. `docs/DEPLOY.md` explains the why; this is the how.
#
# ⚠ **Never background this over SSH.** On 10 September a detached
# `nohup ssh … up -d --build &` died with its connection part-way through
# recreating the containers: the images were built, the site container was
# gone, and the other two were still the old ones. The site was down until it
# was re-run in the foreground, and the launching shell had reported success.
# Run it and watch it.
set -euo pipefail

HOST=${SHRUTI_HOST:-deploy@159.195.251.161}
KEY=${SHRUTI_KEY:-$HOME/.ssh/agents_netcup}
DIR=${SHRUTI_DIR:-/srv/shrutivtuber/prod}

# ⚠ The repo and .env on the box belong to `theourgia`, not to `deploy`. A pull
# as `deploy` fails on .git/FETCH_HEAD and compose cannot read .env at all.
#
# ⚠ `-H`, and `env VAR=…` rather than `sudo -E`: without -H the HOME is still
# /home/deploy and docker warns about a config it cannot read; with -E, sudo
# swallows the compose flags and docker answers "unknown shorthand flag: 'f'".
AS="sudo -u theourgia -H"
DC="$AS docker compose -f docker-compose.yml -f docker-compose.prod.yml"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
on()  { ssh -i "$KEY" "$HOST" "cd $DIR && $*"; }

say "Is the working tree on the server clean?"
# ⚠ This is the guard, and it is first for a reason. On 10 September the tree
# held 34 modified files, every one byte-identical to the laptop's — work that
# had never been committed or pushed reaching production by some route nobody
# has identified. A `git pull` then refuses, half way through a deploy, with a
# message about local changes.
#
# Refusing here turns an invisible condition into a stop sign whatever causes
# it. If it fires: look at the diff before you discard it, because something
# put it there.
dirty=$(on "$AS git status --porcelain" || true)
if [ -n "$dirty" ]; then
  echo "$dirty" | head -40
  cat <<'WHY'

The server's working tree has changes that are not in git.

Do NOT discard them without looking. Save and read them first:

  ssh -i ~/.ssh/agents_netcup deploy@159.195.251.161 \
    'cd /srv/shrutivtuber/prod && sudo -u theourgia git diff' > /tmp/prod-local.patch

Then, once you know what they are and that losing them is fine:

  ssh -i ~/.ssh/agents_netcup deploy@159.195.251.161 \
    'cd /srv/shrutivtuber/prod && sudo -u theourgia git reset --hard origin/main'
WHY
  exit 1
fi
echo "clean."

say "Pulling"
on "$AS git fetch --quiet origin && $AS git pull --ff-only"
SHA=$(on "$AS git rev-parse HEAD")
echo "at $SHA"

say "Building and starting — both profiles"
# ⚠ Both, every time. `site` sits behind `web` and `vcordbot` behind `bot`, so a
# plain `up -d --build` rebuilds postgres, backend and caddy and silently leaves
# the other two running whatever they were built from. Nothing looks wrong
# afterwards: the containers are up, healthy, and answering — with old code.
on "$AS env SHRUTI_SOURCE_SHA=$SHA docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile web --profile bot up -d --build"

say "Migrations"
on "$DC exec -T backend alembic upgrade head"

say "Registering new strings"
# Reading the templates needs no authority, so this half runs as anybody.
on "docker run --rm -v \"\$PWD:/repo:ro\" -w /repo node:22-alpine node scripts/seed-copy.mjs --json > /tmp/copy.json"
on "$DC exec -T backend python scripts/seed_copy.py < /tmp/copy.json && rm -f /tmp/copy.json"

say "Is it actually answering?"
for i in $(seq 1 20); do
  code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' https://shrutivtuber.com/api/health || true)
  [ "$code" = "200" ] && break
  sleep 3
done
[ "$code" = "200" ] || { echo "health is $code, not 200 — the site is not serving"; exit 1; }
curl -s -m 10 https://shrutivtuber.com/api/health; echo

say "Deployed $SHA"
