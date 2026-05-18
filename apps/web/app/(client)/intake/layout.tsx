import { headers } from "next/headers";
import type { ReactNode } from "react";

import { Stepper, type Step } from "@/components/intake/Stepper";

const STEPS: Array<{ key: string; label: string; pattern: RegExp }> = [
  { key: "i1", label: "Services", pattern: /\/intake\/?$|\/intake\/i1-services/ },
  { key: "i2", label: "Organization", pattern: /\/intake\/i2-organization/ },
  { key: "i3", label: "Systems", pattern: /\/intake\/i3-systems/ },
  { key: "i4", label: "Questionnaire", pattern: /\/intake\/i4-questionnaire/ },
  { key: "i5", label: "Artifacts", pattern: /\/intake\/i5-uploads/ },
  { key: "i6", label: "Submit", pattern: /\/intake\/i6-submit/ },
];

export default async function IntakeLayout({ children }: { children: ReactNode }) {
  const hdrs = await headers();
  const path = hdrs.get("x-invoke-path") ?? hdrs.get("next-url") ?? "";
  const idx = STEPS.findIndex((s) => s.pattern.test(path));
  const activeIdx = idx === -1 ? 0 : idx;
  const steps: Step[] = STEPS.map((s, i) => ({
    key: s.key,
    label: s.label,
    status: i < activeIdx ? "done" : i === activeIdx ? "active" : "todo",
  }));

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-navy">Intake</h1>
        <p className="mt-1 text-sm text-n-500">
          Save and resume any time. We&rsquo;ll let your consultant know when you submit.
        </p>
        <div className="mt-6">
          <Stepper steps={steps} />
        </div>
      </div>
      {children}
    </div>
  );
}
