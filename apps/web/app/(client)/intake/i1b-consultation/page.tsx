"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { ApiError, api } from "@/lib/api";

export default function I1bConsultationPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [form, setForm] = useState({
    role_title: "",
    organization_name: "",
    prompt_text: "",
    contact_preference: "email" as "email" | "phone",
    phone: "",
    preferred_time: "",
    additional_notes: "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update<K extends keyof typeof form>(k: K, v: (typeof form)[K]) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!session?.accessToken) return;
    setBusy(true);
    setError(null);
    try {
      await api.consultationRequest(session.accessToken, form);
      router.push("/home?consultation=submitted");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't submit. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="space-y-5" onSubmit={onSubmit}>
      <h2 className="text-xl font-semibold text-navy">Tell us about your situation</h2>
      <p className="text-sm text-n-500">
        We&rsquo;ll review and reach out within one business day. None of these fields are
        required — share what&rsquo;s relevant.
      </p>

      <Field label="Your role or title">
        <input
          className="input"
          value={form.role_title}
          onChange={(e) => update("role_title", e.target.value)}
        />
      </Field>
      <Field label="Organization name">
        <input
          className="input"
          value={form.organization_name}
          onChange={(e) => update("organization_name", e.target.value)}
        />
      </Field>
      <Field label="What's prompting this?">
        <textarea
          className="input min-h-24"
          value={form.prompt_text}
          onChange={(e) => update("prompt_text", e.target.value)}
        />
      </Field>

      <fieldset className="rounded-card border border-n-200 bg-white p-4">
        <legend className="px-1 text-xs font-medium uppercase tracking-wide text-n-500">
          How should we reach out?
        </legend>
        <div className="mt-2 flex gap-4 text-sm">
          {(["email", "phone"] as const).map((opt) => (
            <label key={opt} className="flex items-center gap-2">
              <input
                type="radio"
                name="contact"
                checked={form.contact_preference === opt}
                onChange={() => update("contact_preference", opt)}
                className="h-4 w-4 text-gov-blue"
              />
              <span className="capitalize">{opt}</span>
            </label>
          ))}
        </div>
      </fieldset>

      {form.contact_preference === "phone" && (
        <Field label="Phone number">
          <input
            className="input"
            value={form.phone}
            onChange={(e) => update("phone", e.target.value)}
          />
        </Field>
      )}

      <Field label="Preferred time of day">
        <input
          className="input"
          placeholder="e.g. weekdays after 2pm ET"
          value={form.preferred_time}
          onChange={(e) => update("preferred_time", e.target.value)}
        />
      </Field>
      <Field label="Anything else we should know?">
        <textarea
          className="input min-h-20"
          value={form.additional_notes}
          onChange={(e) => update("additional_notes", e.target.value)}
        />
      </Field>

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex justify-between">
        <button
          type="button"
          onClick={() => router.push("/intake/i1-services")}
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </button>
        <button
          type="submit"
          disabled={busy}
          className="rounded-control bg-gov-blue px-5 py-2.5 text-sm font-semibold text-white shadow-card disabled:opacity-60"
        >
          {busy ? "Sending…" : "Send request"}
        </button>
      </div>

      <style>{`
        .input {
          display: block; width: 100%;
          border: 1px solid rgb(203 213 225);
          border-radius: 6px;
          padding: 8px 10px;
          font-size: 14px;
          color: #0F172A; background: white;
        }
        .input:focus { outline: none; border-color: #005EA2; box-shadow: 0 0 0 2px rgba(0,94,162,0.15); }
      `}</style>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium uppercase tracking-wide text-n-500">{label}</span>
      <span className="mt-1 block">{children}</span>
    </label>
  );
}
