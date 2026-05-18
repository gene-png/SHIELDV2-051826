import Link from "next/link";

import { Wordmark } from "@/components/Wordmark";

export const metadata = {
  title: "Privacy notice — SHIELD by Kentro",
};

// Placeholder. Real privacy notice ships with §16 (documentation) before any
// production deployment. Linked from the sign-up Terms checkbox.
export default function PrivacyPage() {
  return (
    <main className="w-full max-w-2xl rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Privacy notice</h1>
      <p className="mt-3 text-sm text-n-700">
        SHIELD by Kentro is operated by Kentro on behalf of customer engagements. Every deployment
        is single-tenant — your data does not flow to other customer environments.
      </p>
      <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-n-500">
        What we store
      </h2>
      <p className="mt-2 text-sm text-n-700">
        Your name, work email, and the artifacts and answers you contribute during intake and
        assessment. Passwords are hashed with Argon2id; we never store them in plaintext.
      </p>
      <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-n-500">
        AI processing
      </h2>
      <p className="mt-2 text-sm text-n-700">
        SHIELD redacts personally identifiable information (emails, phones, names, addresses,
        signature blocks, federal identifiers) before any payload leaves the platform for AI
        analysis. Redactions are logged and verifiable in the audit trail.
      </p>
      <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-n-500">Audit</h2>
      <p className="mt-2 text-sm text-n-700">
        Every state change writes an append-only audit row. You can request your audit history
        from your consultant at any time.
      </p>
      <p className="mt-6 text-xs text-n-500">
        This is a v1 placeholder. The full notice ships with the §16 documentation pass before
        production deployment.
      </p>
      <p className="mt-6 text-sm">
        <Link href="/sign-up" className="text-gov-blue underline">
          ← Back to sign-up
        </Link>
      </p>
    </main>
  );
}
