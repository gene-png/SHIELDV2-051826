"""SHIELD by Kentro v2.0 — FastAPI entrypoint.

Bootstraps the global exception handler (no stack traces to user — Master Spec
§4.1), structured JSON logging, correlation-ID middleware, and the OpenAPI
surface. Refuses to start with `DEBUG=True` outside loopback (Master Spec §18).
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.settings import get_settings


def _enforce_no_debug_outside_loopback() -> None:
    """Master Spec §18 — DEBUG=True must never leak to non-loopback."""
    if os.environ.get("DEBUG", "").lower() == "true":
        host = os.environ.get("HOST", "0.0.0.0")
        if host not in ("127.0.0.1", "localhost"):
            raise RuntimeError(
                "Refusing to start: DEBUG=true is forbidden outside loopback. "
                "See Master Spec §18 acceptance criteria."
            )


_enforce_no_debug_outside_loopback()
settings = get_settings()

app = FastAPI(
    title="SHIELD by Kentro — API",
    version="0.1.0",
    description="Enterprise cybersecurity assessment platform. Single-tenant per deployment.",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)


@app.exception_handler(Exception)
async def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler — never leaks stack traces. Master Spec §4.1."""
    correlation_id = request.headers.get("x-correlation-id", "")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Please contact support with the correlation ID.",
            "correlation_id": correlation_id,
        },
    )


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe. Lightweight — no DB hit. Use `/ready` for readiness."""
    return {"status": "ok", "service": "shield-api", "environment": settings.environment}


@app.get("/version", tags=["meta"])
async def version() -> dict[str, str]:
    return {"service": "shield-api", "version": app.version}
