// Rehnuma API client. The only file in the frontend that knows the backend URL.
import type {
  Health,
  Language,
  MentorAnswer,
  Meta,
  PlanResult,
  SourcesResponse,
  StudentProfileInput,
} from "./types";

// The backend address comes from the VITE_REHNUMA_API_URL environment variable:
//   - on Vercel: Project -> Settings -> Environment Variables
//   - locally:   .env.local  (see .env.example)
const fromEnv: string | undefined = import.meta.env.VITE_REHNUMA_API_URL;

export const API_URL = (fromEnv ?? "").trim().replace(/\/+$/, "");

const PLAN_TIMEOUT_MS = 30_000;
const MENTOR_TIMEOUT_MS = 30_000;

export class RehnumaApiError extends Error {
  status: number;
  /** Field name -> messages, for inline errors beside the inputs (status 400). */
  fields: Record<string, string[]>;

  constructor(message: string, status: number, fields: Record<string, string[]> = {}) {
    super(message);
    this.name = "RehnumaApiError";
    this.status = status;
    this.fields = fields;
  }
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = PLAN_TIMEOUT_MS): Promise<T> {
  if (!API_URL) {
    throw new RehnumaApiError(
      "The backend address is not set. Add VITE_REHNUMA_API_URL in the frontend's environment variables and redeploy.",
      0,
    );
  }
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch {
    throw new RehnumaApiError(
      "Could not reach the Rehnuma server. Check your connection and try again.",
      0,
    );
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      (body && typeof body.error === "string" && body.error) ||
      `The Rehnuma server returned an error (${response.status}).`;
    throw new RehnumaApiError(message, response.status, body?.fields ?? {});
  }
  return body as T;
}

const post = <T>(path: string, payload: unknown, timeoutMs?: number) =>
  request<T>(path, { method: "POST", body: JSON.stringify(payload) }, timeoutMs);

/** Liveness + whether the dataset is still demo data + whether the AI mentor has a key. */
export const getHealth = () => request<Health>("/api/health");

/** Call once when the landing or profile page mounts, so the backend is warm before the form is submitted. */
export function warmUp(): void {
  void getHealth().catch(() => undefined);
}

/** Dropdown options: groups, cities in the dataset, languages. */
export const getMeta = () => request<Meta>("/api/meta");

/** Profile in, finished plan out. All numbers are calculated by code on the server. */
export const buildPlan = (profile: StudentProfileInput) => post<PlanResult>("/api/plan", profile);

/** Every sourced value with its link, date and official/unofficial flag. */
export const getSources = () => request<SourcesResponse>("/api/sources");

/** AI mentor: short explanation of the student's plan. */
export const explainPlan = (profile: StudentProfileInput, language: Language) =>
  post<MentorAnswer>("/api/explain", { profile, language }, MENTOR_TIMEOUT_MS);

/** AI mentor: answer one follow-up question about the plan. */
export const askMentor = (profile: StudentProfileInput, language: Language, question: string) =>
  post<MentorAnswer>("/api/chat", { profile, language, question }, MENTOR_TIMEOUT_MS);

// --- "Your plan stays in this browser session" --------------------------------------------
const PLAN_KEY = "rehnuma.plan";

export function savePlan(plan: PlanResult): void {
  try {
    sessionStorage.setItem(PLAN_KEY, JSON.stringify(plan));
  } catch {
    // private mode or server-side render: the plan simply is not cached
  }
}

export function loadPlan(): PlanResult | null {
  try {
    const raw = sessionStorage.getItem(PLAN_KEY);
    return raw ? (JSON.parse(raw) as PlanResult) : null;
  } catch {
    return null;
  }
}

export function clearPlan(): void {
  try {
    sessionStorage.removeItem(PLAN_KEY);
  } catch {
    // nothing to clear
  }
}
