import Link from "next/link";

export function ServiceDetailShell({
  title,
  subtitle,
  placeholderText,
}: {
  title: string;
  subtitle: string;
  placeholderText: string;
}) {
  return (
    <div className="mx-auto max-w-4xl">
      <Link href="/services" className="text-sm text-gov-blue hover:underline">
        ← All services
      </Link>
      <h1 className="mt-4 text-2xl font-bold text-navy">{title}</h1>
      <p className="mt-1 text-sm text-n-500">{subtitle}</p>

      <section className="mt-8 rounded-card border border-dashed border-n-300 bg-white p-12 text-center text-n-500">
        {placeholderText}
      </section>

      <p className="mt-6 text-xs text-n-500">
        Methodology details stay hidden by default — your deliverable leads with findings, not
        scoring math. Once your consultant releases a deliverable, the headline appears here.
      </p>
    </div>
  );
}
