"""Route-existence smoke tests.

The QA checklist (`docs/qa-checklist.md`) names a contract: every URL the
web app calls must exist on the FastAPI side. This file is the executable
half of that contract — a rename, accidental delete, or path-prefix change
fails CI before it can break the UI.
"""

from __future__ import annotations

import pytest


EXPECTED_ROUTES = {
    # Meta
    ("GET", "/health"),
    ("GET", "/version"),
    # Auth — Master Spec §6.1
    ("POST", "/api/auth/signup"),
    ("POST", "/api/auth/sign-in"),
    ("POST", "/api/auth/sign-out"),
    ("POST", "/api/auth/accept-invite"),
    ("POST", "/api/auth/change-password"),
    # Intake — Master Spec §6.2
    ("GET", "/api/intake/status"),
    ("POST", "/api/intake/service-selection"),
    ("POST", "/api/intake/consultation-request"),
    ("POST", "/api/intake/organization"),
    ("POST", "/api/intake/systems"),
    ("POST", "/api/intake/submit"),
    # Services — Master Spec §7
    ("GET", "/api/services/mine"),
    ("GET", "/api/services/{service_id}"),
}


def _registered_routes() -> set[tuple[str, str]]:
    from app.main import app

    out: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if not path or not methods:
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            out.add((method, path))
    return out


@pytest.mark.unit
def test_every_expected_route_is_registered() -> None:
    registered = _registered_routes()
    missing = EXPECTED_ROUTES - registered
    assert not missing, f"Routes disappeared: {sorted(missing)}"


@pytest.mark.unit
def test_no_silent_route_additions() -> None:
    """Catch routes that were added without updating EXPECTED_ROUTES.

    Anything in `registered - expected` either belongs in EXPECTED_ROUTES (so
    a future delete is caught) or shouldn't be exposed publicly. Update both
    sides together.
    """
    registered = _registered_routes()
    extras = {
        (m, p)
        for m, p in registered
        if p.startswith("/api/") and (m, p) not in EXPECTED_ROUTES
    }
    assert not extras, (
        "New /api/* routes added without updating EXPECTED_ROUTES in "
        f"tests/unit/test_routes_smoke.py: {sorted(extras)}"
    )


@pytest.mark.unit
def test_correlation_middleware_installed() -> None:
    from app.main import app

    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "CorrelationIdMiddleware" in middleware_names


@pytest.mark.unit
def test_global_exception_handler_installed() -> None:
    from app.main import app

    # FastAPI keeps custom handlers on the underlying Starlette app.
    handler_keys = list(app.exception_handlers.keys())
    assert any(k is Exception for k in handler_keys), "no global Exception handler"
