"""LLM call ledger. Every outbound call writes a row. Master Spec §4.4 / §12."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import LlmCallMode, LlmCallStatus


class LlmCall(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "llm_calls"

    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), index=True
    )
    purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(40), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    mode: Mapped[LlmCallMode] = mapped_column(String(20), nullable=False, default=LlmCallMode.REAL)
    status: Mapped[LlmCallStatus] = mapped_column(
        String(40), nullable=False, default=LlmCallStatus.QUEUED, index=True
    )

    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    error_message: Mapped[Optional[str]] = mapped_column(Text)
    response_artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )
    redaction_summary: Mapped[Optional[str]] = mapped_column(Text)
