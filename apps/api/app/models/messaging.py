"""Lightweight messages — thread-keyed."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin


class Message(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    thread_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    read_by: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
