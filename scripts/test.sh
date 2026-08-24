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
set -euo pipefail
cd "$(dirname "$0")/.."

docker build --quiet --target dev -t shruti-backend-test ./backend >/dev/null

exec docker run --rm \
  -v "$PWD/backend/shruti:/app/shruti:ro" \
  -v "$PWD/backend/tests:/app/tests:ro" \
  -e SHRUTI_SECRET_KEY=test-only-not-a-real-key \
  shruti-backend-test \
  python -m pytest tests "$@"
