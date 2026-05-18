import type { ReactNode } from "react";
import Link from "next/link";

import { auth } from "@/lib/auth";
import { Wordmark } from "@/components/Wordmark";

const NAV: Array<{ href: string; label: string }> = [
  { href: "/home", label: "Home" },
  { href: "/services", label: "My services" },
  { href: "/documents", label: "Documents" },
  { href: "/messages", label: "Messages" },
  { href: "/team", label: "Team" },
  { href: "/settings", label: "Settings" },
];

export default async function ClientLayout({ children }: { children: ReactNode }) {
  const session = await auth();
  return (
    <div className="grid min-h-screen grid-cols-[240px_1fr] bg-n-50">
      <aside className="flex flex-col border-r border-n-200 bg-navy text-n-100">
        <div className="px-6 py-6">
          <div className="text-white">
            <Wordmark size="md" />
          </div>
        </div>
        <nav className="flex-1 px-3">
          <ul className="space-y-1">
            {NAV.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block rounded-control px-3 py-2 text-sm text-n-100 transition-colors hover:bg-white/10"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="border-t border-white/10 px-6 py-4 text-xs text-n-200">
          <div className="font-medium text-white">{session?.user?.name}</div>
          <div className="text-n-300">{session?.user?.email}</div>
          <Link href="/sign-out" className="mt-2 inline-block text-n-200 hover:text-white">
            Sign out
          </Link>
        </div>
      </aside>
      <main className="px-8 py-8">{children}</main>
    </div>
  );
}
