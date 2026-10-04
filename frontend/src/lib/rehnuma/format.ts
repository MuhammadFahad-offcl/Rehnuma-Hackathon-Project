// Display helpers. Formatting only - never calculate a plan number in the frontend.
import type { Category } from "./types";

export const formatPKR = (amount: number) => "PKR " + Math.round(amount).toLocaleString("en-US");

/** 1250000 -> "12.5 lakh". Show it in grey beside the PKR figure. */
export const formatLakh = (amount: number) => (amount / 100000).toFixed(1).replace(/\.0$/, "") + " lakh";

export const formatPercent = (value: number) => value.toFixed(1) + "%";

/** "2027-07-15" -> "15 Jul 2027" */
export const formatDate = (iso: string) =>
  new Date(iso + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

export const FEES_NOTE = "Calculated at current fees. Fees can rise each year.";
export const PART1_NOTE = "Based on Part 1 marks";

export const NOT_PUBLISHED = "Not officially published";

export const CATEGORY_LABEL: Record<Category, string> = {
  safe: "Safe",
  target: "Target",
  reach: "Reach",
  unlikely: "Unlikely",
  "no-data": "No data",
  "not-eligible": "Not eligible",
};
