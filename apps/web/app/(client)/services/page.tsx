import Link from "next/link";

import { fetchMyServices } from "@/lib/api";
import { auth } from "@/lib/auth";
import { ServiceStatusPill, serviceLabel } from "@/components/StatusPill";

export default async function ServicesPage() {
  const session = await auth();
  const services = session?.accessToken ? await fetchMyServices(session.accessToken).catch(() => []) : [];

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-2xl font-bold text-navy">My services</h1>
      <p className="mt-1 text-sm text-n-500">
        Every engagement you&rsquo;ve signed up for, with the latest status and consultant.
      </p>

      {services.length === 0 ? (
        <div className="mt-8 rounded-card border border-dashed border-n-300 bg-white p-12 text-center">
          <p className="text-base font-semibold text-navy">No services yet</p>
          <p className="mt-2 text-sm text-n-500">
            Complete intake to get started — your consultant will be in touch shortly after.
          </p>
          <Link
            href="/intake"
            className="mt-4 inline-flex rounded-control bg-gov-blue px-4 py-2 text-sm font-semibold text-white"
          >
            Start intake
          </Link>
        </div>
      ) : (
        <ul className="mt-8 space-y-3">
          {services.map((s) => (
            <li key={s.id}>
              <Link
                href={typeFromService(s.type)}
                className="flex items-start justify-between rounded-card border border-n-200 bg-white p-5 shadow-card transition-colors hover:border-gov-blue/50"
              >
                <div>
                  <div className="text-base font-semibold text-navy">{serviceLabel(s.type)}</div>
                  {s.headline ? (
                    <p className="mt-1 text-sm text-n-700">{s.headline}</p>
                  ) : (
                    <p className="mt-1 text-sm text-n-500">
                      Your consultant will populate the headline as the engagement progresses.
                    </p>
                  )}
                </div>
                <ServiceStatusPill status={s.status} />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function typeFromService(type: string): string {
  return (
    {
      tech_debt: "/services/tech-debt",
      zero_trust: "/services/zero-trust",
      csf: "/services/csf",
      attack_surface: "/services/attack-surface",
    } as Record<string, string>
  )[type] ?? "/services";
}
