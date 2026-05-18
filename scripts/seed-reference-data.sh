#!/usr/bin/env bash
# Run every reference-data loader. Idempotent — each loader upserts.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[seed] loading CSF subcategories..."
python apps/api/scripts/load_csf_subcategories.py "$@"

echo "[seed] loading CISA ZT questions..."
python apps/api/scripts/load_cisa_zt_questions.py

echo "[seed] loading DoD ZT questions..."
python apps/api/scripts/load_dod_zt_questions.py

echo "[seed] loading CSF tier questionnaires..."
python apps/api/scripts/load_csf_tier_questionnaires.py

echo "[seed] vendoring + loading MITRE ATT&CK..."
python apps/api/scripts/load_attack_techniques.py

echo "[seed] loading ATT&CK curated subset (stub mode until Eugene supplies)..."
python apps/api/scripts/load_attack_curated.py --stub

echo "[seed] loading label map..."
python apps/api/scripts/load_label_map.py

echo "[seed] done."
