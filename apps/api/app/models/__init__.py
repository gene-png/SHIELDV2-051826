"""SQLAlchemy models. Importing this package registers every table on Base.metadata."""

from app.models.base import Base, TimestampMixin, TenantScopedMixin
from app.models.enums import (
    ArtifactOrigin,
    CoverageStatus,
    DeliverableStatus,
    GapPriority,
    LlmCallMode,
    LlmCallStatus,
    MaturityCisaLevel,
    MaturityDodPhase,
    PiiKind,
    Role,
    ServiceFramework,
    ServiceStatus,
    ServiceType,
    TierLevel,
)

# Import every model module so SQLAlchemy registers the tables.
from app.models import (  # noqa: F401  (registration side effects)
    ai,
    artifact,
    audit,
    csf,
    deliverable,
    gap,
    identity,
    messaging,
    notification,
    org,
    questionnaire,
    review,
    service,
    service_request,
    tech_debt,
    attack,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "TenantScopedMixin",
    "ArtifactOrigin",
    "CoverageStatus",
    "DeliverableStatus",
    "GapPriority",
    "LlmCallMode",
    "LlmCallStatus",
    "MaturityCisaLevel",
    "MaturityDodPhase",
    "PiiKind",
    "Role",
    "ServiceFramework",
    "ServiceStatus",
    "ServiceType",
    "TierLevel",
]
