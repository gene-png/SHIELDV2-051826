import Link from "next/link";

import { Wordmark } from "@/components/Wordmark";

export const metadata = {
  title: "Accessibility statement — SHIELD by Kentro",
};

// Placeholder. Real accessibility statement (post WCAG 2.1 AA external audit
// per Master Spec §17) ships before first production deployment.
export default function AccessibilityPage() {
  return (
    <main className="w-full max-w-2xl rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Accessibility statement</h1>
      <p className="mt-3 text-sm text-n-700">
        SHIELD by Kentro is built to meet WCAG 2.1 Level AA. Our internal CI runs axe-core checks
        on every signed-in and public route, and a third-party accessibility audit is required
        before each production deployment per the Master Spec.
      </p>
      <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-n-500">
        Known patterns
      </h2>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-n-700">
        <li>Keyboard-navigable forms with visible focus rings.</li>
        <li>Semantic HTML headings, labels bound to inputs.</li>
        <li>Color contrast meets AA across the design system palette.</li>
        <li>Live-region announcements on autosave + form errors.</li>
      </ul>
      <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-n-500">
        Report an issue
      </h2>
      <p className="mt-2 text-sm text-n-700">
        Email your consultant or open a support request. We treat accessibility regressions as
        HIGH-priority bugs.
      </p>
      <p className="mt-6 text-xs text-n-500">
        This is a v1 placeholder. The full statement (with the third-party audit reference) ships
        with §17 of the execution plan.
      </p>
      <p className="mt-6 text-sm">
        <Link href="/sign-up" className="text-gov-blue underline">
          ← Back to sign-up
        </Link>
      </p>
    </main>
  );
}
