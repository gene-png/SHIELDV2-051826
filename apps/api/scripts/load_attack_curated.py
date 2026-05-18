"""Mark the Kentro curated ATT&CK subset.

In v1 this is a thin wrapper around `load_attack_techniques.py` — the curated
JSON IS the source. When the full STIX bundle ships, this loader will instead
flag the curated 33–40 within the larger `attack_techniques` table.

Owner of the final curated list: Eugene Powell (TBD per execution plan §19).
"""

from __future__ import annotations

from apps.api.scripts import load_attack_techniques

if __name__ == "__main__":
    load_attack_techniques.main()
