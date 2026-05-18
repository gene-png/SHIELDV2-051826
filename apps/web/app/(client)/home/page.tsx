import Link from "next/link";

import { fetchMyServices } from "@/lib/api";
import { auth } from "@/lib/auth";
import { ServiceStatusPill, serviceLabel } from "@/components/StatusPill";

export default async function HomePage() {
  const session = await auth();
  const services = session?.accessToken ? await fetchMyServices(session.accessToken).catch(() => []) : [];
  const firstName = session?.user?.name?.split(" ")[0] ?? "there";
  const hasServices = services.length > 0;
  const released = services.filter((s) => s.status === "released");
  const inProgress = services.filter((s) => s.status === "in_progress" || s.status === "awaiting_review");
  const queued = services.filter((s) => s.status === "intake_pending" || s.status === "new");

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-2xl font-bold text-navy">Welcome back, {firstName}.</h1>
      <p className="mt-1 text-sm text-n-500">
        Here&rsquo;s where each engagement stands. We&rsquo;ll surface anything that needs your input
        at the top.
      </p>

      {!hasServices && (
        <section className="mt-8 rounded-card border border-n-200 bg-white p-8 shadow-card">
          <h2 className="text-lg font-semibold text-navy">Up next: intake</h2>
          <p className="mt-2 text-sm text-n-700">
            Tell us about your organization and the services you&rsquo;re interested in.
          </p>
          <Link
            href="/intake"
            className="mt-4 inline-flex rounded-control bg-gov-blue px-4 py-2 text-sm font-semibold text-white"
          >
            Start intake
          </Link>
        </section>
      )}

      {released.length > 0 && (
        <section className="mt-8 overflow-hidden rounded-card shadow-card">
          <div
            className="px-6 py-5 text-white"
            style={{
              background: "linear-gradient(135deg, #005EA2 0%, #1B3A5B 100%)",
            }}
          >
            <p className="text-xs uppercase tracking-widest opacity-80">Ready to read</p>
            <h2 className="mt-1 text-xl font-semibold">
              {released.length === 1 ? "1 deliverable released" : `${released.length} deliverables released`}
            </h2>
            <p className="mt-1 text-sm opacity-90">
              Your consultant has finalized {released.length === 1 ? "a deliverable" : "deliverables"}. Open them in{" "}
              <Link href="/documents" className="underline">
                Documents
              </Link>
              .
            </p>
          </div>
        </section>
      )}

      {hasServices && (
        <section className="mt-8">
          <h2 className="text-lg font-semibold text-navy">Your services</h2>
          <ul className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
            {services.map((s) => (
              <li key={s.id} className="rounded-card border border-n-200 bg-white p-5 shadow-card">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-navy">{serviceLabel(s.type)}</div>
                    {s.headline ? (
                      <p className="mt-1 text-sm text-n-700">{s.headline}</p>
                    ) : (
                      <p className="mt-1 text-sm text-n-500">No headline yet — your consultant will populate this.</p>
                    )}
                  </div>
                  <ServiceStatusPill status={s.status} />
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {inProgress.length === 0 && queued.length > 0 && (
        <section className="mt-8 rounded-card border border-warning/30 bg-warning/5 p-5">
          <h3 className="text-sm font-semibold text-warning">Waiting on us</h3>
          <p className="mt-1 text-sm text-n-700">
            We&rsquo;ve received your intake. Your consultant is reviewing scope.
          </p>
        </section>
      )}
    </div>
  );
}
