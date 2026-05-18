"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { signIn } from "next-auth/react";

import { Wordmark } from "@/components/Wordmark";
import { PasswordStrengthMeter, evaluatePassword } from "@/components/PasswordStrength";
import { api, ApiError } from "@/lib/api";

export default function AcceptInvitePage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();

  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const strength = evaluatePassword(password);
  const ok = displayName && strength.score >= 4;

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!ok) return;
    setBusy(true);
    setError(null);
    try {
      const resp = await api.acceptInvite({
        token: token as string,
        display_name: displayName,
        password,
      });
      const res = await signIn("credentials", { email: resp.user.email, password, redirect: false });
      if (res?.error) {
        router.push("/sign-in");
        return;
      }
      router.push("/home");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unexpected error. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="w-full max-w-md rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Accept your invitation</h1>
      <p className="mt-1 text-sm text-n-500">
        Set your name and a password. We&rsquo;ll sign you in immediately.
      </p>
      <form className="mt-6 space-y-5" onSubmit={onSubmit}>
        <Field
          id="display_name"
          label="Your name"
          type="text"
          value={displayName}
          onChange={setDisplayName}
          required
        />
        <div>
          <Field
            id="password"
            label="Password (12+ characters)"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={setPassword}
            required
          />
          {password && <PasswordStrengthMeter value={password} />}
        </div>
        {error && (
          <p role="alert" className="rounded-control border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={!ok || busy}
          className="w-full rounded-control bg-gov-blue px-4 py-2.5 text-sm font-semibold text-white shadow-card transition-colors hover:bg-navy disabled:opacity-60"
        >
          {busy ? "Accepting…" : "Accept invitation"}
        </button>
      </form>
    </main>
  );
}

function Field(props: {
  id: string;
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label htmlFor={props.id} className="block text-xs font-medium uppercase tracking-wide text-n-500">
        {props.label}
      </label>
      <input
        id={props.id}
        type={props.type}
        autoComplete={props.autoComplete}
        required={props.required}
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        className="block w-full border-0 border-b border-n-300 bg-transparent px-0 py-2 text-base text-n-900 focus:border-gov-blue focus:outline-none focus:ring-0"
      />
    </div>
  );
}
