"""Artifact lineage helpers. Lineage JSONB lives on every `artifacts` row and
records provenance, redaction proof, and consultant-approval timestamps.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def new_lineage(*, origin: str, source_artifact_ids: list[uuid.UUID] | None = None) -> dict[str, Any]:
    return {
        "origin": origin,
        "sources": [str(s) for s in (source_artifact_ids or [])],
        "redaction": None,
        "transforms": [],
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def attach_redaction(lineage: dict[str, Any], *, redaction_id: uuid.UUID, summary: dict[str, int]) -> None:
    lineage["redaction"] = {
        "id": str(redaction_id),
        "summary": summary,
        "at": datetime.now(tz=timezone.utc).isoformat(),
    }


def append_transform(lineage: dict[str, Any], *, name: str, by: uuid.UUID | None = None) -> None:
    lineage.setdefault("transforms", []).append(
        {
            "name": name,
            "by": str(by) if by else None,
            "at": datetime.now(tz=timezone.utc).isoformat(),
        }
    )
