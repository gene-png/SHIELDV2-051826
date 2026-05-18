// Placeholder landing page. Real sign-in lives at /sign-in (Master Spec §6.1).
export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <div className="rounded-card border border-n-200 bg-white p-8 shadow-card">
        <h1 className="text-2xl font-bold text-navy">SHIELD by Kentro</h1>
        <p className="mt-1 text-sm text-n-500">v2.0 — dev container scaffolding online</p>
        <p className="mt-6 text-n-700">
          The platform is being built per the locked Master Spec. This placeholder confirms the
          web service is reachable. Sign-in moves to <code className="rounded bg-n-100 px-1">/sign-in</code>{" "}
          once §5 of the execution plan ships.
        </p>
      </div>
    </main>
  );
}
