// Rehnuma API contract. Mirrors backend/app/schemas.py - change both together.

export type Group = "pre-engineering" | "ics" | "pre-medical" | "icom" | "fa";
export type InterStatus = "part1" | "complete";
export type Language = "en" | "roman-ur";
export type Category = "safe" | "target" | "reach" | "unlikely" | "no-data" | "not-eligible";

/** What the profile form sends. Totals are optional: the API defaults to 1100 (550 for inter part 1). */
export interface StudentProfileInput {
  matricObtained: number;
  matricTotal?: number;
  interObtained: number;
  interTotal?: number;
  interStatus?: InterStatus;
  group: Group;
  homeCity: string;
  willingToRelocate?: boolean;
  /** Total budget for the whole degree, in PKR. */
  budgetTotal: number;
  familyIncomeMonthly?: number | null;
  /** Leave null/undefined when the student has no expected score. 0 is a real score. */
  expectedTestPercent?: number | null;
}

/** The profile as echoed back inside a plan, with every default filled in. */
export interface StudentProfile {
  matricObtained: number;
  matricTotal: number;
  interObtained: number;
  interTotal: number;
  interStatus: InterStatus;
  group: Group;
  homeCity: string;
  willingToRelocate: boolean;
  budgetTotal: number;
  familyIncomeMonthly: number | null;
  expectedTestPercent: number | null;
}

export interface SourceRef {
  sourceName: string;
  sourceUrl: string;
  /** YYYY-MM-DD */
  verifiedOn: string;
  confidence: "official" | "unofficial";
  note?: string | null;
}

export interface Cost {
  tuition: number;
  admissionFee: number;
  hostel: number;
  total: number;
  withinBudget: boolean;
  /** total - budget. Positive = over budget. */
  gap: number;
  /** true when the university is in another city than the student's home city. */
  hostelApplies: boolean;
  /** true when hostel applies but no sourced figure exists (hostel is then NOT in total). */
  hostelUnknown: boolean;
}

export interface ScholarshipMatch {
  id: string;
  name: string;
  provider: string | null;
  type: string | null;
  summary: string;
  applyUrl: string;
  source: SourceRef;
}

export interface Deadline {
  label: string;
  /** YYYY-MM-DD */
  date: string;
  cycle: string;
}

export type SourcedField =
  | "weights"
  | "closingMerit"
  | "minInterPercent"
  | "admissionFee"
  | "feePerSemester"
  | "hostelPerYear";

export interface PlanOption {
  programId: string;
  universityId: string;
  universityName: string;
  universityShortName: string | null;
  sector: string | null;
  website: string | null;
  programName: string;
  city: string;
  testName: string;
  eligible: boolean;
  ineligibleReason: string | null;
  category: Category;
  /** One ready-to-show sentence explaining the category. */
  categoryReason: string;
  matricPercent: number;
  interPercent: number;
  academicPart: number | null;
  /** Only when the student gave an expected test score (or the program has no test). */
  aggregate: number | null;
  /** Test score needed to reach last closing merit. Can be below 0 or above 100. */
  requiredTestPercent: number | null;
  closingMerit: number | null;
  closingMeritCycle: string | null;
  weights: { matric: number; inter: number; test: number } | null;
  semesters: number;
  cost: Cost;
  scholarships: ScholarshipMatch[];
  nextDeadline: Deadline | null;
  /** Source chip for each number on the card. A missing key means "not officially published". */
  sources: Partial<Record<SourcedField, SourceRef>>;
}

export interface TimelineItem {
  date: string;
  label: string;
  universityName: string;
  programId: string;
  cycle: string;
  isPast: boolean;
  source: SourceRef;
}

export interface PlanSummary {
  safe: number;
  target: number;
  reach: number;
  unlikely: number;
  noData: number;
  notEligible: number;
  withinBudget: number;
}

export interface PlanResult {
  profile: StudentProfile;
  generatedAt: string;
  /** true while the backend still serves demo data - show a visible "demo data" banner. */
  dataIsFixture: boolean;
  summary: PlanSummary;
  /** Already sorted best-first: safe, target, reach, unlikely, no-data, not-eligible. */
  options: PlanOption[];
  timeline: TimelineItem[];
}

export interface Fact {
  /** "F1", "F2", ... */
  id: string;
  label: string;
  /** Ready-to-show value, e.g. "PKR 1,250,000" or "74.0%". */
  display: string;
  kind: "sourced" | "calculated";
  source: SourceRef | null;
}

export interface MentorAnswer {
  /** Contains [[F#]] tokens, never raw digits. Render with <MentorText />. */
  text: string;
  /** Plain-text version with every token already replaced. */
  rendered: string;
  /** Only the facts used in `text`. */
  facts: Fact[];
  /** true when the template answer was used (no key, provider down, or the guard rejected the model). */
  usedFallback: boolean;
}

export interface SourceRow {
  field: SourcedField | "deadline" | "scholarship";
  label: string;
  value: string | number | Record<string, number> | null;
  /** Ready-to-show value, or "Not officially published". */
  display: string;
  published: boolean;
  source: SourceRef | null;
}

export interface UniversitySources {
  universityId: string;
  universityName: string;
  shortName: string | null;
  city: string;
  sector: string | null;
  website: string | null;
  programId: string;
  programName: string;
  rows: SourceRow[];
}

export interface SourcesResponse {
  dataIsFixture: boolean;
  universities: UniversitySources[];
}

export interface Meta {
  groups: { value: Group; label: string }[];
  cities: string[];
  languages: { value: Language; label: string }[];
  categories: { value: Category; label: string }[];
  defaults: { matricTotal: number; interTotal: number; interPart1Total: number };
}

export interface Health {
  status: "ok";
  dataset: {
    universities: number;
    programs: number;
    scholarships: number;
    isFixture: boolean;
    placeholders: string[];
  };
  mentor: { llmConfigured: boolean; model: string | null; backupConfigured: boolean };
}
