/**
 * 6-segment intake progress bar matching the design mockup. Each segment
 * cycles gray → blue (active) → green (done) per Master Spec §6.2.
 */
import clsx from "clsx";

export type StepStatus = "todo" | "active" | "done";

export interface Step {
  key: string;
  label: string;
  status: StepStatus;
}

export function Stepper({ steps }: { steps: Step[] }) {
  return (
    <ol className="flex gap-2" aria-label="Intake progress">
      {steps.map((s) => (
        <li key={s.key} className="flex flex-1 flex-col gap-1">
          <span
            className={clsx(
              "h-1.5 rounded-full transition-colors",
              s.status === "done"
                ? "bg-success"
                : s.status === "active"
                  ? "bg-gov-blue"
                  : "bg-n-200",
            )}
            aria-hidden
          />
          <span
            className={clsx(
              "text-[11px] uppercase tracking-wide",
              s.status === "active"
                ? "font-semibold text-navy"
                : s.status === "done"
                  ? "text-success"
                  : "text-n-500",
            )}
          >
            {s.label}
          </span>
        </li>
      ))}
    </ol>
  );
}
