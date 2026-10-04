// One university, top to bottom: header, reason, required test score, aggregate, cost,
// scholarships, next deadline.
import { useLanguage } from "@/lib/i18n";
import { formatDate, formatPercent, type PlanOption } from "@/lib/rehnuma";
import { CategoryBadge } from "./CategoryBadge";
import { CostBlock } from "./CostBlock";
import { RequiredTestMeter } from "./RequiredTestMeter";
import { SourceChip } from "./SourceChip";

interface OptionCardProps {
  option: PlanOption;
  position: number;
  /** The landing page's sample card: chips are not links. */
  example?: boolean;
}

export function OptionCard({ option, position, example }: OptionCardProps) {
  const { t } = useLanguage();
  const muted = option.category === "not-eligible";

  return (
    <article
      className={`rounded-2xl border border-line bg-white p-5 sm:p-6 ${
        muted ? "opacity-75" : "shadow-[0_1px_2px_rgba(31,27,46,0.04),0_8px_24px_-12px_rgba(31,27,46,0.18)]"
      }`}
    >
      <header className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-muted">Option {position}</p>
          <h3 className="mt-0.5 text-xl font-extrabold leading-tight">{option.universityName}</h3>
          <p className="mt-1 text-sm text-muted">
            {option.programName}, {option.city}
          </p>
        </div>
        <CategoryBadge category={option.category} />
      </header>

      <p className="mt-3 text-[15px]">{option.categoryReason}</p>

      {!muted && (
        <div className="mt-5 space-y-5">
          <RequiredTestMeter option={option} example={example} />

          {option.aggregate !== null && (
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="text-sm font-medium text-muted">Your aggregate</span>
              <span className="num text-2xl font-extrabold">{formatPercent(option.aggregate)}</span>
            </div>
          )}

          <CostBlock option={option} example={example} />

          <div>
            <h4 className="text-sm font-medium text-muted">Scholarships to check</h4>
            {option.scholarships.length === 0 ? (
              <p className="mt-1 text-sm text-muted">No scholarship in our verified list matches this profile.</p>
            ) : (
              <ul className="mt-2 space-y-2.5">
                {option.scholarships.map((scholarship) => (
                  <li key={scholarship.id} className="text-[15px]">
                    <span className="font-semibold">{scholarship.name}</span>
                    <span className="text-muted"> — {scholarship.summary}</span>
                    <span className="mt-1 flex flex-wrap items-center gap-2">
                      <a
                        href={example ? undefined : scholarship.applyUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-semibold text-brand underline underline-offset-2"
                      >
                        Apply ↗
                      </a>
                      <SourceChip source={scholarship.source} example={example} />
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-xl bg-wash px-3.5 py-3">
            <h4 className="text-sm font-medium text-muted">{t("Next deadline")}</h4>
            {option.nextDeadline ? (
              <p className="mt-0.5 flex flex-wrap items-baseline justify-between gap-x-3">
                <span className="font-semibold">{option.nextDeadline.label}</span>
                <span className="whitespace-nowrap">
                  <span className="num font-extrabold">{formatDate(option.nextDeadline.date)}</span>{" "}
                  <span className="text-sm text-muted">{option.nextDeadline.cycle}</span>
                </span>
              </p>
            ) : (
              <p className="mt-0.5 text-muted">No upcoming date announced</p>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
