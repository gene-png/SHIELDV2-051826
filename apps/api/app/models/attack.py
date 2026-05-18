"""MITRE ATT&CK reference data + coverage findings."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import CoverageStatus


class AttackTechnique(TimestampMixin, Base):
    """Vendored MITRE ATT&CK Enterprise reference. Refresh quarterly."""

    __tablename__ = "attack_techniques"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tactic: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_sources: Mapped[list[str]] = mapped_column(JSONB, default=list)
    platforms: Mapped[list[str]] = mapped_column(JSONB, default=list)
    vendored_at: Mapped[Optional[str]] = mapped_column(String(40))


class AttackFinding(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "attack_findings"
    __table_args__ = (
        UniqueConstraint("service_id", "technique_id", name="uq_attack_findings_svc_tech"),
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    technique_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("attack_techniques.id"), nullable=False, index=True
    )
    coverage_status: Mapped[CoverageStatus] = mapped_column(
        String(20), nullable=False, default=CoverageStatus.UNCOVERED
    )
    detection_tools: Mapped[list[str]] = mapped_column(JSONB, default=list)
    prevention_tools: Mapped[list[str]] = mapped_column(JSONB, default=list)
    response_tools: Mapped[list[str]] = mapped_column(JSONB, default=list)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    confidence_pct: Mapped[Optional[int]] = mapped_column(Integer)
