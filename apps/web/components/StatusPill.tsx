import clsx from "clsx";

type Tone = "gray" | "blue" | "amber" | "green" | "red" | "purple";

export function StatusPill({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium",
        tone === "gray" && "bg-n-100 text-n-700",
        tone === "blue" && "bg-[#E0EEFB] text-gov-blue",
        tone === "amber" && "bg-warning/15 text-warning",
        tone === "green" && "bg-success/15 text-success",
        tone === "red" && "bg-danger/15 text-danger",
        tone === "purple" && "bg-accent/15 text-accent",
      )}
    >
      {children}
    </span>
  );
}

const STATUS_TO_TONE: Record<string, Tone> = {
  new: "gray",
  intake_pending: "blue",
  in_progress: "blue",
  awaiting_review: "amber",
  ready_for_release: "amber",
  released: "green",
  archived: "gray",
};

const STATUS_LABEL: Record<string, string> = {
  new: "New",
  intake_pending: "Intake submitted",
  in_progress: "In progress",
  awaiting_review: "Awaiting reviewer",
  ready_for_release: "Ready to release",
  released: "Released",
  archived: "Archived",
};

export function ServiceStatusPill({ status }: { status: string }) {
  return <StatusPill tone={STATUS_TO_TONE[status] ?? "gray"}>{STATUS_LABEL[status] ?? status}</StatusPill>;
}

const SERVICE_LABEL: Record<string, string> = {
  tech_debt: "Technical Debt Review",
  zero_trust: "Zero Trust Assessment",
  csf: "NIST CSF 2.0 Assessment",
  attack_surface: "Attack Surface Coverage",
};

export function serviceLabel(type: string): string {
  return SERVICE_LABEL[type] ?? type;
}
