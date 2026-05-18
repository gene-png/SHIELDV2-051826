import { ServiceDetailShell } from "@/components/ServiceDetailShell";

export default function ZeroTrustServicePage() {
  return (
    <ServiceDetailShell
      title="Zero Trust Assessment"
      subtitle="Pillar-by-pillar maturity, current → target roadmap"
      placeholderText="The per-pillar radar + roadmap timeline ship with §8.2 of the execution plan."
    />
  );
}
