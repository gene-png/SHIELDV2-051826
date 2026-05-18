import Link from "next/link";

// Service-specific questionnaire renderer (CSF tier questionnaires + CISA or
// DoD ZT) lands alongside §8.2 / §8.3 of the execution plan. Right now this
// is a placeholder that lets users skip past it so the rest of the wizard
// continues to flow end-to-end.
export default function I4QuestionnairePage() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-navy">Service questionnaires</h2>
      <p className="mt-2 text-sm text-n-700">
        We&rsquo;ll load the right questions based on the services you picked. The interactive
        section-tabbed renderer ships alongside the Zero Trust + CSF workspaces in §8.
      </p>
      <div className="mt-6 rounded-card border border-dashed border-n-300 bg-white p-10 text-center text-n-500">
        Placeholder. Your questions are queued — you can continue and we&rsquo;ll surface them
        in your home dashboard.
      </div>
      <div className="mt-6 flex justify-between">
        <Link
          href="/intake/i3-systems"
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </Link>
        <Link
          href="/intake/i5-uploads"
          className="rounded-control bg-gov-blue px-5 py-2.5 text-sm font-semibold text-white shadow-card"
        >
          Continue
        </Link>
      </div>
    </div>
  );
}
