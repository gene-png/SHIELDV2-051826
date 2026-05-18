"""Vendor + load MITRE ATT&CK Enterprise techniques into `attack_techniques`.

Real STIX vendor lives at packages/attack-data/enterprise-attack.json (not yet
checked in — refresh quarterly per Master Spec §10). Until then we simply load
the curated subset and tag it as the active reference. The curated loader
covers ~30 techniques; the full 600+ load runs the same upsert path against a
larger source file.

Idempotent: upserts by id (e.g. `T1078`).
"""

from __future__ import annotations

import json

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.attack import AttackTechnique
from app.spine.db import SessionLocal
from apps.api.scripts._common import PACKAGES, print_progress

LOADER = "attack_techniques"
FULL_SOURCE = PACKAGES / "attack-data" / "enterprise-attack.json"
FALLBACK_SOURCE = PACKAGES / "attack-data" / "curated_subset.json"


def main() -> None:
    source = FULL_SOURCE if FULL_SOURCE.exists() else FALLBACK_SOURCE
    data = json.loads(source.read_text(encoding="utf-8"))
    techniques = data.get("techniques", [])
    print_progress(LOADER, f"loading {len(techniques)} techniques from {source.name}")

    with SessionLocal() as db:
        for t in techniques:
            stmt = pg_insert(AttackTechnique).values(
                id=t["id"],
                name=t["name"],
                tactic=t["tactic"],
                description=t.get("description"),
                data_sources=t.get("data_sources", []),
                platforms=t.get("platforms", []),
                vendored_at=data.get("vendored_at"),
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[AttackTechnique.id],
                set_={
                    "name": stmt.excluded.name,
                    "tactic": stmt.excluded.tactic,
                    "description": stmt.excluded.description,
                    "data_sources": stmt.excluded.data_sources,
                    "platforms": stmt.excluded.platforms,
                    "vendored_at": stmt.excluded.vendored_at,
                },
            )
            db.execute(stmt)
        db.commit()
    if source == FALLBACK_SOURCE:
        print_progress(
            LOADER,
            "loaded curated subset only — vendor the full MITRE ATT&CK STIX bundle to "
            "packages/attack-data/enterprise-attack.json for full coverage",
        )


if __name__ == "__main__":
    main()
