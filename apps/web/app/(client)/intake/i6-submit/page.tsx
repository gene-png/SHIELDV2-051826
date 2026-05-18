"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { ApiError, api } from "@/lib/api";

export default function I6SubmitPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit() {
    if (!session?.accessToken) return;
    setBusy(true);
    setError(null);
    try {
      const resp = await api.submitIntake(session.accessToken);
      router.push(resp.home_url || "/home?intake=submitted");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't submit. Try again.");
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-navy">Ready to submit</h2>
      <p className="mt-2 text-sm text-n-700">
        We&rsquo;ll notify your consultant that you&rsquo;ve completed intake. They typically
        reach out within one business day to confirm scope and start the engagement.
      </p>

      <ul className="mt-6 space-y-2 text-sm text-n-700">
        <li className="flex items-start gap-2">
          <Check /> You can keep editing your organization details, system list, and uploads
          from <code className="rounded bg-n-100 px-1">/settings</code>.
        </li>
        <li className="flex items-start gap-2">
          <Check /> Your consultant cannot see methodology internals you haven&rsquo;t shared
          — the deliverable will lead with findings, not raw scoring math.
        </li>
        <li className="flex items-start gap-2">
          <Check /> Any AI analysis is reviewed by your consultant before you see it. Drafts
          never reach you directly.
        </li>
      </ul>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={() => router.push("/intake/i5-uploads")}
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </button>
        <button
          type="button"
          onClick={onSubmit}
          disabled={busy}
          className="rounded-control bg-success px-5 py-2.5 text-sm font-semibold text-white shadow-card disabled:opacity-60"
        >
          {busy ? "Submitting…" : "Submit intake"}
        </button>
      </div>
    </div>
  );
}

function Check() {
  return (
    <svg viewBox="0 0 16 16" className="mt-0.5 h-4 w-4 flex-shrink-0 text-success" fill="currentColor" aria-hidden>
      <path d="M6.2 11.8 3 8.6l1.1-1.1 2.1 2.1 5.7-5.7L13 5z" />
    </svg>
  );
}
