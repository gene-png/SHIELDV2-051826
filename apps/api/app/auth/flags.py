"""Feature-flag enforcement for MFA and email verification.

Both are deferred for v1 (`SHIELD_AUTH_REQUIRE_MFA=false`,
`SHIELD_AUTH_REQUIRE_EMAIL_VERIFY=false`). The enforcement helpers below keep
the same call-site shape so flipping the flag in v1.x activates the
requirement without touching any router code (Master Spec §4.5 / §6.1).
"""

from __future__ import annotations

from fastapi import HTTPException, status

from app.models.identity import User
from app.settings import get_settings


def require_mfa_if_enforced(user: User) -> None:
    settings = get_settings()
    if not settings.shield_auth_require_mfa:
        return
    if not user.mfa_enrolled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="MFA enrollment required"
        )


def require_email_verified_if_enforced(user: User) -> None:
    settings = get_settings()
    if not settings.shield_auth_require_email_verify:
        return
    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email verification required"
        )
