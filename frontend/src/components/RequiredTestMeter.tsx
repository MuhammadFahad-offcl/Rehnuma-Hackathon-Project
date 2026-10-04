// A 0-100 bar marked at the entry-test score the student needs.
import { useLanguage } from "@/lib/i18n";
import { formatPercent, type PlanOption } from "@/lib/rehnuma";
import { SourceChip } from "./SourceChip";

const FILL: Record<string, string> = {
  safe: "bg-safe",
  target: "bg-target",
  reach: "bg-reach",
  unlikely: "bg-unlikely",
};

export function RequiredTestMeter({ option, example }: { option: PlanOption; example?: boolean }) {
  const { t } = useLanguage();
  const required = option.requiredTestPercent;
  if (required === null) return null;

  const above = required > 100;
  const reached = required <= 0;
  const width = Math.max(0, Math.min(100, required));

  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <span className="text-sm font-medium text-muted">
          {t("Test score you need")} ({option.testName})
        </span>
        <span className="num text-2xl font-extrabold">
          {above ? "above 100%" : reached ? "0%" : formatPercent(required)}
        </span>
      </div>
      <div
        className="mt-2 h-2.5 overflow-hidden rounded-full bg-quiet-soft"
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(width)}
        aria-label={`${t("Test score you need")}: ${Math.round(width)}%`}
      >
        <div
          className={`h-full rounded-full ${above ? "bg-unlikely" : (FILL[option.category] ?? "bg-brand")}`}
          style={{ width: `${above ? 100 : width}%` }}
        />
      </div>
      {reached && <p className="mt-2 text-sm text-safe">Your marks alone reach the last closing merit.</p>}
      <dl className="mt-2.5 space-y-1.5 text-sm text-muted">
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
          <dt>Aggregate formula</dt>
          <dd>
            <SourceChip source={option.sources.weights} example={example} />
          </dd>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
          <dt>
            Last closing merit{option.closingMerit !== null && ` ${formatPercent(option.closingMerit)}`}
            {option.closingMeritCycle && ` (${option.closingMeritCycle})`}
          </dt>
          <dd>
            <SourceChip source={option.sources.closingMerit} example={example} />
          </dd>
        </div>
      </dl>
    </div>
  );
}
