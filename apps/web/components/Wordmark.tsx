// "SHIELD by Kentro" wordmark per Master Spec §13 (reference-docs/SHIELDv2_Design_Mockup.html L585).
export function Wordmark({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const big = { sm: "text-lg", md: "text-2xl", lg: "text-4xl" }[size];
  const sub = { sm: "text-[10px]", md: "text-xs", lg: "text-sm" }[size];
  return (
    <div className="flex flex-col leading-tight">
      <span className={`${big} font-bold tracking-tight text-navy`}>SHIELD</span>
      <span className={`${sub} font-medium uppercase tracking-[0.2em] text-n-500`}>
        by Kentro
      </span>
    </div>
  );
}
