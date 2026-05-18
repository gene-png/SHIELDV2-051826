import type { ReactNode } from "react";

import { PolygonalBackdrop } from "@/components/PolygonalBackdrop";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="relative isolate min-h-screen overflow-hidden">
      <PolygonalBackdrop />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        {children}
      </div>
    </div>
  );
}
