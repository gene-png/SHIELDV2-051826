"""SHIELD by Kentro v2.0 — FastAPI entrypoint.

Bootstraps the global exception handler (no stack traces to user — Master Spec
§4.1), structured JSON logging, correlation-ID middleware, and the OpenAPI
surface. Refuses to start with `DEBUG=True` outside loopback (Master Spec §18).
"""

from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import auth as auth_router
from app.api.routers import intake as intake_router
from app.settings import get_settings
from app.spine.access import AccessDenied
from app.spine.correlation import CorrelationIdMiddleware
from app.spine.logging import get_logger


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
log = get_logger("shield.api")

app = FastAPI(
    title="SHIELD by Kentro — API",
    version="0.1.0",
    description="Enterprise cybersecurity assessment platform. Single-tenant per deployment.",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(auth_router.router)
app.include_router(intake_router.router)


@app.exception_handler(AccessDenied)
async def _access_denied_handler(request: Request, exc: AccessDenied) -> JSONResponse:
    """Treat IDOR as 404 to avoid leaking object existence (Master Spec §4.1)."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "correlation_id": getattr(request.state, "correlation_id", ""),
        },
    )


@app.exception_handler(Exception)
async def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler — never leaks stack traces. Master Spec §4.1."""
    correlation_id = getattr(request.state, "correlation_id", "") or request.headers.get(
        "x-correlation-id", ""
    )
    log.exception("unhandled_exception", correlation_id=correlation_id, path=request.url.path)
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
    return {"status": "ok", "service": "shield-api", "environment": settings.environment}


@app.get("/version", tags=["meta"])
async def version() -> dict[str, str]:
    return {"service": "shield-api", "version": app.version}
