/**
 * Enum → display-label maps. Master Spec §14 forbids exposing raw enum slugs
 * in any user-facing surface. Every API response runs `applyLabels(payload)`
 * at the serializer boundary; every UI render uses these helpers instead of
 * the raw value.
 *
 * Keys mirror `apps/api/app/models/enums.py` exactly.
 */

export const RoleLabels = {
  admin: "Kentro consultant",
  reviewer: "Reviewer",
  client: "Client",
} as const;

export const ServiceTypeLabels = {
  tech_debt: "Technical Debt Review",
  zero_trust: "Zero Trust Assessment",
  csf: "NIST CSF 2.0 Assessment",
  attack_surface: "Attack Surface Coverage",
} as const;

export const ServiceFrameworkLabels = {
  cisa: "CISA Zero Trust Maturity Model 2.0",
  dod: "DoD Zero Trust Reference Architecture",
} as const;

export const ServiceStatusLabels = {
  new: "New",
  intake_pending: "Intake in progress",
  in_progress: "Active",
  awaiting_review: "Awaiting review",
  ready_for_release: "Ready to release",
  released: "Released",
  archived: "Archived",
} as const;

export const TierLevelLabels = {
  high: "High",
  moderate: "Moderate",
  low: "Low",
} as const;

export const CoverageStatusLabels = {
  covered: "Covered",
  partial: "Partial",
  uncovered: "Uncovered",
} as const;

export const GapPriorityLabels = {
  P1: "Priority 1",
  P2: "Priority 2",
  P3: "Priority 3",
} as const;

export const MaturityCisaLevelLabels = {
  traditional: "Traditional",
  initial: "Initial",
  advanced: "Advanced",
  optimal: "Optimal",
} as const;

export const MaturityDodPhaseLabels = {
  target: "Target",
  advanced: "Advanced",
} as const;

export const DeliverableStatusLabels = {
  draft: "Draft",
  final: "Final",
  released: "Released",
  superseded: "Superseded",
} as const;

export function applyLabels<T extends Record<string, unknown>>(
  obj: T,
  field: keyof T,
  map: Record<string, string>,
): T {
  const v = obj[field];
  if (typeof v === "string" && v in map) {
    return { ...obj, [`${String(field)}_label`]: map[v] };
  }
  return obj;
}
