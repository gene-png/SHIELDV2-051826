"""FastAPI dependencies — `require_role(Role.admin)` etc.

The token validator (`validate_bearer`) is a stub in v1: it accepts a
Keycloak-issued JWT, validates signature against JWKS, and maps
`realm_access.roles` to internal `Role`. For unit tests, providing the
`X-Test-User-*` headers bypasses Keycloak — only enabled when
`ENVIRONMENT in {development, test, ci}`.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, status

from app.auth.jwt import decode_access_token
from app.models.enums import Role
from app.settings import get_settings


class CurrentUser:
    def __init__(
        self,
        *,
        user_id: uuid.UUID,
        client_id: uuid.UUID,
        email: str,
        role: Role,
        display_name: str,
    ) -> None:
        self.user_id = user_id
        self.client_id = client_id
        self.email = email
        self.role = role
        self.display_name = display_name


async def _resolve_user_from_test_headers(
    x_test_user_id: str | None = Header(default=None, alias="X-Test-User-Id"),
    x_test_client_id: str | None = Header(default=None, alias="X-Test-Client-Id"),
    x_test_role: str | None = Header(default=None, alias="X-Test-Role"),
    x_test_email: str | None = Header(default=None, alias="X-Test-Email"),
) -> CurrentUser | None:
    settings = get_settings()
    if settings.environment not in ("development", "test", "ci"):
        return None
    if not (x_test_user_id and x_test_client_id and x_test_role):
        return None
    return CurrentUser(
        user_id=uuid.UUID(x_test_user_id),
        client_id=uuid.UUID(x_test_client_id),
        email=x_test_email or "test@example.org",
        role=Role(x_test_role),
        display_name="Test User",
    )


async def get_current_user(
    test_user: CurrentUser | None = Depends(_resolve_user_from_test_headers),
    authorization: str | None = Header(default=None),
) -> CurrentUser:
    if test_user is not None:
        return test_user
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token expired"
        ) from exc
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc
    return CurrentUser(
        user_id=uuid.UUID(payload["sub"]),
        client_id=uuid.UUID(payload["client_id"]),
        email=payload["email"],
        role=Role(payload["role"]),
        display_name=payload.get("display_name", ""),
    )


def require_role(*roles: Role) -> Callable[..., Awaitable[CurrentUser]]:
    async def _enforce(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="role not permitted on this resource",
            )
        return user

    return _enforce
