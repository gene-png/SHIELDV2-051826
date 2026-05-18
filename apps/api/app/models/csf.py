"""NIST CSF 2.0 reference data + tier profiles + enterprise rollup.

Master Spec §8 — 5-dimension scoring (G, P, I, M, C ∈ {0,1,2}), total ∈ {0..10},
maturity ∈ {1..5}. Enterprise rollup runs Rules 1–6 against tier profile entries.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import TierLevel


class CsfSubcategory(TimestampMixin, Base):
    """Static seed: 108 subcategory rows. ID = e.g. `GV.OC-01`."""

    __tablename__ = "csf_subcategories"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    function: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ig_metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    alignment: Mapped[Optional[str]] = mapped_column(String(40))
    fisma_domain: Mapped[Optional[str]] = mapped_column(String(80))
    interview_topic_family: Mapped[Optional[str]] = mapped_column(String(120))
    question_summary: Mapped[Optional[str]] = mapped_column(Text)


class CsfTierProfileEntry(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "csf_tier_profile_entries"
    __table_args__ = (
        UniqueConstraint(
            "service_id", "tier", "subcategory_id", name="uq_csf_tpe_service_tier_subcat"
        ),
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    tier: Mapped[TierLevel] = mapped_column(String(20), nullable=False)
    subcategory_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("csf_subcategories.id"), nullable=False
    )

    in_scope: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    narrative: Mapped[Optional[str]] = mapped_column(Text)
    evidence_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)

    dim_g: Mapped[Optional[int]] = mapped_column(Integer)
    dim_p: Mapped[Optional[int]] = mapped_column(Integer)
    dim_i: Mapped[Optional[int]] = mapped_column(Integer)
    dim_m: Mapped[Optional[int]] = mapped_column(Integer)
    dim_c: Mapped[Optional[int]] = mapped_column(Integer)
    total_auto: Mapped[Optional[int]] = mapped_column(Integer)
    maturity_level_auto: Mapped[Optional[int]] = mapped_column(Integer)

    target_maturity: Mapped[Optional[int]] = mapped_column(Integer)
    gap_auto: Mapped[Optional[int]] = mapped_column(Integer)

    draft: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CsfEnterpriseEntry(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """One row per subcategory after roll-up. `tier_driver_rule` records which
    of Rules 1–6 fired (Master Spec §8)."""

    __tablename__ = "csf_enterprise_entries"
    __table_args__ = (
        UniqueConstraint("service_id", "subcategory_id", name="uq_csf_ee_service_subcat"),
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service.id"), nullable=False, index=True
    )
    subcategory_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("csf_subcategories.id"), nullable=False
    )

    narrative: Mapped[Optional[str]] = mapped_column(Text)
    dim_g: Mapped[Optional[int]] = mapped_column(Integer)
    dim_p: Mapped[Optional[int]] = mapped_column(Integer)
    dim_i: Mapped[Optional[int]] = mapped_column(Integer)
    dim_m: Mapped[Optional[int]] = mapped_column(Integer)
    dim_c: Mapped[Optional[int]] = mapped_column(Integer)
    total_auto: Mapped[Optional[int]] = mapped_column(Integer)
    current_maturity_auto: Mapped[Optional[int]] = mapped_column(Integer)
    target_maturity: Mapped[Optional[int]] = mapped_column(Integer)
    gap_auto: Mapped[Optional[int]] = mapped_column(Integer)

    tier_driver_rule: Mapped[Optional[str]] = mapped_column(String(40))
    notes: Mapped[Optional[str]] = mapped_column(Text)
