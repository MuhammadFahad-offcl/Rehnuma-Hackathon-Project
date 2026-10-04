import { useLanguage } from "@/lib/i18n";
import type { PlanSummary } from "@/lib/rehnuma";

export function SummaryBar({ summary }: { summary: PlanSummary }) {
  const { t } = useLanguage();
  const items = [
    { label: "Safe", value: summary.safe, tone: "text-safe" },
    { label: "Target", value: summary.target, tone: "text-target" },
    { label: "Reach", value: summary.reach, tone: "text-reach" },
    { label: t("Within budget"), value: summary.withinBudget, tone: "text-ink" },
  ];
  return (
    <dl className="grid grid-cols-4 divide-x divide-line rounded-2xl border border-line bg-white">
      {items.map((item) => (
        <div key={item.label} className="px-2 py-3 text-center">
          <dd className={`num text-2xl font-extrabold ${item.tone}`}>{item.value}</dd>
          <dt className="text-xs font-medium text-muted sm:text-sm">{item.label}</dt>
        </div>
      ))}
    </dl>
  );
}
