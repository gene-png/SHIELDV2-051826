"""Intake wizard schemas — request/response Pydantic models.

Each intake step writes onto in-progress draft state under the user's account.
`POST /api/intake/submit` is what actually creates `service` rows and fires
admin notifications (Master Spec §6.2 / §11 — no partial service creation).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import ServiceFramework, ServiceType, TierLevel


class ServiceSelectionRequest(BaseModel):
    services: list[ServiceType] = Field(default_factory=list)
    not_sure: bool = False
    framework: Optional[ServiceFramework] = None  # only meaningful when ZERO_TRUST is picked


class ConsultationRequestPayload(BaseModel):
    role_title: Optional[str] = None
    organization_name: Optional[str] = None
    prompt_text: Optional[str] = Field(default=None, max_length=4000)
    contact_preference: Optional[str] = None  # "phone" | "email"
    phone: Optional[str] = None
    preferred_time: Optional[str] = None
    additional_notes: Optional[str] = Field(default=None, max_length=4000)


class OrganizationPayload(BaseModel):
    legal_name: str = Field(min_length=1, max_length=200)
    dba_name: Optional[str] = None
    website: Optional[str] = None
    size_band: Optional[str] = None
    industry: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = "US"
    compliance_deadline: Optional[date] = None


class SystemPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    csam_id: Optional[str] = None
    fips_categorization: Optional[TierLevel] = None
    owner_email: Optional[EmailStr] = None
    isso_email: Optional[EmailStr] = None
    hosting: Optional[str] = None
    ato_status: Optional[str] = None
    ato_expiration_date: Optional[date] = None
    notes: Optional[str] = None


class SystemsRequest(BaseModel):
    systems: list[SystemPayload]


class QuestionResponsePayload(BaseModel):
    question_id: uuid.UUID
    system_id: Optional[uuid.UUID] = None
    answer_text: Optional[str] = None
    current_state_score: Optional[str] = None
    target_state_score: Optional[str] = None
    target_state_notes: Optional[str] = None
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None


class IntakeStatusResponse(BaseModel):
    selected_services: list[ServiceType]
    framework: Optional[ServiceFramework]
    org_complete: bool
    systems_complete: bool
    questionnaire_progress_pct: int
    artifacts_uploaded: int
    can_submit: bool


class IntakeSubmitResponse(BaseModel):
    services_created: list[uuid.UUID]
    home_url: str = "/home"
