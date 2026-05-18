"""Pydantic request/response schemas for the auth surface."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Role


class SignUpRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=200)
    accept_terms: bool


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=200)


class AcceptInviteRequest(BaseModel):
    token: str
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=200)


class AuthUserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str
    role: Role
    is_primary_poc: bool
    mfa_enrolled: bool
    email_verified_at: datetime | None


class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserOut


class SignUpResponse(SignInResponse):
    """Same shape — v1 signs the user in immediately on signup."""
