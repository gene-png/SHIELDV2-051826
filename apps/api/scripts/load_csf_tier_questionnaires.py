"""Load CSF tier (HIGH/MOD/LOW) questionnaires into `questions`.

STUB until Eugene supplies the full Kentro Playbook Step 1.1/1.2/1.3 question
banks. The seed file at packages/csf-data/csf_tier_questionnaires.json carries
one representative question per tier so the questionnaire renderer has
something to display end-to-end. Replace before first real engagement.

Idempotent: upserts by (framework_key, external_id).
"""

from __future__ import annotations

import json

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.questionnaire import Question
from app.spine.db import SessionLocal
from apps.api.scripts._common import PACKAGES, print_progress

LOADER = "csf_tier_questionnaires"
SOURCE = PACKAGES / "csf-data" / "csf_tier_questionnaires.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    framework_keys = {"high": "csf-tier-high", "moderate": "csf-tier-moderate", "low": "csf-tier-low"}

    with SessionLocal() as db:
        total = 0
        for tier_id, tier in data["tiers"].items():
            framework_key = framework_keys[tier_id]
            for index, q in enumerate(tier["questions"], start=1):
                stmt = pg_insert(Question).values(
                    framework_key=framework_key,
                    external_id=q["id"],
                    pillar=tier["label"],
                    order_index=index,
                    stem=q["stem"],
                    cues=q.get("cues", []),
                    framework_activities=[],
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["framework_key", "external_id"],
                    set_={
                        "pillar": stmt.excluded.pillar,
                        "order_index": stmt.excluded.order_index,
                        "stem": stmt.excluded.stem,
                        "cues": stmt.excluded.cues,
                    },
                )
                db.execute(stmt)
                total += 1
        db.commit()
    print_progress(LOADER, f"upserted {total} stub questions across HIGH / MOD / LOW")


if __name__ == "__main__":
    main()
