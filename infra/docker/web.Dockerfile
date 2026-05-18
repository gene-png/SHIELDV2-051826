# SHIELD by Kentro v2.0 — web (Next.js 14 App Router) dev image
FROM node:20-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN corepack enable \
 && corepack prepare pnpm@9.12.3 --activate

RUN groupadd --system --gid 1001 appgroup \
 && useradd  --system --uid 1001 --gid appgroup --home /home/appuser --shell /bin/bash appuser \
 && mkdir -p /workspace /home/appuser \
 && chown -R appuser:appgroup /workspace /home/appuser

USER appuser
WORKDIR /workspace

ENV NODE_ENV=development \
    PNPM_HOME=/home/appuser/.local/share/pnpm \
    PATH=/home/appuser/.local/share/pnpm:$PATH

EXPOSE 3000
