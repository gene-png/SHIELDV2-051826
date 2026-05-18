"""Append-only audit log. Enforced by a Postgres trigger created in the
baseline migration — see Master Spec §4.1 / §11.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utcnow


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_id: Mapped[str | None] = mapped_column(String(80))
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(80), index=True)
