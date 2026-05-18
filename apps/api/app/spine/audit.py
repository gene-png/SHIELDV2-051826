"""Audit-log helper. Every state-changing route calls `audit(...)`. The DB
trigger from migration 0001 rejects any later UPDATE/DELETE.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditEntry


def audit(
    db: Session,
    *,
    client_id: uuid.UUID,
    action: str,
    target_type: str,
    target_id: str | None = None,
    actor_user_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> AuditEntry:
    entry = AuditEntry(
        client_id=client_id,
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {},
        correlation_id=correlation_id,
        at=datetime.now(tz=timezone.utc),
    )
    db.add(entry)
    db.flush()  # Surfaces trigger violations on `UPDATE`/`DELETE` (here only INSERT runs).
    return entry
