import Link from "next/link";

import { auth } from "@/lib/auth";

export default async function SettingsPage() {
  const session = await auth();
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold text-navy">Settings</h1>
      <p className="mt-2 text-n-500">Profile fields, password, and notification preferences.</p>

      <section className="mt-8 rounded-card border border-n-200 bg-white p-6 shadow-card">
        <h2 className="text-lg font-semibold text-navy">Profile</h2>
        <dl className="mt-4 grid grid-cols-[140px_1fr] gap-x-6 gap-y-3 text-sm">
          <dt className="text-n-500">Name</dt>
          <dd className="text-n-900">{session?.user?.name}</dd>
          <dt className="text-n-500">Email</dt>
          <dd className="text-n-900">{session?.user?.email}</dd>
          <dt className="text-n-500">Role</dt>
          <dd className="text-n-900 capitalize">{session?.user?.role}</dd>
        </dl>
        <p className="mt-4 text-xs text-n-500">
          Editing profile fields lands with the full settings surface in §5+.
        </p>
      </section>

      <section className="mt-6 rounded-card border border-n-200 bg-white p-6 shadow-card">
        <h2 className="text-lg font-semibold text-navy">Password</h2>
        <p className="mt-2 text-sm text-n-700">
          Update your password. We require 12+ characters and a mix of types.
        </p>
        <Link
          href="/settings/password"
          className="mt-4 inline-flex rounded-control bg-gov-blue px-4 py-2 text-sm font-semibold text-white"
        >
          Change password
        </Link>
      </section>
    </div>
  );
}
