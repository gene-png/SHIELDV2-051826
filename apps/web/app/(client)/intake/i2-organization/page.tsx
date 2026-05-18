"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { ApiError, api, type OrganizationInput } from "@/lib/api";
import { AutoSaveIndicator } from "@/components/intake/AutoSaveIndicator";
import { usePersistOnBlur } from "@/components/intake/usePersistOnBlur";

const SIZE_BANDS = ["1-50", "51-250", "251-1000", "1001-5000", "5001+"];

export default function I2OrgPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [form, setForm] = useState<OrganizationInput>({
    legal_name: "",
    dba_name: "",
    website: "",
    size_band: "",
    industry: "",
    address_street: "",
    address_city: "",
    address_state: "",
    address_postal_code: "",
    address_country: "US",
    compliance_deadline: "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { mark, flush, savedAt } = usePersistOnBlur(form, async (next) => {
    if (!session?.accessToken || !next.legal_name) return;
    await api.saveOrganization(session.accessToken, next);
  });

  function update<K extends keyof OrganizationInput>(k: K, v: OrganizationInput[K]) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function onContinue() {
    if (!session?.accessToken) return;
    setBusy(true);
    setError(null);
    try {
      await api.saveOrganization(session.accessToken, form);
      router.push("/intake/i3-systems");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save. Try again.");
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-xl font-semibold text-navy">About your organization</h2>
          <p className="mt-1 text-sm text-n-500">
            We use this for the cover page of every deliverable. You can edit later in settings.
          </p>
        </div>
        <AutoSaveIndicator savedAt={savedAt} />
      </div>

      <div className="mt-6 space-y-5">
        <Field label="Legal name">
          <input
            required
            className="input"
            value={form.legal_name}
            onChange={(e) => update("legal_name", e.target.value)}
            onBlur={mark}
          />
        </Field>
        <Field label="Doing-business-as (optional)">
          <input
            className="input"
            value={form.dba_name ?? ""}
            onChange={(e) => update("dba_name", e.target.value)}
            onBlur={mark}
          />
        </Field>
        <Field label="Website">
          <input
            className="input"
            type="url"
            placeholder="https://"
            value={form.website ?? ""}
            onChange={(e) => update("website", e.target.value)}
            onBlur={mark}
          />
        </Field>
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <Field label="Size">
            <select
              className="input"
              value={form.size_band ?? ""}
              onChange={(e) => update("size_band", e.target.value)}
              onBlur={mark}
            >
              <option value="">Select…</option>
              {SIZE_BANDS.map((s) => (
                <option key={s} value={s}>
                  {s} people
                </option>
              ))}
            </select>
          </Field>
          <Field label="Industry">
            <input
              className="input"
              value={form.industry ?? ""}
              onChange={(e) => update("industry", e.target.value)}
              onBlur={mark}
            />
          </Field>
        </div>
        <fieldset className="rounded-card border border-n-200 bg-white p-5">
          <legend className="px-1 text-xs font-medium uppercase tracking-wide text-n-500">Address</legend>
          <div className="mt-2 space-y-4">
            <Field label="Street">
              <input
                className="input"
                value={form.address_street ?? ""}
                onChange={(e) => update("address_street", e.target.value)}
                onBlur={mark}
              />
            </Field>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <Field label="City">
                <input
                  className="input"
                  value={form.address_city ?? ""}
                  onChange={(e) => update("address_city", e.target.value)}
                  onBlur={mark}
                />
              </Field>
              <Field label="State">
                <input
                  className="input"
                  value={form.address_state ?? ""}
                  onChange={(e) => update("address_state", e.target.value)}
                  onBlur={mark}
                />
              </Field>
              <Field label="Postal code">
                <input
                  className="input"
                  value={form.address_postal_code ?? ""}
                  onChange={(e) => update("address_postal_code", e.target.value)}
                  onBlur={mark}
                />
              </Field>
            </div>
          </div>
        </fieldset>
        <Field label="Compliance deadline (if any)">
          <input
            type="date"
            className="input"
            value={form.compliance_deadline ?? ""}
            onChange={(e) => update("compliance_deadline", e.target.value)}
            onBlur={mark}
          />
        </Field>
      </div>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={() => router.push("/intake/i1-services")}
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </button>
        <button
          type="button"
          onClick={onContinue}
          disabled={!form.legal_name || busy}
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium uppercase tracking-wide text-n-500">{label}</span>
      <span className="mt-1 block">{children}</span>
    </label>
  );
}
