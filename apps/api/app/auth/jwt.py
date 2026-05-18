"""SHIELD-issued JWT for the web app's NextAuth Credentials provider.

In v1 we sign our own short-lived JWTs (15 minutes per Master Spec §4.5). The
web app passes the bearer back to the API on every request; FastAPI verifies
the signature here. When we migrate to Keycloak as the IdP in v1.x, the
verification path swaps to JWKS validation — call sites stay identical.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.settings import get_settings

ALGORITHM = "HS256"
ISSUER = "shield-api"


def _signing_key() -> str:
    """Use NEXTAUTH_SECRET so web + api share a key in dev. Hard-fail if unset
    in non-dev — the web app's own validator wouldn't have anything to verify
    against either."""
    secret = os.environ.get("NEXTAUTH_SECRET", "")
    if not secret:
        env = get_settings().environment
        if env == "development":
            return "dev-only-not-for-prod"
        raise RuntimeError("NEXTAUTH_SECRET is required outside development")
    return secret


def issue_access_token(
    *,
    user_id: uuid.UUID,
    client_id: uuid.UUID,
    role: str,
    email: str,
    display_name: str,
) -> tuple[str, int]:
    settings = get_settings()
    now = datetime.now(tz=timezone.utc)
    ttl = settings.jwt_access_ttl_seconds
    payload = {
        "iss": ISSUER,
        "sub": str(user_id),
        "client_id": str(client_id),
        "role": role,
        "email": email,
        "display_name": display_name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, _signing_key(), algorithm=ALGORITHM)
    return token, ttl


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _signing_key(), algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
