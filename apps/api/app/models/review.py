"""Reviewer notes. Separated from consultant notes — never visible to consultants."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class ReviewerNote(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "reviewer_notes"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str] = mapped_column(String(80), nullable=False)
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    disposition: Mapped[str] = mapped_column(String(40), nullable=False, default="comment")
