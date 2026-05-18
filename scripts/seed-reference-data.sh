#!/usr/bin/env bash
# Run every reference-data loader. Idempotent — each loader upserts.
# Expects to be run from inside the api container (or anywhere with the
# project venv active) so `python -m apps.api.scripts.*` resolves.
set -euo pipefail

cd "$(dirname "$0")/.."

run() {
  echo ""
  echo "[seed] >>> $*"
  python -m "$@"
}

run apps.api.scripts.load_csf_subcategories "$@"
run apps.api.scripts.load_cisa_zt_questions
run apps.api.scripts.load_dod_zt_questions
run apps.api.scripts.load_csf_tier_questionnaires
run apps.api.scripts.load_attack_techniques
run apps.api.scripts.load_label_map

echo ""
echo "[seed] done."
