"""Engagement service rows + in-scope systems."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import ServiceFramework, ServiceStatus, ServiceType, TierLevel


class Service(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "service"

    type: Mapped[ServiceType] = mapped_column(String(40), nullable=False, index=True)
    framework: Mapped[Optional[ServiceFramework]] = mapped_column(String(20))
    status: Mapped[ServiceStatus] = mapped_column(
        String(40), nullable=False, default=ServiceStatus.NEW, index=True
    )
    assigned_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    assigned_reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    headline: Mapped[Optional[str]] = mapped_column(String(500))
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class System(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """In-scope systems for CSF and Zero Trust engagements (Master Spec §6.2 I3)."""

    __tablename__ = "systems"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    csam_id: Mapped[Optional[str]] = mapped_column(String(40))
    fips_categorization: Mapped[Optional[TierLevel]] = mapped_column(String(20))
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    isso_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    hosting: Mapped[Optional[str]] = mapped_column(String(120))
    ato_status: Mapped[Optional[str]] = mapped_column(String(60))
    ato_expiration_date: Mapped[Optional[date]] = mapped_column(Date)
    poams_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)
