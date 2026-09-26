#!/usr/bin/env bash
# Delete an account for real, against a throwaway Postgres, and check what
# went and what stayed.
#
# Why this is not in scripts/test.sh: every other test reads source, and this
# one needs a database migrated to head — the only way to know a foreign key
# will not refuse the deletion is to ask Postgres. Deletion could not finish
# for months while every guard on the source was green.
#
# It starts its own Postgres on its own network, migrates it from nothing
# (which also proves the migrations run from an empty database), runs
# `test_an_account_can_be_deleted.py`, and removes both afterwards. It never
# touches the dev stack's database.
set -euo pipefail
cd "$(dirname "$0")/.."

NET=shruti-erase-test
PG=shruti-erase-pg
URL=postgresql+asyncpg://shruti:shruti@$PG:5432/shruti

cleanup() { docker rm -f "$PG" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup

docker network create "$NET" >/dev/null
docker run -d --name "$PG" --network "$NET" \
  -e POSTGRES_USER=shruti -e POSTGRES_PASSWORD=shruti -e POSTGRES_DB=shruti postgres:17 >/dev/null
docker build --quiet --target dev -t shruti-backend-test ./backend >/dev/null

until docker exec "$PG" pg_isready -U shruti >/dev/null 2>&1; do sleep 1; done

RUN=(docker run --rm --network "$NET"
  -e SHRUTI_DATABASE_URL="$URL" -e SHRUTI_ERASE_DATABASE_URL="$URL"
  -e SHRUTI_SECRET_KEY=test-only-not-a-real-key
  -v "$PWD/backend/shruti:/app/shruti:ro"
  -v "$PWD/backend/shrutisguides:/app/shrutisguides:ro"
  -v "$PWD/backend/tests:/app/tests:ro"
  -v "$PWD/backend/alembic:/app/alembic:ro"
  -v "$PWD/backend/alembic.ini:/app/alembic.ini:ro"
  -v "$PWD/frontend/site/src:/app/frontend/site/src:ro"
  -v "$PWD/docker-compose.yml:/app/docker-compose.yml:ro"
  shruti-backend-test)

"${RUN[@]}" alembic upgrade head
"${RUN[@]}" python -m pytest tests/test_an_account_can_be_deleted.py -rs "$@"
