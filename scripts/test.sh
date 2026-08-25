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

exec docker run --rm \
  -v "$PWD/backend/shruti:/app/shruti:ro" \
  -v "$PWD/backend/tests:/app/tests:ro" \
  -v "$PWD/frontend/site/src:/app/frontend/site/src:ro" \
  -e SHRUTI_SECRET_KEY=test-only-not-a-real-key \
  shruti-backend-test \
  python -m pytest tests "$@"
