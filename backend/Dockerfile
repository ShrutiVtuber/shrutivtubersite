# ── build/runtime base ──────────────────────────────────────────────────────
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY shruti ./shruti
RUN pip install --upgrade pip && pip install .

# ── dev ─────────────────────────────────────────────────────────────────────
FROM base AS dev
RUN pip install ".[dev]"
CMD ["uvicorn", "shruti.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── prod ────────────────────────────────────────────────────────────────────
FROM base AS prod
COPY alembic.ini ./
COPY alembic ./alembic
RUN useradd --create-home --uid 10001 shruti \
 && mkdir -p /app/media && chown -R shruti:shruti /app
USER shruti
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/api/health || exit 1
CMD ["uvicorn", "shruti.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
