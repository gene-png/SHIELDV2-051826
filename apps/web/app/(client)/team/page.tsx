export default function TeamPage() {
  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-2xl font-bold text-navy">Team</h1>
      <p className="mt-1 text-sm text-n-500">
        Invite colleagues to collaborate on this engagement. They&rsquo;ll receive a sign-up link
        (7-day expiry).
      </p>

      <section className="mt-8 rounded-card border border-n-200 bg-white p-6 shadow-card">
        <h2 className="text-lg font-semibold text-navy">Invite a colleague</h2>
        <p className="mt-2 text-sm text-n-500">
          The invitation flow lands with §6 user-invitation router (one half is already in place —
          <code className="ml-1 rounded bg-n-100 px-1">/api/auth/accept-invite</code> accepts
          inbound tokens; the outbound send happens once the SMTP flag is on).
        </p>
      </section>
    </div>
  );
}
