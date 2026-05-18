"""Deliverable bundles (PDF + XLSX). Versioned and supersedable."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import DeliverableStatus


class Deliverable(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "deliverables"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[DeliverableStatus] = mapped_column(
        String(20), nullable=False, default=DeliverableStatus.DRAFT, index=True
    )

    pdf_artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )
    xlsx_artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )

    finalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finalized_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    released_to_client_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    superseded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliverables.id")
    )
