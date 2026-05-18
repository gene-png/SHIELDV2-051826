"use client";

/**
 * Strength meter — 5 bins. Pure heuristic so it works without bringing in
 * zxcvbn. Underpinned by Argon2id server-side; this is UI feedback only.
 */

import clsx from "clsx";

export interface PasswordStrength {
  score: 0 | 1 | 2 | 3 | 4 | 5;
  label: string;
  reasons: string[];
}

export function evaluatePassword(pw: string): PasswordStrength {
  const reasons: string[] = [];
  let score = 0;
  if (pw.length >= 12) score++;
  else reasons.push("At least 12 characters");

  if (/[A-Z]/.test(pw)) score++;
  else reasons.push("An uppercase letter");

  if (/[a-z]/.test(pw)) score++;
  else reasons.push("A lowercase letter");

  if (/\d/.test(pw)) score++;
  else reasons.push("A number");

  if (/[^A-Za-z0-9]/.test(pw)) score++;
  else reasons.push("A symbol");

  const label =
    score >= 5 ? "Strong" : score === 4 ? "Good" : score === 3 ? "Fair" : score >= 1 ? "Weak" : "—";
  return { score: score as PasswordStrength["score"], label, reasons };
}

export function PasswordStrengthMeter({ value }: { value: string }) {
  const { score, label, reasons } = evaluatePassword(value);
  const bars = [0, 1, 2, 3, 4];
  return (
    <div className="mt-2 text-xs">
      <div className="flex gap-1" aria-hidden>
        {bars.map((i) => (
          <span
            key={i}
            className={clsx(
              "h-1 flex-1 rounded-full transition-colors",
              i < score
                ? score >= 5
                  ? "bg-success"
                  : score === 4
                    ? "bg-gov-blue"
                    : score === 3
                      ? "bg-warning"
                      : "bg-danger"
                : "bg-n-200",
            )}
          />
        ))}
      </div>
      <div className="mt-1 flex items-center justify-between">
        <span className="font-medium text-n-700">{label}</span>
        {reasons.length > 0 ? (
          <span className="text-n-500">Add: {reasons.join(", ")}</span>
        ) : (
          <span className="text-success">Meets policy</span>
        )}
      </div>
    </div>
  );
}
