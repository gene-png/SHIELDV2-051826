import { auth } from "@/lib/auth";

export default async function HomePage() {
  const session = await auth();
  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-2xl font-bold text-navy">
        Welcome back, {session?.user?.name?.split(" ")[0] ?? "there"}.
      </h1>
      <p className="mt-1 text-sm text-n-500">
        Last checked just now. We&rsquo;ll show your service status, what&rsquo;s waiting on you,
        and a hero band for any ready deliverables once §6 lands.
      </p>

      <section className="mt-8 rounded-card border border-n-200 bg-white p-8 shadow-card">
        <h2 className="text-lg font-semibold text-navy">Up next: intake</h2>
        <p className="mt-2 text-sm text-n-700">
          Tell us about your organization and the services you&rsquo;re interested in.
        </p>
        <a
          href="/intake"
          className="mt-4 inline-flex rounded-control bg-gov-blue px-4 py-2 text-sm font-semibold text-white"
        >
          Start intake
        </a>
      </section>

      <p className="mt-8 text-xs text-n-500">
        Cross-service value loop, status grid, waiting-on-you list, and recent activity all land
        with §6 of the execution plan. See <code className="rounded bg-n-100 px-1">docs/execution-plan.md</code>.
      </p>
    </div>
  );
}
