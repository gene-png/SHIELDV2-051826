"""Service requests + consultation requests (the 'I'm not sure' intake path)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class ServiceRequest(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "service_requests"

    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    fulfilled_service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id")
    )
    declined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    declined_reason: Mapped[Optional[str]] = mapped_column(Text)


class ConsultationRequest(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """The 'I'm not sure' short-circuit from intake step I1B. Master Spec §6.2."""

    __tablename__ = "consultation_requests"

    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    role_title: Mapped[Optional[str]] = mapped_column(String(120))
    organization_name: Mapped[Optional[str]] = mapped_column(String(200))
    prompt_text: Mapped[Optional[str]] = mapped_column(Text)
    contact_preference: Mapped[Optional[str]] = mapped_column(String(40))
    phone: Mapped[Optional[str]] = mapped_column(String(40))
    preferred_time: Mapped[Optional[str]] = mapped_column(String(120))
    additional_notes: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending", index=True)
