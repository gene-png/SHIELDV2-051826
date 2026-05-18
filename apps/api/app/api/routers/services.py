"""Service-listing endpoints. Master Spec §7 — client-facing read paths.

The admin / reviewer service workspaces ship with §8 of the execution plan.
This file only covers the read-only client view (list + per-service detail).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.services import ServiceSummary
from app.auth.dependencies import CurrentUser, get_current_user
from app.models.service import Service
from app.spine.db import get_db

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("/mine", response_model=list[ServiceSummary])
def my_services(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[ServiceSummary]:
    rows = (
        db.execute(
            select(Service)
            .where(Service.client_id == user.client_id)
            .order_by(Service.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [
        ServiceSummary(
            id=r.id,
            type=r.type,
            framework=r.framework,
            status=r.status,
            headline=r.headline,
            released_at=r.released_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.get("/{service_id}", response_model=ServiceSummary)
def service_detail(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> ServiceSummary:
    svc = db.get(Service, service_id)
    if svc is None or svc.client_id != user.client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return ServiceSummary(
        id=svc.id,
        type=svc.type,
        framework=svc.framework,
        status=svc.status,
        headline=svc.headline,
        released_at=svc.released_at,
        updated_at=svc.updated_at,
    )
