"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import clsx from "clsx";

import { ApiError, api, type ServiceFramework, type ServiceType } from "@/lib/api";

interface ServiceOption {
  key: ServiceType;
  title: string;
  blurb: string;
}

const SERVICES: ServiceOption[] = [
  {
    key: "tech_debt",
    title: "Technical Debt Review",
    blurb: "Inventory your cybersecurity tooling, find overlap, recommend consolidation.",
  },
  {
    key: "zero_trust",
    title: "Zero Trust Assessment",
    blurb: "Score maturity against CISA ZTMM 2.0 or DoD ZT Reference Architecture; build a roadmap.",
  },
  {
    key: "csf",
    title: "NIST CSF 2.0 Assessment",
    blurb: "10-step Kentro Playbook with tiered profiles and gap analysis.",
  },
  {
    key: "attack_surface",
    title: "Attack Surface Coverage",
    blurb: "Map your tooling against MITRE ATT&CK and find the blind spots.",
  },
];

export default function I1ServicesPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [picked, setPicked] = useState<Set<ServiceType>>(new Set());
  const [notSure, setNotSure] = useState(false);
  const [framework, setFramework] = useState<ServiceFramework | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function togglePick(s: ServiceType) {
    if (notSure) setNotSure(false);
    setPicked((prev) => {
      const next = new Set(prev);
      next.has(s) ? next.delete(s) : next.add(s);
      if (!next.has("zero_trust")) {
        // Clear framework when zero_trust is unselected.
        setFramework(null);
      }
      return next;
    });
  }

  function toggleNotSure() {
    if (!notSure) {
      setPicked(new Set());
      setFramework(null);
    }
    setNotSure((v) => !v);
  }

  const hasZeroTrust = picked.has("zero_trust");

  function validate(): string | null {
    if (notSure) return null;
    if (picked.size === 0) {
      return "Pick at least one service, or select 'I'm not sure' to talk it through with us.";
    }
    if (hasZeroTrust && framework === null) {
      return "Choose CISA ZTMM or DoD ZTRA for the Zero Trust Assessment.";
    }
    return null;
  }

  async function onContinue() {
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
      if (notSure) {
        router.push("/intake/i1b-consultation");
        return;
      }
      await api.selectServices(session.accessToken, {
        services: Array.from(picked),
        not_sure: false,
        framework: hasZeroTrust ? framework : null,
      });
      router.push("/intake/i2-organization");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-navy">Which services would you like?</h2>
      <p className="mt-1 text-sm text-n-500">Pick one or more, or tell us you&rsquo;d like to talk first.</p>

      <div className="mt-6 space-y-3">
        {SERVICES.map((svc) => {
          const selected = picked.has(svc.key);
          return (
            <button
              key={svc.key}
              type="button"
              onClick={() => togglePick(svc.key)}
              disabled={notSure}
              className={clsx(
                "flex w-full items-start gap-4 rounded-card border bg-white p-5 text-left shadow-card transition-colors",
                selected ? "border-gov-blue bg-[#F0F7FF]" : "border-n-200 hover:border-gov-blue/50",
                notSure && "cursor-not-allowed opacity-60",
              )}
              aria-pressed={selected}
            >
              <span
                className={clsx(
                  "mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border-2",
                  selected ? "border-gov-blue bg-gov-blue text-white" : "border-n-300 bg-white",
                )}
                aria-hidden
              >
                {selected && (
                  <svg viewBox="0 0 16 16" className="h-3 w-3" fill="currentColor">
                    <path d="M6.2 11.8 3 8.6l1.1-1.1 2.1 2.1 5.7-5.7L13 5z" />
                  </svg>
                )}
              </span>
              <span className="flex-1">
                <span className="block text-base font-semibold text-navy">{svc.title}</span>
                <span className="mt-1 block text-sm text-n-700">{svc.blurb}</span>
              </span>
            </button>
          );
        })}

        {hasZeroTrust && (
          <fieldset className="mt-3 rounded-card border border-n-200 bg-white p-5">
            <legend className="px-1 text-xs font-medium uppercase tracking-wide text-n-500">
              Zero Trust framework
            </legend>
            <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
              {[
                { v: "cisa" as const, label: "CISA ZTMM 2.0" },
                { v: "dod" as const, label: "DoD ZT Reference Architecture" },
              ].map((opt) => (
                <label
                  key={opt.v}
                  className={clsx(
                    "flex cursor-pointer items-center gap-2 rounded-control border p-3 text-sm",
                    framework === opt.v ? "border-gov-blue bg-[#F0F7FF]" : "border-n-300",
                  )}
                >
                  <input
                    type="radio"
                    name="framework"
                    className="h-4 w-4 text-gov-blue focus:ring-gov-blue"
                    checked={framework === opt.v}
                    onChange={() => setFramework(opt.v)}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>
        )}

        <label
          className={clsx(
            "mt-2 flex cursor-pointer items-start gap-3 rounded-card border bg-white p-5 shadow-card",
            notSure ? "border-gov-blue bg-[#F0F7FF]" : "border-n-200",
          )}
        >
          <input
            type="radio"
            name="not_sure"
            className="mt-1 h-5 w-5 text-gov-blue"
            checked={notSure}
            onChange={toggleNotSure}
          />
          <span>
            <span className="block text-base font-semibold text-navy">I&rsquo;m not sure</span>
            <span className="mt-1 block text-sm text-n-700">
              Tell us a little about your situation and we&rsquo;ll set up a 30-minute call to recommend the right path.
            </span>
          </span>
        </label>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-control border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
          {error}
        </p>
      )}

      <div className="mt-8 flex justify-end">
        <button
          type="button"
          onClick={onContinue}
          disabled={busy}
          className="rounded-control bg-gov-blue px-5 py-2.5 text-sm font-semibold text-white shadow-card transition-colors hover:bg-navy disabled:opacity-60"
        >
          {busy ? "Saving…" : notSure ? "Request a call →" : "Continue"}
        </button>
      </div>
    </div>
  );
}
