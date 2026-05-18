"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { signIn } from "next-auth/react";

import { Wordmark } from "@/components/Wordmark";

export default function SignInPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("callbackUrl") ?? "/home";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const res = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });
    setBusy(false);
    if (res?.error) {
      setError(
        res.error === "lockout"
          ? "Too many failed attempts. Please wait a few minutes and try again."
          : "Invalid email or password.",
      );
      return;
    }
    router.push(callbackUrl);
  }

  return (
    <main className="w-full max-w-md rounded-card bg-white p-8 shadow-card">
      <Wordmark size="lg" />
      <h1 className="mt-6 text-xl font-semibold text-navy">Sign in</h1>
      <form className="mt-6 space-y-5" onSubmit={onSubmit}>
        <BottomBorderField
          id="email"
          label="Work email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={setEmail}
          required
        />
        <BottomBorderField
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={setPassword}
          required
        />
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
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="text-center text-sm text-n-500">
          New to SHIELD?{" "}
          <Link href="/sign-up" className="font-medium text-gov-blue hover:underline">
            Create an account
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
