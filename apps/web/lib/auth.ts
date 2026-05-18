/**
 * NextAuth (Auth.js v5) configuration.
 *
 * v1 strategy: SHIELD's API is the source of credentials. The Credentials
 * provider posts to `/api/auth/sign-in`, receives a SHIELD-issued JWT, and
 * we stash it on the NextAuth session. The same JWT is sent as a Bearer to
 * the API on every server-side call.
 *
 * v1.x: swap the Credentials provider for a Keycloak provider; the session
 * shape stays the same so consumers don't change.
 */

import NextAuth, { type NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";

import { api, ApiError } from "@/lib/api";

const ttlSecondsDefault = 900;

export const authConfig: NextAuthConfig = {
  trustHost: true,
  session: { strategy: "jwt", maxAge: ttlSecondsDefault },
  pages: {
    signIn: "/sign-in",
    error: "/sign-in",
  },
  providers: [
    Credentials({
      name: "SHIELD",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(creds) {
        if (typeof creds?.email !== "string" || typeof creds?.password !== "string") {
          return null;
        }
        try {
          const resp = await api.signIn({ email: creds.email, password: creds.password });
          return {
            id: resp.user.id,
            email: resp.user.email,
            name: resp.user.display_name,
            role: resp.user.role,
            isPrimaryPoc: resp.user.is_primary_poc,
            accessToken: resp.access_token,
            expiresIn: resp.expires_in,
          };
        } catch (err) {
          if (err instanceof ApiError && err.status === 429) {
            // Surface lockout via NextAuth error param.
            throw new Error("lockout");
          }
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role;
        token.isPrimaryPoc = user.isPrimaryPoc;
        token.accessToken = user.accessToken;
        token.expiresAt = Math.floor(Date.now() / 1000) + (user.expiresIn ?? ttlSecondsDefault);
      }
      return token;
    },
    async session({ session, token }) {
      session.user = {
        ...session.user,
        role: token.role as "admin" | "reviewer" | "client" | undefined,
        isPrimaryPoc: Boolean(token.isPrimaryPoc),
      };
      session.accessToken = token.accessToken as string | undefined;
      return session;
    },
    async authorized({ auth, request }) {
      const { pathname } = request.nextUrl;
      const publicRoutes = ["/", "/sign-in", "/sign-up", "/verify", "/accept-invite"];
      if (publicRoutes.some((p) => pathname === p || pathname.startsWith(`${p}/`))) {
        return true;
      }
      return !!auth?.user;
    },
  },
};

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
