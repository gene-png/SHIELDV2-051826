import type { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface User {
    role: "admin" | "reviewer" | "client";
    isPrimaryPoc: boolean;
    accessToken: string;
    expiresIn: number;
  }

  interface Session {
    user: DefaultSession["user"] & {
      role?: "admin" | "reviewer" | "client";
      isPrimaryPoc?: boolean;
    };
    accessToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: "admin" | "reviewer" | "client";
    isPrimaryPoc?: boolean;
    accessToken?: string;
    expiresAt?: number;
  }
}
