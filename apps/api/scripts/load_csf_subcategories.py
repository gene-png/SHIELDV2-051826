"""Load CSF 2.0 subcategories into `csf_subcategories`.

Idempotent: upserts by primary key (e.g. `GV.OC-01`). Until Eugene supplies the
full Reference Data CSV with IG metric alignment + FISMA domain mapping, this
loader runs in **stub mode** — `ig_metrics`, `alignment`, `fisma_domain`,
`interview_topic_family`, and `question_summary` are all null. CSF rollup Rule 2
and Rule 5 will short-circuit (logged on the enterprise entry) until those
columns are populated.

Usage:
    python -m apps.api.scripts.load_csf_subcategories
    python -m apps.api.scripts.load_csf_subcategories --csv path/to/full_reference.csv
"""

from __future__ import annotations

import argparse
import csv

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.csf import CsfSubcategory
from app.spine.db import SessionLocal
from apps.api.scripts._common import PACKAGES, die, print_progress

LOADER = "csf_subcategories"
DEFAULT_CSV = PACKAGES / "csf-data" / "csf_2_0_subcategories.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=str, default=str(DEFAULT_CSV))
    args = parser.parse_args()

    csv_path = args.csv
    try:
        rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    except FileNotFoundError:
        die(LOADER, f"CSV not found at {csv_path}")
        return

    if not rows:
        die(LOADER, f"CSV at {csv_path} is empty")
        return

    print_progress(LOADER, f"upserting {len(rows)} subcategories from {csv_path}")

    with SessionLocal() as db:
        for row in rows:
            stmt = pg_insert(CsfSubcategory).values(
                id=row["id"],
                function=row["function"],
                category=row["category"],
                description=row["description"],
                ig_metrics={},
                alignment=row.get("alignment") or None,
                fisma_domain=row.get("fisma_domain") or None,
                interview_topic_family=row.get("interview_topic_family") or None,
                question_summary=row.get("question_summary") or None,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[CsfSubcategory.id],
                set_={
                    "function": stmt.excluded.function,
                    "category": stmt.excluded.category,
                    "description": stmt.excluded.description,
                    "alignment": stmt.excluded.alignment,
                    "fisma_domain": stmt.excluded.fisma_domain,
                    "interview_topic_family": stmt.excluded.interview_topic_family,
                    "question_summary": stmt.excluded.question_summary,
                },
            )
            db.execute(stmt)
        db.commit()

    print_progress(LOADER, f"upserted {len(rows)} subcategories — STUB mode (no IG metrics yet)")


if __name__ == "__main__":
    main()
