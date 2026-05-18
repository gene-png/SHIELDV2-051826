"use client";

import { useEffect, useState } from "react";

/**
 * Renders "Saved N seconds ago" once a save completes. Per Master Spec §6.6
 * the indicator stays visible on the wizard between blurs. Idle state reads
 * "Saved" without a clock.
 */
export function AutoSaveIndicator({ savedAt }: { savedAt: number | null }) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!savedAt) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [savedAt]);

  if (!savedAt) return null;
  const seconds = Math.max(0, Math.floor((now - savedAt) / 1000));
  const text =
    seconds < 5
      ? "Saved just now"
      : seconds < 60
        ? `Saved ${seconds} seconds ago`
        : `Saved ${Math.floor(seconds / 60)} minute${seconds < 120 ? "" : "s"} ago`;

  return (
    <span className="inline-flex items-center gap-1 text-xs text-n-500" aria-live="polite">
      <svg className="h-3 w-3 text-success" viewBox="0 0 24 24" aria-hidden>
        <path
          fill="currentColor"
          d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"
        />
      </svg>
      {text}
    </span>
  );
}
