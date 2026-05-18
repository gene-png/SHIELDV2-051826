"""Intake wizard endpoints. Master Spec §6.2 (I1–I6).

The wizard writes draft state across multiple resources, then `submit`
finalizes by creating `service` rows and dispatching admin notifications.
Each step is independently call-able so the autosave pattern works.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.intake import (
    ConsultationRequestPayload,
    IntakeStatusResponse,
    IntakeSubmitResponse,
    OrganizationPayload,
    ServiceSelectionRequest,
    SystemsRequest,
)
from app.auth.dependencies import CurrentUser, get_current_user
from app.models.enums import Role, ServiceStatus, ServiceType
from app.models.identity import User
from app.models.org import Client
from app.models.service import Service, System
from app.models.service_request import ConsultationRequest
from app.spine.audit import audit
from app.spine.db import get_db

router = APIRouter(prefix="/api/intake", tags=["intake"])


def _require_client(user: CurrentUser) -> None:
    if user.role != Role.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Intake is for client users only.",
        )


@router.get("/status", response_model=IntakeStatusResponse)
def status_endpoint(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> IntakeStatusResponse:
    _require_client(user)
    client = db.get(Client, user.client_id)
    services = db.execute(
        select(Service).where(Service.client_id == user.client_id)
    ).scalars().all()
    systems = db.execute(
        select(System).where(System.client_id == user.client_id)
    ).scalars().all()

    selected = list({ServiceType(s.type) for s in services})
    framework = next((s.framework for s in services if s.framework), None)

    return IntakeStatusResponse(
        selected_services=selected,
        framework=framework,
        org_complete=bool(client and client.legal_name and client.legal_name != "(pending intake)"),
        systems_complete=len(systems) > 0,
        questionnaire_progress_pct=0,
        artifacts_uploaded=0,
        can_submit=False,
    )


@router.post("/service-selection", status_code=status.HTTP_204_NO_CONTENT)
def select_services(
    body: ServiceSelectionRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> None:
    _require_client(user)

    if body.not_sure and body.services:
        raise HTTPException(status_code=400, detail="Choose specific services OR consultation, not both.")

    # Wipe any prior draft selection on this deployment and re-create from input.
    db.execute(
        select(Service).where(
            Service.client_id == user.client_id,
            Service.status == ServiceStatus.NEW,
        )
    )
    # Use a delete loop rather than a raw DELETE so triggers fire if a future
    # version adds them; the volume is tiny.
    existing = db.execute(
        select(Service).where(
            Service.client_id == user.client_id,
            Service.status == ServiceStatus.NEW,
        )
    ).scalars().all()
    for svc in existing:
        db.delete(svc)

    for stype in body.services:
        svc = Service(
            client_id=user.client_id,
            type=stype,
            framework=body.framework if stype == ServiceType.ZERO_TRUST else None,
            status=ServiceStatus.NEW,
        )
        db.add(svc)

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="intake.service_selection",
        target_type="service",
        details={
            "selected": [s.value for s in body.services],
            "framework": body.framework.value if body.framework else None,
            "not_sure": body.not_sure,
        },
        correlation_id=correlation_id,
    )
    db.commit()


@router.post("/consultation-request", status_code=status.HTTP_201_CREATED)
def consultation_request(
    body: ConsultationRequestPayload,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    _require_client(user)
    cr = ConsultationRequest(
        client_id=user.client_id,
        requested_by=user.user_id,
        role_title=body.role_title,
        organization_name=body.organization_name,
        prompt_text=body.prompt_text,
        contact_preference=body.contact_preference,
        phone=body.phone,
        preferred_time=body.preferred_time,
        additional_notes=body.additional_notes,
        status="pending",
    )
    db.add(cr)
    correlation_id = getattr(request.state, "correlation_id", "")
    db.flush()
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="intake.consultation_requested",
        target_type="consultation_requests",
        target_id=str(cr.id),
        correlation_id=correlation_id,
    )
    db.commit()
    return {"status": "pending", "id": str(cr.id)}


@router.post("/organization", status_code=status.HTTP_204_NO_CONTENT)
def update_organization(
    body: OrganizationPayload,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> None:
    _require_client(user)
    client = db.get(Client, user.client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="client singleton missing")

    client.legal_name = body.legal_name
    client.dba_name = body.dba_name
    client.website = body.website
    client.size_band = body.size_band
    client.industry = body.industry
    client.address_json = {
        "street": body.address_street,
        "city": body.address_city,
        "state": body.address_state,
        "postal_code": body.address_postal_code,
        "country": body.address_country,
    }
    client.compliance_deadline = body.compliance_deadline

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="intake.organization_saved",
        target_type="client",
        target_id=str(client.id),
        correlation_id=correlation_id,
    )
    db.commit()


@router.post("/systems", status_code=status.HTTP_204_NO_CONTENT)
def upsert_systems(
    body: SystemsRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> None:
    _require_client(user)

    # Replace the system list. Clients rarely have more than a dozen rows so a
    # simple delete-then-insert is cleaner than diff'ing.
    existing = db.execute(
        select(System).where(System.client_id == user.client_id)
    ).scalars().all()
    for s in existing:
        db.delete(s)
    db.flush()

    # Resolve owner / ISSO emails to users when they already exist in the
    # deployment; otherwise leave the FK null and capture in notes.
    for s in body.systems:
        owner = None
        isso = None
        if s.owner_email:
            owner = db.execute(
                select(User).where(User.email == s.owner_email)
            ).scalar_one_or_none()
        if s.isso_email:
            isso = db.execute(
                select(User).where(User.email == s.isso_email)
            ).scalar_one_or_none()
        db.add(
            System(
                client_id=user.client_id,
                name=s.name,
                csam_id=s.csam_id,
                fips_categorization=s.fips_categorization,
                owner_user_id=owner.id if owner else None,
                isso_user_id=isso.id if isso else None,
                hosting=s.hosting,
                ato_status=s.ato_status,
                ato_expiration_date=s.ato_expiration_date,
                notes=s.notes,
            )
        )

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="intake.systems_saved",
        target_type="systems",
        details={"count": len(body.systems)},
        correlation_id=correlation_id,
    )
    db.commit()


@router.post("/submit", response_model=IntakeSubmitResponse)
def submit_intake(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> IntakeSubmitResponse:
    _require_client(user)

    services = db.execute(
        select(Service).where(
            Service.client_id == user.client_id,
            Service.status == ServiceStatus.NEW,
        )
    ).scalars().all()
    if not services:
        raise HTTPException(status_code=400, detail="No services selected. Pick at least one or request a consultation.")

    moved: list[uuid.UUID] = []
    for svc in services:
        svc.status = ServiceStatus.INTAKE_PENDING
        moved.append(svc.id)

    client = db.get(Client, user.client_id)
    if client is not None:
        client.intake_completed_at = datetime.now(tz=timezone.utc)

    correlation_id = getattr(request.state, "correlation_id", "")
    audit(
        db,
        client_id=user.client_id,
        actor_user_id=user.user_id,
        action="intake.submitted",
        target_type="service",
        details={"service_ids": [str(s) for s in moved]},
        correlation_id=correlation_id,
    )
    # Admin notification dispatch lives in §12; for now the audit row is the
    # signal that an admin queue refresh should pick the engagement up.
    db.commit()

    return IntakeSubmitResponse(services_created=moved)
