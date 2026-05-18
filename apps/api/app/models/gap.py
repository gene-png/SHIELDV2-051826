"""Gap rows produced by every assessment service."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import GapPriority


class Gap(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "gaps"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    framework_key: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subcategory_or_pillar_id: Mapped[str] = mapped_column(String(120), nullable=False)

    characterization: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[GapPriority] = mapped_column(String(4), nullable=False, default=GapPriority.P3)

    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    resources_needed: Mapped[Optional[str]] = mapped_column(Text)
    success_criteria: Mapped[Optional[str]] = mapped_column(Text)
    poam_ref: Mapped[Optional[str]] = mapped_column(String(80))
    initiative_group: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open")
