import { ServiceDetailShell } from "@/components/ServiceDetailShell";

export default function AttackSurfaceServicePage() {
  return (
    <ServiceDetailShell
      title="Attack Surface Coverage"
      subtitle="MITRE ATT&CK technique-by-technique coverage and blind spots"
      placeholderText="The tactic heatmap + blind-spot card grid ship with §8.4 of the execution plan."
    />
  );
}
