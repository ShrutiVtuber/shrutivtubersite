#!/usr/bin/env bash
# Rebuild the backend image and restart it, then report honestly.
#
# The backend source is NOT mounted into the container in dev — the image ships
# the code. So editing a file and running `alembic upgrade head` runs the OLD
# code, reports the OLD head, and looks exactly like a migration that did
# nothing wrong. That has now cost time twice, once locally and once on
# production.
#
# Reads docker's EXIT CODE, never grep output: `docker compose build | grep -c
# error` returns 0 on failure, which reads as success.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! docker compose build backend; then
  echo "  BUILD FAILED — the running container is still the old code" >&2
  exit 1
fi
docker compose up -d backend >/dev/null

# Wait for it to answer before anyone runs a migration against it.
for _ in $(seq 1 40); do
  if docker compose exec -T backend python -c "import shruti" >/dev/null 2>&1; then
    echo "  backend rebuilt and up"
    exit 0
  fi
  sleep 1
done
echo "  backend rebuilt but never came up" >&2
exit 1
