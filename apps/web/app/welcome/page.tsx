import Link from "next/link";

import { auth } from "@/lib/auth";
import { Wordmark } from "@/components/Wordmark";

export default async function WelcomePage() {
  const session = await auth();
  const displayName = session?.user?.name ?? "there";
  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <Wordmark size="lg" />
      <h1 className="mt-8 text-3xl font-bold text-navy">Welcome, {displayName}.</h1>
      <p className="mt-3 text-base text-n-700">
        We&rsquo;ll walk you through a short intake to understand what services would be most
        useful to your organization. You can save and resume anytime.
      </p>
      <Link
        href="/intake"
        className="mt-8 inline-flex items-center rounded-control bg-gov-blue px-5 py-3 text-sm font-semibold text-white shadow-card hover:bg-navy"
      >
        Let&rsquo;s get started
      </Link>
    </main>
  );
}
