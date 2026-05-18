"""Load DoD ZT Reference Architecture questionnaire into `questions`.

Source: packages/zt-data/dod_questions.json (extracted from
reference-docs/SHIELDv2_DoD_ZT_Questionnaire.docx).

Idempotent: upserts by (framework_key, external_id).
"""

from __future__ import annotations

import json

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.questionnaire import Question
from app.spine.db import SessionLocal
from apps.api.scripts._common import PACKAGES, print_progress

LOADER = "dod_zt_questions"
SOURCE = PACKAGES / "zt-data" / "dod_questions.json"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    framework_key = data["framework_key"]
    print_progress(LOADER, f"loading {len(data['questions'])} questions for {framework_key}")

    with SessionLocal() as db:
        for q in data["questions"]:
            stmt = pg_insert(Question).values(
                framework_key=framework_key,
                external_id=q["external_id"],
                pillar=q["pillar"],
                order_index=int(q.get("order_index", 0)),
                stem=q["stem"],
                cues=q.get("cues", []),
                phase=q.get("phase"),
                framework_activities=q.get("framework_activities", []),
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["framework_key", "external_id"],
                set_={
                    "pillar": stmt.excluded.pillar,
                    "order_index": stmt.excluded.order_index,
                    "stem": stmt.excluded.stem,
                    "cues": stmt.excluded.cues,
                    "phase": stmt.excluded.phase,
                    "framework_activities": stmt.excluded.framework_activities,
                },
            )
            db.execute(stmt)
        db.commit()
    print_progress(LOADER, "done")


if __name__ == "__main__":
    main()
