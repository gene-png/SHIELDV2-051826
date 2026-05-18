"""Questionnaire questions (static seed) and per-engagement responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class Question(UuidPkMixin, TimestampMixin, Base):
    """Static seed loaded from packages/zt-data and packages/csf-data."""

    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("framework_key", "external_id", name="uq_questions_framework_external_id"),)

    framework_key: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(40), nullable=False)
    pillar: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    cues: Mapped[list[str]] = mapped_column(JSONB, default=list)
    phase: Mapped[Optional[str]] = mapped_column(String(40))
    framework_activities: Mapped[list[str]] = mapped_column(JSONB, default=list)


class QuestionnaireResponse(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "questionnaire_responses"
    __table_args__ = (
        UniqueConstraint(
            "service_id", "system_id", "question_id", name="uq_qresp_service_system_question"
        ),
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    system_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("systems.id")
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True
    )
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    current_state_score: Mapped[Optional[str]] = mapped_column(String(40))
    target_state_score: Mapped[Optional[str]] = mapped_column(String(40))
    target_state_notes: Mapped[Optional[str]] = mapped_column(Text)
    not_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    not_applicable_reason: Mapped[Optional[str]] = mapped_column(Text)
    evidence_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    locked_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
