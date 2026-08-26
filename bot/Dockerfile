# vcordbot — an ordinary web service, which is the whole argument for HTTP
# interactions over a gateway: nothing here has to stay connected to anything.
FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev
RUN pip install --no-cache-dir pytest==8.3.4
COPY . .
CMD ["python", "-m", "pytest", "-q"]

FROM base AS prod
COPY vcordbot ./vcordbot
# No shell, no test runner, nothing to poke at.
CMD ["uvicorn", "vcordbot.app:app", "--host", "0.0.0.0", "--port", "8000"]
