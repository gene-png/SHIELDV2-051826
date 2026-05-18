"""Canonical enums for SHIELD models. Display labels live in
packages/design-system/labels.ts — Master Spec §14 forbids exposing raw enum
slugs in user-facing surfaces.
"""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    CLIENT = "client"


class ServiceType(StrEnum):
    TECH_DEBT = "tech_debt"
    ZERO_TRUST = "zero_trust"
    CSF = "csf"
    ATTACK_SURFACE = "attack_surface"


class ServiceFramework(StrEnum):
    """Optional framework selector. Only `ZERO_TRUST` services set this."""

    CISA = "cisa"
    DOD = "dod"


class ServiceStatus(StrEnum):
    NEW = "new"
    INTAKE_PENDING = "intake_pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    READY_FOR_RELEASE = "ready_for_release"
    RELEASED = "released"
    ARCHIVED = "archived"


class TierLevel(StrEnum):
    """FIPS 199 categorization tier for CSF systems."""

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class MaturityCisaLevel(StrEnum):
    TRADITIONAL = "traditional"
    INITIAL = "initial"
    ADVANCED = "advanced"
    OPTIMAL = "optimal"


class MaturityDodPhase(StrEnum):
    TARGET = "target"
    ADVANCED = "advanced"


class GapPriority(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class CoverageStatus(StrEnum):
    COVERED = "covered"
    PARTIAL = "partial"
    UNCOVERED = "uncovered"


class ArtifactOrigin(StrEnum):
    CLIENT_UPLOAD = "client_upload"
    AUTOMATED_DRAFT = "automated_draft"
    CONSULTANT_APPROVED = "consultant_approved"
    SYSTEM = "system"


class LlmCallMode(StrEnum):
    REAL = "real"
    FIXTURE = "fixture"


class LlmCallStatus(StrEnum):
    QUEUED = "queued"
    PENDING_REDACTION_REVIEW = "pending_redaction_review"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliverableStatus(StrEnum):
    DRAFT = "draft"
    FINAL = "final"
    RELEASED = "released"
    SUPERSEDED = "superseded"


class PiiKind(StrEnum):
    """PII kinds the redactor strips. Master Spec §12."""

    EMAIL = "email"
    PHONE = "phone"
    PERSON_NAME = "person_name"
    STREET_ADDRESS = "street_address"
    CLIENT_ORG_NAME = "client_org_name"
    SSN = "ssn"
    EIN = "ein"
    CAGE_CODE = "cage_code"
    CONTRACT_NUMBER = "contract_number"
    SIGNATURE_BLOCK = "signature_block"
