"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { ApiError, api, type SystemInput, type TierLevel } from "@/lib/api";

interface DraftSystem extends SystemInput {
  _key: string;
}

const empty = (): DraftSystem => ({ _key: crypto.randomUUID(), name: "" });

export default function I3SystemsPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [items, setItems] = useState<DraftSystem[]>([empty()]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update<K extends keyof SystemInput>(idx: number, key: K, value: SystemInput[K]) {
    setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, [key]: value } : it)));
  }

  function remove(idx: number) {
    setItems((prev) => (prev.length === 1 ? prev : prev.filter((_, i) => i !== idx)));
  }

  async function onContinue() {
    if (!session?.accessToken) return;
    const cleaned = items
      .filter((s) => s.name.trim())
      .map(({ _key, ...rest }) => rest);
    if (!cleaned.length) {
      setError("Add at least one system, or skip if no CSF / Zero Trust services are selected.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.saveSystems(session.accessToken, { systems: cleaned });
      router.push("/intake/i4-questionnaire");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-navy">In-scope systems</h2>
      <p className="mt-1 text-sm text-n-500">
        List the systems the assessment will cover. You can add more later. Skip if you only chose
        Tech Debt Review or Attack Surface Coverage.
      </p>

      <div className="mt-6 space-y-4">
        {items.map((it, idx) => (
          <div key={it._key} className="rounded-card border border-n-200 bg-white p-5 shadow-card">
            <div className="flex items-start justify-between">
              <h3 className="text-sm font-semibold text-navy">System {idx + 1}</h3>
              {items.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(idx)}
                  className="text-xs text-n-500 hover:text-danger"
                >
                  Remove
                </button>
              )}
            </div>
            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <Field label="System name (required)">
                <input
                  className="input"
                  value={it.name}
                  onChange={(e) => update(idx, "name", e.target.value)}
                />
              </Field>
              <Field label="CSAM ID">
                <input
                  className="input"
                  value={it.csam_id ?? ""}
                  onChange={(e) => update(idx, "csam_id", e.target.value)}
                />
              </Field>
              <Field label="FIPS 199 categorization">
                <select
                  className="input"
                  value={it.fips_categorization ?? ""}
                  onChange={(e) =>
                    update(idx, "fips_categorization", (e.target.value || undefined) as TierLevel | undefined)
                  }
                >
                  <option value="">Select…</option>
                  <option value="high">High</option>
                  <option value="moderate">Moderate</option>
                  <option value="low">Low</option>
                </select>
              </Field>
              <Field label="Hosting">
                <input
                  className="input"
                  placeholder="On-prem / AWS / Azure / hybrid"
                  value={it.hosting ?? ""}
                  onChange={(e) => update(idx, "hosting", e.target.value)}
                />
              </Field>
              <Field label="System owner email">
                <input
                  type="email"
                  className="input"
                  value={it.owner_email ?? ""}
                  onChange={(e) => update(idx, "owner_email", e.target.value)}
                />
              </Field>
              <Field label="ISSO email">
                <input
                  type="email"
                  className="input"
                  value={it.isso_email ?? ""}
                  onChange={(e) => update(idx, "isso_email", e.target.value)}
                />
              </Field>
              <Field label="ATO status">
                <input
                  className="input"
                  placeholder="ATO / iATO / pending"
                  value={it.ato_status ?? ""}
                  onChange={(e) => update(idx, "ato_status", e.target.value)}
                />
              </Field>
              <Field label="ATO expiration">
                <input
                  type="date"
                  className="input"
                  value={it.ato_expiration_date ?? ""}
                  onChange={(e) => update(idx, "ato_expiration_date", e.target.value)}
                />
              </Field>
            </div>
            <Field label="Notes" className="mt-4 block">
              <textarea
                className="input min-h-16"
                value={it.notes ?? ""}
                onChange={(e) => update(idx, "notes", e.target.value)}
              />
            </Field>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => setItems((prev) => [...prev, empty()])}
        className="mt-4 rounded-control border border-dashed border-n-300 px-4 py-2 text-sm text-n-600 hover:border-gov-blue hover:text-gov-blue"
      >
        + Add another system
      </button>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={() => router.push("/intake/i2-organization")}
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </button>
        <button
          type="button"
          onClick={onContinue}
          disabled={busy}
          className="rounded-control bg-gov-blue px-5 py-2.5 text-sm font-semibold text-white shadow-card disabled:opacity-60"
        >
          {busy ? "Saving…" : "Continue"}
        </button>
      </div>

      <style>{`
        .input { display:block;width:100%;border:1px solid #CBD5E1;border-radius:6px;padding:8px 10px;font-size:14px;color:#0F172A;background:white; }
        .input:focus { outline:none;border-color:#005EA2;box-shadow:0 0 0 2px rgba(0,94,162,0.15); }
      `}</style>
    </div>
  );
}

function Field({
  label,
  children,
  className = "",
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={className || "block"}>
      <span className="block text-xs font-medium uppercase tracking-wide text-n-500">{label}</span>
      <span className="mt-1 block">{children}</span>
    </label>
  );
}
