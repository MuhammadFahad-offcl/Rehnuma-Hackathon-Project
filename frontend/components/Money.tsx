import { formatLakh, formatPKR } from "@/lib/rehnuma";

/** Money is shown twice: the exact rupee figure, and beside it the amount in lakh. */
export function Money({ amount, bold = false }: { amount: number; bold?: boolean }) {
  return (
    <span className="num whitespace-nowrap">
      <span className={bold ? "text-lg font-extrabold" : "font-semibold"}>{formatPKR(amount)}</span>{" "}
      <span className="text-sm font-normal text-muted">{formatLakh(amount)}</span>
    </span>
  );
}
