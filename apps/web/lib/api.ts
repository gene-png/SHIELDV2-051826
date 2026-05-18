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

  // ----- Intake (Master Spec §6.2 / §7 of execution plan) ------------------

  intakeStatus: (bearer: string) =>
    call<IntakeStatus>("/api/intake/status", {
      method: "GET",
      headers: { Authorization: `Bearer ${bearer}` },
    }),

  selectServices: (bearer: string, body: ServiceSelectionInput) =>
    fetch(`${BASE}/api/intake/service-selection`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${bearer}` },
      body: JSON.stringify(body),
    }).then(throwIfError),

  consultationRequest: (bearer: string, body: ConsultationInput) =>
    call<{ status: string; id: string }>("/api/intake/consultation-request", {
      method: "POST",
      headers: { Authorization: `Bearer ${bearer}` },
      body: JSON.stringify(body),
    }),

  saveOrganization: (bearer: string, body: OrganizationInput) =>
    fetch(`${BASE}/api/intake/organization`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${bearer}` },
      body: JSON.stringify(body),
    }).then(throwIfError),

  saveSystems: (bearer: string, body: { systems: SystemInput[] }) =>
    fetch(`${BASE}/api/intake/systems`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${bearer}` },
      body: JSON.stringify(body),
    }).then(throwIfError),

  submitIntake: (bearer: string) =>
    call<{ services_created: string[]; home_url: string }>("/api/intake/submit", {
      method: "POST",
      headers: { Authorization: `Bearer ${bearer}` },
    }),
};

async function throwIfError(res: Response): Promise<void> {
  if (!res.ok) {
    let detail: string | undefined;
    try {
      detail = (await res.json())?.detail;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail ?? res.statusText);
  }
}

export type ServiceType = "tech_debt" | "zero_trust" | "csf" | "attack_surface";
export type ServiceFramework = "cisa" | "dod";
export type TierLevel = "high" | "moderate" | "low";

export interface ServiceSelectionInput {
  services: ServiceType[];
  not_sure: boolean;
  framework?: ServiceFramework | null;
}

export interface ConsultationInput {
  role_title?: string;
  organization_name?: string;
  prompt_text?: string;
  contact_preference?: "phone" | "email";
  phone?: string;
  preferred_time?: string;
  additional_notes?: string;
}

export interface OrganizationInput {
  legal_name: string;
  dba_name?: string;
  website?: string;
  size_band?: string;
  industry?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_postal_code?: string;
  address_country?: string;
  compliance_deadline?: string;
}

export interface SystemInput {
  name: string;
  csam_id?: string;
  fips_categorization?: TierLevel;
  owner_email?: string;
  isso_email?: string;
  hosting?: string;
  ato_status?: string;
  ato_expiration_date?: string;
  notes?: string;
}

export interface IntakeStatus {
  selected_services: ServiceType[];
  framework: ServiceFramework | null;
  org_complete: boolean;
  systems_complete: boolean;
  questionnaire_progress_pct: number;
  artifacts_uploaded: number;
  can_submit: boolean;
}
