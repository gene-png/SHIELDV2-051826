"""Customer organization (singleton row per deployment)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class Client(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """Master Spec §11 — exactly one row per deployment.

    Singleton enforced at application level (a creation guard) plus a
    partial-unique index in the baseline migration. `client_id` is the row's
    own `id` value (set on insert) so every other table's tenant scope FK
    resolves cleanly.
    """

    __tablename__ = "client"

    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dba_name: Mapped[Optional[str]] = mapped_column(String(200))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    size_band: Mapped[Optional[str]] = mapped_column(String(40))
    industry: Mapped[Optional[str]] = mapped_column(String(120))
    address_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    primary_poc_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    compliance_deadline: Mapped[Optional[date]] = mapped_column(Date)
    service_interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    intake_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
