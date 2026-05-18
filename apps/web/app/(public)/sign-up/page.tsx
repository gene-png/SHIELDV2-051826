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

  function validate(): string | null {
    if (!displayName.trim()) return "Enter your name.";
    if (!email.trim()) return "Enter your work email.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Enter a valid email address.";
    const strength = evaluatePassword(password);
    if (password.length < 12) return "Password must be at least 12 characters.";
    if (strength.score < 3) {
      return `Password is too weak. Missing: ${strength.reasons.join(", ")}.`;
    }
    if (password !== confirm) return "Passwords don't match.";
    if (!acceptTerms) return "Please accept the privacy notice and accessibility statement to continue.";
    return null;
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const validation = validate();
    if (validation) {
      setError(validation);
      return;
    }
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
      <form className="mt-6 space-y-5" onSubmit={onSubmit} noValidate>
        <BottomBorderField
          id="display_name"
          label="Your name"
          type="text"
          autoComplete="name"
          value={displayName}
          onChange={setDisplayName}
        />
        <BottomBorderField
          id="email"
          label="Work email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={setEmail}
        />
        <div>
          <BottomBorderField
            id="password"
            label="Password (12+ characters)"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={setPassword}
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
          disabled={busy}
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
