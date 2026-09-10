#!/usr/bin/env bash
# Run the backend test suite.
#
# Not `docker compose exec backend pytest`: the compose file names no build
# target, so Docker builds the LAST stage in backend/Dockerfile — `prod`, which
# deliberately does not ship a test runner. The `dev` stage does, and this
# builds that one on its own and mounts the working tree into it read-only.
#
# The consequence worth having: tests run against the files as they are on
# disk, with no rebuild of the running stack and no restart of anything the
# browser is pointed at.
#
# The site's own source is mounted too. One test reads the pages — the wrapper
# every page needs is a frontend fact with no backend to ask about it — and
# without this it would find no files and pass on an empty list, which is the
# worst kind of green.
set -euo pipefail
cd "$(dirname "$0")/.."

docker build --quiet --target dev -t shruti-backend-test ./backend >/dev/null

# Mounted read-only, and more than just `shruti`:
#   frontend/site/src     the page-wrapper and structured-data guards read it
#   frontend/site/public  the service worker lives there
#   backend/alembic       the dev stage does not ship it, and some guarantees
#                         live in a migration rather than in code
#   the two Caddyfiles    who may frame the site is a proxy fact, and the
#                         answer differing between local and production is
#                         exactly how the preview shipped broken
#   docker-compose.yml    where the packs volume and the caddy routes are said
#   fonts-render          the share-card fonts
#
# ⚠ And `tests/conftest.py` resolves the root by looking for a marker rather
# than by counting `parents[2]`, which is the repository on a laptop and `/`
# inside this container. Eleven guards had been failing on the missing file
# rather than on the thing they guard.
# A guard that cannot read the file it guards passes on an empty string, which
# is the way this kind of check usually lies.
exec docker run --rm \
  -v "$PWD/backend/shruti:/app/shruti:ro" \
  -v "$PWD/backend/tests:/app/tests:ro" \
  -v "$PWD/backend/alembic:/app/alembic:ro" \
  -v "$PWD/frontend/site/src:/app/frontend/site/src:ro" \
  -v "$PWD/frontend/site/public:/app/frontend/site/public:ro" \
  -v "$PWD/Caddyfile.internal:/app/Caddyfile.internal:ro" \
  -v "$PWD/deploy:/app/deploy:ro" \
  -v "$PWD/scripts:/app/scripts:ro" \
  -v "$PWD/docker-compose.yml:/app/docker-compose.yml:ro" \
  -v "$PWD/frontend/site/fonts-render:/app/frontend/site/fonts-render:ro" \
  -v "$PWD/frontend/site/Dockerfile:/app/frontend/site/Dockerfile:ro" \
  -v "$PWD/frontend/site/package.json:/app/frontend/site/package.json:ro" \
  -v "$PWD/frontend/site/scripts:/app/frontend/site/scripts:ro" \
  -e SHRUTI_SECRET_KEY=test-only-not-a-real-key \
  shruti-backend-test \
  python -m pytest tests "$@"
