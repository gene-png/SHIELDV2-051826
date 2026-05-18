"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signIn } from "next-auth/react";

import { Wordmark } from "@/components/Wordmark";
import { PasswordStrengthMeter, evaluatePassword } from "@/components/PasswordStrength";
import { api, ApiError } from "@/lib/api";

export default function SignUpPage() {
  const router = useRouter();

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const strength = evaluatePassword(password);
  const passwordOk = strength.score >= 4;
  const passwordsMatch = password.length > 0 && password === confirm;
  const formOk = displayName && email && passwordOk && passwordsMatch && acceptTerms;

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!formOk) return;
    setBusy(true);
    setError(null);
    try {
      await api.signUp({
        display_name: displayName,
        email,
        password,
        accept_terms: acceptTerms,
      });
      // Hand off to NextAuth so the session cookie lands; on success → /intake.
      const res = await signIn("credentials", { email, password, redirect: false });
      if (res?.error) {
        setError("Account created but sign-in failed. Please sign in manually.");
        router.push("/sign-in");
        return;
      }
      router.push("/intake");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unexpected error. Please try again.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="w-full max-w-md rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Create your account</h1>
      <p className="mt-1 text-sm text-n-500">
        It takes about a minute. Your consultant will reach out after intake.
      </p>
      <form className="mt-6 space-y-5" onSubmit={onSubmit}>
        <BottomBorderField
          id="display_name"
          label="Your name"
          type="text"
          autoComplete="name"
          value={displayName}
          onChange={setDisplayName}
          required
        />
        <BottomBorderField
          id="email"
          label="Work email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={setEmail}
          required
        />
        <div>
          <BottomBorderField
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
        <BottomBorderField
          id="confirm"
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          value={confirm}
          onChange={setConfirm}
          required
        />
        <label className="flex items-start gap-2 text-sm text-n-700">
          <input
            type="checkbox"
            className="mt-1 h-4 w-4 rounded border-n-300 text-gov-blue focus:ring-gov-blue"
            checked={acceptTerms}
            onChange={(e) => setAcceptTerms(e.target.checked)}
          />
          <span>
            I agree to the{" "}
            <Link href="/legal/privacy" className="text-gov-blue underline">
              privacy notice
            </Link>{" "}
            and{" "}
            <Link href="/legal/accessibility" className="text-gov-blue underline">
              accessibility statement
            </Link>
            .
          </span>
        </label>
        {error && (
          <p role="alert" className="rounded-control border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={!formOk || busy}
          className="w-full rounded-control bg-gov-blue px-4 py-2.5 text-sm font-semibold text-white shadow-card transition-colors hover:bg-navy disabled:opacity-60"
        >
          {busy ? "Creating account…" : "Create account"}
        </button>
        <p className="text-center text-sm text-n-500">
          Already have an account?{" "}
          <Link href="/sign-in" className="font-medium text-gov-blue hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </main>
  );
}

function BottomBorderField(props: {
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
