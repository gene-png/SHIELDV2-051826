"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { PasswordStrengthMeter, evaluatePassword } from "@/components/PasswordStrength";
import { ApiError, api } from "@/lib/api";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  function validate(): string | null {
    if (!current) return "Enter your current password.";
    if (next.length < 12) return "New password must be at least 12 characters.";
    const strength = evaluatePassword(next);
    if (strength.score < 3) {
      return `New password is too weak. Missing: ${strength.reasons.join(", ")}.`;
    }
    if (current === next) return "New password must differ from the current one.";
    return null;
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const validation = validate();
    if (validation) {
      setError(validation);
      return;
    }
    if (!session?.accessToken) {
      setError("Session expired — please sign in again.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.changePassword(session.accessToken, {
        current_password: current,
        new_password: next,
      });
      setSuccess(true);
      setCurrent("");
      setNext("");
      setTimeout(() => router.push("/settings"), 1200);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unexpected error.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="text-2xl font-bold text-navy">Change password</h1>
      <form className="mt-6 space-y-4 rounded-card border border-n-200 bg-white p-6 shadow-card" onSubmit={onSubmit}>
        <Field
          id="current"
          label="Current password"
          type="password"
          autoComplete="current-password"
          value={current}
          onChange={setCurrent}
        />
        <div>
          <Field
            id="next"
            label="New password (12+ characters)"
            type="password"
            autoComplete="new-password"
            value={next}
            onChange={setNext}
          />
          {next && <PasswordStrengthMeter value={next} />}
        </div>
        {error && <p role="alert" className="text-sm text-danger">{error}</p>}
        {success && <p className="text-sm text-success">Password updated.</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-control bg-gov-blue px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
        >
          {busy ? "Saving…" : "Update password"}
        </button>
      </form>
    </div>
  );
}

function Field(props: {
  id: string;
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete?: string;
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
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        className="block w-full border-0 border-b border-n-300 bg-transparent px-0 py-2 text-base text-n-900 focus:border-gov-blue focus:outline-none focus:ring-0"
      />
    </div>
  );
}
