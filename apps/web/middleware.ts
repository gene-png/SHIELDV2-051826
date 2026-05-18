/**
 * Route-protection middleware. Hands off to the NextAuth `authorized`
 * callback in lib/auth.ts so the policy lives in a single place.
 */

export { auth as middleware } from "@/lib/auth";

export const config = {
  matcher: [
    // Run on every page except API auth + Next internals + public assets.
    "/((?!api/auth|_next/static|_next/image|favicon.ico).*)",
  ],
};
