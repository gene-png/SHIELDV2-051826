"""Service-listing schemas for the client home / services pages."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import ServiceFramework, ServiceStatus, ServiceType


class ServiceSummary(BaseModel):
    id: uuid.UUID
    type: ServiceType
    framework: Optional[ServiceFramework]
    status: ServiceStatus
    headline: Optional[str]
    released_at: Optional[datetime]
    updated_at: datetime
