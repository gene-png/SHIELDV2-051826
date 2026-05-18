"""File artifacts + redaction lineage."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import ArtifactOrigin


class Artifact(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "artifacts"

    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lineage: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    origin: Mapped[ArtifactOrigin] = mapped_column(String(40), nullable=False)
    stage: Mapped[Optional[str]] = mapped_column(String(60))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[Optional[str]] = mapped_column(String(80))

    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    archived_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    purged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    purged_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )


class ArtifactRedaction(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """Audit trail of every PII strip event (Master Spec §12)."""

    __tablename__ = "artifact_redactions"

    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=False, index=True
    )
    redacted_payload_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )
    redacted_items: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence: Mapped[Optional[int]] = mapped_column(Integer)
    llm_call_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_calls.id")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
