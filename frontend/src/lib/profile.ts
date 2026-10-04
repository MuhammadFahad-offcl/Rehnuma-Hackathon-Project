// The profile wizard's draft: what the student has typed so far, kept as strings
// so empty fields stay empty. Converted to a StudentProfileInput only on submit.
import type { Group, InterStatus, StudentProfileInput } from "./rehnuma/types";

export interface Draft {
  matricObtained: string;
  matricTotal: string;
  interObtained: string;
  interTotal: string;
  interStatus: InterStatus;
  group: Group | "";
  homeCity: string;
  otherCity: string;
  willingToRelocate: boolean;
  budgetTotal: string;
  familyIncomeMonthly: string;
  expectedTestPercent: string;
}

export const OTHER_CITY = "__other__";

export const EMPTY_DRAFT: Draft = {
  matricObtained: "",
  matricTotal: "1100",
  interObtained: "",
  interTotal: "1100",
  interStatus: "complete",
  group: "",
  homeCity: "",
  otherCity: "",
  willingToRelocate: true,
  budgetTotal: "",
  familyIncomeMonthly: "",
  expectedTestPercent: "",
};

export const STEPS = ["Marks", "Group", "City", "Budget", "Entry test"] as const;

/** Which wizard step owns each API field, so server errors land on the right screen. */
export const FIELD_STEP: Record<string, number> = {
  matricObtained: 0,
  matricTotal: 0,
  interObtained: 0,
  interTotal: 0,
  interStatus: 0,
  group: 1,
  homeCity: 2,
  willingToRelocate: 2,
  budgetTotal: 3,
  familyIncomeMonthly: 3,
  expectedTestPercent: 4,
};

const KEY = "rehnuma.draft";

export function loadDraft(): Draft {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? { ...EMPTY_DRAFT, ...(JSON.parse(raw) as Partial<Draft>) } : EMPTY_DRAFT;
  } catch {
    return EMPTY_DRAFT;
  }
}

export function saveDraft(draft: Draft): void {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(draft));
  } catch {
    // not persisted in private mode
  }
}

const num = (text: string) => Number(text.replace(/,/g, "").trim());
const isNumber = (text: string) => text.trim() !== "" && Number.isFinite(num(text));

export const cityOf = (draft: Draft) => (draft.homeCity === OTHER_CITY ? draft.otherCity : draft.homeCity).trim();

export type Errors = Partial<Record<keyof Draft, string>>;

function marks(obtained: string, total: string, label: string): string | undefined {
  if (!isNumber(obtained)) return `Enter your ${label} marks.`;
  if (!isNumber(total) || num(total) <= 0) return "Enter the total marks.";
  if (num(obtained) < 0) return "Marks cannot be negative.";
  if (num(obtained) > num(total)) return "Obtained marks cannot be more than total marks.";
  return undefined;
}

export function validateStep(step: number, draft: Draft): Errors {
  const errors: Errors = {};
  if (step === 0) {
    const matric = marks(draft.matricObtained, draft.matricTotal, "matric");
    if (matric) errors.matricObtained = matric;
    const inter = marks(draft.interObtained, draft.interTotal, "inter");
    if (inter) errors.interObtained = inter;
  }
  if (step === 1 && !draft.group) errors.group = "Choose your inter group.";
  if (step === 2 && !cityOf(draft)) {
    errors[draft.homeCity === OTHER_CITY ? "otherCity" : "homeCity"] = "Tell us your home city.";
  }
  if (step === 3) {
    if (!isNumber(draft.budgetTotal) || num(draft.budgetTotal) < 0) {
      errors.budgetTotal = "Enter your total budget for the whole degree, in rupees.";
    }
    if (draft.familyIncomeMonthly.trim() && (!isNumber(draft.familyIncomeMonthly) || num(draft.familyIncomeMonthly) < 0)) {
      errors.familyIncomeMonthly = "Enter a monthly income in rupees, or leave this empty.";
    }
  }
  if (step === 4 && draft.expectedTestPercent.trim()) {
    const value = num(draft.expectedTestPercent);
    if (!isNumber(draft.expectedTestPercent) || value < 0 || value > 100) {
      errors.expectedTestPercent = "Enter a percentage from 0 to 100, or leave this empty.";
    }
  }
  return errors;
}

/** An empty optional field is left out of the object. 0 is never sent for "empty". */
export function toProfile(draft: Draft): StudentProfileInput {
  const profile: StudentProfileInput = {
    matricObtained: num(draft.matricObtained),
    matricTotal: num(draft.matricTotal),
    interObtained: num(draft.interObtained),
    interTotal: num(draft.interTotal),
    interStatus: draft.interStatus,
    group: draft.group as Group,
    homeCity: cityOf(draft),
    willingToRelocate: draft.willingToRelocate,
    budgetTotal: num(draft.budgetTotal),
  };
  if (draft.familyIncomeMonthly.trim()) profile.familyIncomeMonthly = num(draft.familyIncomeMonthly);
  if (draft.expectedTestPercent.trim()) profile.expectedTestPercent = num(draft.expectedTestPercent);
  return profile;
}
