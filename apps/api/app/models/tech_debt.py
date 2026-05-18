"""Tech Debt service — capability list + items."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class CapabilityList(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "capability_list"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )


class CapabilityItem(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "capability_items"

    capability_list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capability_list.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[Optional[str]] = mapped_column(String(120))
    function: Mapped[Optional[str]] = mapped_column(String(120))
    annual_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    license_count: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    confidence_pct: Mapped[Optional[int]] = mapped_column(Integer)
    source_artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )
