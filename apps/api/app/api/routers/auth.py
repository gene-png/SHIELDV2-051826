"""Authentication endpoints.

Master Spec §6.1 — v1 ships without MFA or email verification; both flows are
feature-flag-gated so flipping them on later requires no code changes here.

Flows wired:
- POST /api/auth/signup          create the first user / additional users
- POST /api/auth/sign-in         credentials → access token
- POST /api/auth/sign-out        no-op besides the audit row (tokens expire)
- POST /api/auth/accept-invite   accept a hashed `user_invitations` token
- POST /api/auth/change-password verify current, rotate to Argon2id
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.auth import (
    AcceptInviteRequest,
    AuthUserOut,
    ChangePasswordRequest,
    SignInRequest,
    SignInResponse,
    SignUpRequest,
    SignUpResponse,
)
from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.jwt import issue_access_token
from app.auth.passwords import hash_password, verify_password
from app.auth.session import (
    clear_failed_attempts,
    current_state,
    record_failed_attempt,
)
from app.models.enums import Role
from app.models.identity import User, UserInvitation
from app.models.org import Client
from app.spine.audit import audit
from app.spine.db import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ensure_client_singleton(db: Session) -> Client:
    """First call on a fresh deployment provisions the `client` row. Subsequent
    calls return the existing singleton. Master Spec §11 — exactly one row."""
    existing = db.execute(select(Client)).scalar_one_or_none()
    if existing is not None:
        return existing
    client = Client(legal_name="(pending intake)", address_json={})
    # client_id is mandated on every row by TenantScopedMixin; the singleton
    # references itself.
    new_id = uuid.uuid4()
    client.id = new_id
    client.client_id = new_id
    db.add(client)
    db.flush()
    return client


def _hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _user_to_out(user: User) -> AuthUserOut:
    return AuthUserOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        is_primary_poc=user.is_primary_poc,
        mfa_enrolled=user.mfa_enrolled,
        email_verified_at=user.email_verified_at,
    )


# ---------------------------------------------------------------------------
# signup
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
def signup(
    body: SignUpRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SignUpResponse:
    if not body.accept_terms:
        raise HTTPException(status_code=400, detail="Terms must be accepted")

    if db.execute(select(User).where(User.email == body.email)).scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    client = _ensure_client_singleton(db)

    # First user → Primary POC. Atomic with the user insert so a concurrent
    # signup can't race ahead (Master Spec §6.1 — Eugene's TBD; this is the
    # plan's accepted "developer judgment per spec §1 Q2" resolution).
    is_first_user = db.execute(select(User).limit(1)).scalar_one_or_none() is None

    user = User(
        client_id=client.id,
        email=body.email,
        password_hash=hash_password(body.password),
        role=Role.CLIENT,
        display_name=body.display_name,
        is_primary_poc=is_first_user,
        last_login_at=datetime.now(tz=timezone.utc),
    )
    db.add(user)
    db.flush()

    if is_first_user and client.primary_poc_user_id is None:
        client.primary_poc_user_id = user.id

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=client.id,
        actor_user_id=user.id,
        action="user.signup",
        target_type="users",
        target_id=str(user.id),
        details={"email": body.email, "is_first_user": is_first_user},
        correlation_id=correlation_id,
    )
    db.commit()

    access_token, ttl = issue_access_token(
        user_id=user.id,
        client_id=client.id,
        role=user.role.value,
        email=user.email,
        display_name=user.display_name,
    )
    return SignUpResponse(access_token=access_token, expires_in=ttl, user=_user_to_out(user))


# ---------------------------------------------------------------------------
# sign-in
# ---------------------------------------------------------------------------

@router.post("/sign-in", response_model=SignInResponse)
def sign_in(
    body: SignInRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SignInResponse:
    lockout = current_state(body.email)
    if lockout.locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Try again in {lockout.retry_after_seconds}s.",
        )

    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
    correlation_id = getattr(request.state, "correlation_id", "")

    if user is None or not user.is_active or not verify_password(user.password_hash, body.password):
        new_state = record_failed_attempt(body.email)
        # Audit even on failure — Master Spec §4.1: every auth event writes a row.
        if user is not None:
            audit(
                db,
                client_id=user.client_id,
                actor_user_id=None,
                action="user.sign_in_failed",
                target_type="users",
                target_id=str(user.id),
                details={"email": body.email, "attempts": new_state.attempts},
                correlation_id=correlation_id,
            )
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    clear_failed_attempts(body.email)
    user.last_login_at = datetime.now(tz=timezone.utc)
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.id,
        action="user.sign_in",
        target_type="users",
        target_id=str(user.id),
        correlation_id=correlation_id,
    )
    db.commit()

    access_token, ttl = issue_access_token(
        user_id=user.id,
        client_id=user.client_id,
        role=user.role.value,
        email=user.email,
        display_name=user.display_name,
    )
    return SignInResponse(access_token=access_token, expires_in=ttl, user=_user_to_out(user))


# ---------------------------------------------------------------------------
# sign-out
# ---------------------------------------------------------------------------

@router.post("/sign-out")
def sign_out(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="user.sign_out",
        target_type="users",
        target_id=str(user.user_id),
        correlation_id=correlation_id,
    )
    db.commit()
    # JWT is stateless; the access token simply expires. A future refresh-token
    # store would revoke here.
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# accept invitation
# ---------------------------------------------------------------------------

@router.post("/accept-invite", response_model=SignInResponse)
def accept_invite(
    body: AcceptInviteRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SignInResponse:
    token_hash = _hash_invite_token(body.token)
    invitation = db.execute(
        select(UserInvitation).where(UserInvitation.token_hash == token_hash)
    ).scalar_one_or_none()
    if invitation is None or invitation.revoked_at or invitation.accepted_at:
        raise HTTPException(status_code=400, detail="Invitation is no longer valid.")
    if invitation.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation has expired.")

    # Reuse signup path semantics (no terms checkbox on invite acceptance — the
    # inviter is the surface that surfaced the terms).
    if db.execute(select(User).where(User.email == invitation.email)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    user = User(
        client_id=invitation.client_id,
        email=invitation.email,
        password_hash=hash_password(body.password),
        role=invitation.role_invited_as,
        display_name=body.display_name,
        last_login_at=datetime.now(tz=timezone.utc),
    )
    db.add(user)
    db.flush()

    invitation.accepted_at = datetime.now(tz=timezone.utc)

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=invitation.client_id,
        actor_user_id=user.id,
        action="user.invite_accepted",
        target_type="user_invitations",
        target_id=str(invitation.id),
        correlation_id=correlation_id,
    )
    db.commit()

    access_token, ttl = issue_access_token(
        user_id=user.id,
        client_id=user.client_id,
        role=user.role.value,
        email=user.email,
        display_name=user.display_name,
    )
    return SignInResponse(access_token=access_token, expires_in=ttl, user=_user_to_out(user))


# ---------------------------------------------------------------------------
# change password
# ---------------------------------------------------------------------------

@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    user = db.get(User, current.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    if not verify_password(user.password_hash, body.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    user.password_hash = hash_password(body.new_password)
    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.id,
        action="user.change_password",
        target_type="users",
        target_id=str(user.id),
        correlation_id=correlation_id,
    )
    db.commit()
    return {"status": "ok"}
