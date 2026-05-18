/**
 * GET /sign-out — POSTs to the SHIELD API to write an audit row, then triggers
 * NextAuth's signOut. Using a GET handler so links from menus can hit it
 * directly; the audit row is the same either way.
 */

import { NextResponse } from "next/server";

import { api } from "@/lib/api";
import { auth, signOut } from "@/lib/auth";

export async function GET() {
  const session = await auth();
  if (session?.accessToken) {
    try {
      await api.signOut(session.accessToken);
    } catch {
      // Don't block sign-out on a failed audit ping.
    }
  }
  await signOut({ redirect: false });
  return NextResponse.redirect(new URL("/sign-in", process.env.NEXTAUTH_URL ?? "http://localhost:3000"));
}
