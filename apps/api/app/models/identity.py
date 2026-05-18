"""Users and invitations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin, TimestampMixin, UuidPkMixin
from app.models.enums import Role


class User(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(String(20), nullable=False, default=Role.CLIENT)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(120))
    phone: Mapped[Optional[str]] = mapped_column(String(40))
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_primary_poc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_executive_viewer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_enrolled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    intake_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    notification_prefs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class UserInvitation(UuidPkMixin, TenantScopedMixin, TimestampMixin, Base):
    """7-day, single-use, hashed invitation token (Master Spec §5)."""

    __tablename__ = "user_invitations"

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    message: Mapped[Optional[str]] = mapped_column(String(2048))
    role_invited_as: Mapped[Role] = mapped_column(String(20), nullable=False, default=Role.CLIENT)
