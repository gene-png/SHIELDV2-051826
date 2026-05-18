"""Declarative base + common mixins.

Every table carries:
- `id` UUID primary key (uuid4 default)
- `client_id` UUID — defense-in-depth column even though deployments are
  single-tenant (Master Spec §1, line 1707 in reference-docs/SHIELDv2_Master_Spec.txt)
- `created_at` / `updated_at` timestamps in UTC

`audit_entries` and a few static reference tables (e.g. `csf_subcategories`)
opt out of one or more of these via direct column declarations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class TenantScopedMixin:
    """Adds `client_id` to a model. Singletons (e.g. `client`) and static
    reference tables (e.g. `csf_subcategories`) skip this mixin."""

    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)


class UuidPkMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
