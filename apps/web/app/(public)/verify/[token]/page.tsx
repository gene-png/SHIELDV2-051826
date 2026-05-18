// Email verification — no-op for v1 because SHIELD_AUTH_REQUIRE_EMAIL_VERIFY=false.
// The page is wired so the redirect target exists; activation in v1.x replaces
// this body with a real verification flow without touching call sites.

import { Wordmark } from "@/components/Wordmark";

export default function VerifyPage() {
  return (
    <main className="w-full max-w-md rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Email verification</h1>
      <p className="mt-3 text-sm text-n-700">
        Email verification is not required in this version of SHIELD. Your account is already
        active.
      </p>
      <a
        href="/home"
        className="mt-6 inline-block rounded-control bg-gov-blue px-4 py-2 text-sm font-semibold text-white"
      >
        Continue
      </a>
    </main>
  );
}
