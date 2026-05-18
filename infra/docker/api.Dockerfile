# SHIELD by Kentro v2.0 — api + worker (FastAPI / Celery) dev image
FROM python:3.12-slim-bookworm

# System deps:
#   - libpango / libcairo / libgdk-pixbuf — WeasyPrint runtime
#   - libpq-dev — psycopg
#   - build essentials — for any wheels that compile
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      curl ca-certificates git \
      libpq-dev \
      libpango-1.0-0 libpangoft2-1.0-0 \
      libcairo2 \
      libgdk-pixbuf-2.0-0 \
      libffi-dev \
      shared-mime-info \
      fonts-dejavu \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1001 appgroup \
 && useradd  --system --uid 1001 --gid appgroup --home /home/appuser --shell /bin/bash appuser \
 && mkdir -p /workspace /opt/venv /home/appuser \
 && chown -R appuser:appgroup /workspace /opt/venv /home/appuser

USER appuser
WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN python -m venv /opt/venv \
 && pip install --upgrade pip wheel setuptools

EXPOSE 8000
