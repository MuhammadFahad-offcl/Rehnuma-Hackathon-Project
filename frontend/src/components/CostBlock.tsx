// Tuition, admission fee, hostel, total and the gap against the family's budget.
import { useLanguage } from "@/lib/i18n";
import { FEES_NOTE, type PlanOption } from "@/lib/rehnuma";
import { Money } from "./Money";
import { SourceChip } from "./SourceChip";

export function CostBlock({ option, example }: { option: PlanOption; example?: boolean }) {
  const { t } = useLanguage();
  const { cost, sources } = option;
  const over = cost.gap > 0;

  return (
    <div>
      <h4 className="text-sm font-medium text-muted">Estimated {option.semesters / 2}-year cost</h4>
      <dl className="mt-2 divide-y divide-line text-[15px]">
        <Row label="Tuition">
          <Money amount={cost.tuition} />
          <SourceChip source={sources.feePerSemester} example={example} />
        </Row>
        <Row label="Admission fee">
          <Money amount={cost.admissionFee} />
          <SourceChip source={sources.admissionFee} example={example} />
        </Row>
        {cost.hostelApplies && (
          <Row label="Hostel">
            {cost.hostelUnknown ? (
              <span className="text-sm text-muted">hostel cost {t("Not officially published").toLowerCase()}</span>
            ) : (
              <>
                <Money amount={cost.hostel} />
                <SourceChip source={sources.hostelPerYear} example={example} />
              </>
            )}
          </Row>
        )}
        <Row label="Total">
          <Money amount={cost.total} bold />
        </Row>
      </dl>

      <div
        className={`mt-3 flex flex-wrap items-center justify-between gap-2 rounded-xl px-3.5 py-2.5 font-semibold ${
          over ? "bg-unlikely-soft text-unlikely" : "bg-safe-soft text-safe"
        }`}
      >
        <span>{over ? t("Over budget") : t("Within budget")}</span>
        <span className="num">
          {over ? "over by " : "under by "}
          <Money amount={Math.abs(cost.gap)} />
        </span>
      </div>
      <p className="mt-2 text-xs text-muted">{FEES_NOTE}</p>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 py-2">
      <dt className="text-muted">{label}</dt>
      <dd className="flex flex-wrap items-center justify-end gap-2">{children}</dd>
    </div>
  );
}
