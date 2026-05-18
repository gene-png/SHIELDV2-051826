import { ServiceDetailShell } from "@/components/ServiceDetailShell";

export default function CsfServicePage() {
  return (
    <ServiceDetailShell
      title="NIST CSF 2.0 Assessment"
      subtitle="Function-by-function maturity heatmap, tiered profile breakdown"
      placeholderText="The maturity heatmap + enterprise profile rollup ship with §8.3 of the execution plan."
    />
  );
}
