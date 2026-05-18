"""IDOR defense — check that an object belongs to the caller's deployment
before returning it. Single-tenant deployments make this mostly redundant, but
the per-deployment `client_id` carried on every row gives us a cheap belt-and-
braces guard that catches application bugs in tests.
"""

from __future__ import annotations

import uuid
from typing import Protocol


class HasClientId(Protocol):
    client_id: uuid.UUID


class AccessDenied(Exception):
    """Raised when an object belongs to a different client_id than the user.
    The FastAPI exception handler converts this to HTTP 404 (not 403) to
    avoid leaking object existence (Master Spec §4.1)."""


def check_object_access(*, obj: HasClientId, user_client_id: uuid.UUID) -> None:
    if obj.client_id != user_client_id:
        raise AccessDenied("object does not belong to this deployment")
