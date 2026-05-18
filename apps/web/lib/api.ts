/**
 * Thin SHIELD API client. Always talks server-to-server in NextAuth's
 * `authorize` callback (uses NEXT_PUBLIC_API_BASE_URL but resolved inside the
 * server runtime). Client components should call route handlers, not this
 * directly.
 */

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://api:8000";

export interface SignUpInput {
  display_name: string;
  email: string;
  password: string;
  accept_terms: boolean;
}

export interface SignInInput {
  email: string;
  password: string;
}

export interface SignInResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: {
    id: string;
    email: string;
    display_name: string;
    role: "admin" | "reviewer" | "client";
    is_primary_poc: boolean;
    mfa_enrolled: boolean;
    email_verified_at: string | null;
  };
}

async function call<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = await res.json();
      detail = body?.detail ?? body?.error;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail ?? res.statusText);
  }
  return (await res.json()) as T;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export const api = {
  signUp: (body: SignUpInput) =>
    call<SignInResponse>("/api/auth/signup", { method: "POST", body: JSON.stringify(body) }),

  signIn: (body: SignInInput) =>
    call<SignInResponse>("/api/auth/sign-in", { method: "POST", body: JSON.stringify(body) }),

  acceptInvite: (body: { token: string; display_name: string; password: string }) =>
    call<SignInResponse>("/api/auth/accept-invite", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  signOut: (bearer: string) =>
    call<{ status: string }>("/api/auth/sign-out", {
      method: "POST",
      headers: { Authorization: `Bearer ${bearer}` },
    }),

  changePassword: (bearer: string, body: { current_password: string; new_password: string }) =>
    call<{ status: string }>("/api/auth/change-password", {
      method: "POST",
      headers: { Authorization: `Bearer ${bearer}` },
      body: JSON.stringify(body),
    }),
};
