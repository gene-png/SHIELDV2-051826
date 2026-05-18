"""Cross-check that the enum→label maps in packages/design-system/enums.yaml
and packages/design-system/labels.ts agree, and that every enum value in
app/models/enums.py has a label.

Doesn't touch the database — this is a build-time invariant check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from apps.api.scripts._common import PACKAGES, print_progress

LOADER = "label_map"
ENUMS_YAML = PACKAGES / "design-system" / "enums.yaml"
LABELS_TS = PACKAGES / "design-system" / "labels.ts"


def _enum_values_from_python() -> dict[str, set[str]]:
    """Lazy import after sys.path setup."""
    from app.models import enums as enum_mod

    out: dict[str, set[str]] = {}
    for name in (
        "Role",
        "ServiceType",
        "ServiceFramework",
        "ServiceStatus",
        "TierLevel",
        "CoverageStatus",
        "GapPriority",
        "MaturityCisaLevel",
        "MaturityDodPhase",
        "DeliverableStatus",
    ):
        cls = getattr(enum_mod, name)
        out[name] = {member.value for member in cls}
    return out


def _yaml_map() -> dict[str, dict[str, str]]:
    return yaml.safe_load(ENUMS_YAML.read_text(encoding="utf-8"))


def _ts_labels(name: str) -> set[str]:
    """Crude regex extraction of the keys in `export const <Name>Labels = { ... }`."""
    txt = LABELS_TS.read_text(encoding="utf-8")
    match = re.search(rf"export const {name}Labels = \{{(.*?)\}} as const;", txt, re.DOTALL)
    if not match:
        return set()
    body = match.group(1)
    return {m.group(1) for m in re.finditer(r"(\w+):\s*\"[^\"]+\"", body)}


def main() -> None:
    py_enums = _enum_values_from_python()
    yaml_map = _yaml_map()

    failures: list[str] = []
    for name, values in py_enums.items():
        yaml_keys = set((yaml_map.get(name) or {}).keys())
        ts_keys = _ts_labels(name)
        missing_yaml = values - yaml_keys
        missing_ts = values - ts_keys
        if missing_yaml:
            failures.append(f"{name}: missing in enums.yaml -> {sorted(missing_yaml)}")
        if missing_ts:
            failures.append(f"{name}: missing in labels.ts -> {sorted(missing_ts)}")

    if failures:
        for f in failures:
            print_progress(LOADER, f)
        sys.exit(1)
    print_progress(LOADER, f"every enum value mapped (checked {len(py_enums)} enums)")


if __name__ == "__main__":
    main()
