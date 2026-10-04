// The 5-step profile wizard: Marks, Group, City, Budget, Entry test.
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/lib/i18n";
import {
  cityOf,
  FIELD_STEP,
  loadDraft,
  OTHER_CITY,
  saveDraft,
  STEPS,
  toProfile,
  validateStep,
  type Draft,
  type Errors,
} from "@/lib/profile";
import {
  buildPlan,
  formatLakh,
  formatPKR,
  getMeta,
  RehnumaApiError,
  savePlan,
  warmUp,
  type Group,
  type InterStatus,
} from "@/lib/rehnuma";

const HEADINGS = ["Your marks 🎯", "Your group 📚", "Your city 🏙️", "Your budget 💰", "Entry test ✏️"];

const GROUPS: { value: Group; label: string; emoji: string }[] = [
  { value: "pre-engineering", label: "Pre-Engineering", emoji: "⚙️" },
  { value: "ics", label: "ICS", emoji: "💻" },
  { value: "pre-medical", label: "Pre-Medical", emoji: "🩺" },
  { value: "icom", label: "I.Com", emoji: "📊" },
  { value: "fa", label: "FA", emoji: "📖" },
];

const STATUSES: { value: InterStatus; label: string; emoji: string }[] = [
  { value: "part1", label: "Part 1", emoji: "📖" },
  { value: "complete", label: "Complete", emoji: "🎓" },
];

const BUDGET_PICKS = [500000, 1000000, 1500000, 2500000];

const inputClass =
  "min-h-12 w-full rounded-xl border border-line bg-white px-3.5 text-base outline-none focus:border-brand aria-[invalid=true]:border-unlikely";

function Field({
  label,
  htmlFor,
  hint,
  error,
  children,
}: {
  label: string;
  htmlFor: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block font-bold">
        {label}
      </label>
      <div className="mt-1.5">{children}</div>
      {hint && !error && <p className="mt-1.5 text-sm text-muted">{hint}</p>}
      {error && (
        <p role="alert" className="mt-1.5 text-sm font-semibold text-unlikely">
          {error}
        </p>
      )}
    </div>
  );
}

function Choice({
  selected,
  onClick,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={`flex min-h-12 items-center gap-2.5 rounded-xl border px-4 text-left font-semibold transition-colors ${
        selected ? "border-brand bg-brand-soft text-brand-dark" : "border-line bg-white hover:border-brand/50"
      }`}
    >
      {children}
    </button>
  );
}

export default function Profile() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [draft, setDraft] = useState<Draft>(loadDraft);
  const [step, setStep] = useState(0);
  const [errors, setErrors] = useState<Errors>({});
  const [cities, setCities] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [slow, setSlow] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);

  useEffect(() => {
    warmUp();
    getMeta()
      .then((meta) => setCities(meta.cities))
      .catch(() => setCities([]));
  }, []);

  useEffect(() => saveDraft(draft), [draft]);

  function set<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((previous) => ({ ...previous, [key]: value }));
    setErrors((previous) => ({ ...previous, [key]: undefined }));
  }

  function setStatus(status: InterStatus) {
    setDraft((previous) => {
      // Part 1 is marked out of half the total, unless the student already changed it.
      const untouched = previous.interTotal === "1100" || previous.interTotal === "550";
      return { ...previous, interStatus: status, interTotal: untouched ? (status === "part1" ? "550" : "1100") : previous.interTotal };
    });
  }

  function next(event: FormEvent) {
    event.preventDefault();
    const found = validateStep(step, draft);
    setErrors(found);
    if (Object.values(found).some(Boolean)) return;
    if (step < STEPS.length - 1) {
      setStep(step + 1);
      window.scrollTo(0, 0);
    } else {
      void submit();
    }
  }

  async function submit() {
    setSubmitting(true);
    setFailure(null);
    const timer = window.setTimeout(() => setSlow(true), 5000);
    try {
      const plan = await buildPlan(toProfile(draft));
      savePlan(plan);
      navigate("/plan");
    } catch (error) {
      if (error instanceof RehnumaApiError && error.status === 400) {
        // Show the server's field errors beside the inputs, on the step that owns the first one.
        const fromServer: Errors = {};
        let firstStep = STEPS.length - 1;
        for (const [field, messages] of Object.entries(error.fields)) {
          if (field in FIELD_STEP) {
            fromServer[field as keyof Draft] = messages[0];
            firstStep = Math.min(firstStep, FIELD_STEP[field]);
          }
        }
        if (Object.keys(fromServer).length > 0) {
          setErrors(fromServer);
          setStep(firstStep);
        } else {
          setFailure(error.message);
        }
      } else {
        setFailure(error instanceof Error ? error.message : "Something went wrong. Please try again.");
      }
    } finally {
      window.clearTimeout(timer);
      setSlow(false);
      setSubmitting(false);
    }
  }

  const budget = Number(draft.budgetTotal.replace(/,/g, ""));
  const last = step === STEPS.length - 1;

  return (
    <div className="bg-wash">
      <div className="mx-auto max-w-xl px-4 py-8 sm:py-12">
        <p className="text-sm font-bold text-brand">
          Step {step + 1} of {STEPS.length} · {STEPS[step]}
        </p>
        <div className="mt-2 flex gap-1.5" aria-hidden>
          {STEPS.map((name, index) => (
            <span key={name} className={`h-1.5 flex-1 rounded-full ${index <= step ? "bg-brand" : "bg-line"}`} />
          ))}
        </div>

        <form onSubmit={next} noValidate className="mt-5 rounded-3xl border border-line bg-white p-5 sm:p-7">
          <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{HEADINGS[step]}</h1>

          <div className="mt-6 space-y-6">
            {step === 0 && (
              <>
                <Field
                  label={t("Matric marks")}
                  htmlFor="matricObtained"
                  hint="Use your obtained marks, not the total."
                  error={errors.matricObtained ?? errors.matricTotal}
                >
                  <MarksInputs
                    id="matricObtained"
                    obtained={draft.matricObtained}
                    total={draft.matricTotal}
                    error={errors.matricObtained ?? errors.matricTotal}
                    onObtained={(value) => set("matricObtained", value)}
                    onTotal={(value) => set("matricTotal", value)}
                  />
                </Field>
                <Field
                  label={t("Inter marks")}
                  htmlFor="interObtained"
                  hint={
                    draft.interStatus === "part1"
                      ? "Your Part 1 marks. Part 1 is usually out of 550."
                      : "Use your obtained marks, not the total."
                  }
                  error={errors.interObtained ?? errors.interTotal}
                >
                  <MarksInputs
                    id="interObtained"
                    obtained={draft.interObtained}
                    total={draft.interTotal}
                    error={errors.interObtained ?? errors.interTotal}
                    onObtained={(value) => set("interObtained", value)}
                    onTotal={(value) => set("interTotal", value)}
                  />
                </Field>
                <fieldset>
                  <legend className="font-bold">Intermediate status</legend>
                  <div className="mt-2 grid grid-cols-2 gap-2.5">
                    {STATUSES.map((status) => (
                      <Choice
                        key={status.value}
                        selected={draft.interStatus === status.value}
                        onClick={() => setStatus(status.value)}
                      >
                        <span aria-hidden>{status.emoji}</span>
                        {status.label}
                      </Choice>
                    ))}
                  </div>
                </fieldset>
              </>
            )}

            {step === 1 && (
              <fieldset>
                <legend className="font-bold">Which group did you study in inter?</legend>
                <div className="mt-2 grid gap-2.5 sm:grid-cols-2">
                  {GROUPS.map((group) => (
                    <Choice key={group.value} selected={draft.group === group.value} onClick={() => set("group", group.value)}>
                      <span aria-hidden>{group.emoji}</span>
                      {group.label}
                    </Choice>
                  ))}
                </div>
                {errors.group && (
                  <p role="alert" className="mt-2 text-sm font-semibold text-unlikely">
                    {errors.group}
                  </p>
                )}
              </fieldset>
            )}

            {step === 2 && (
              <>
                <Field
                  label="Home city"
                  htmlFor="homeCity"
                  hint="If a university is in another city, we add its hostel cost."
                  error={errors.homeCity}
                >
                  {cities.length > 0 ? (
                    <select
                      id="homeCity"
                      value={draft.homeCity}
                      aria-invalid={Boolean(errors.homeCity)}
                      onChange={(event) => set("homeCity", event.target.value)}
                      className={inputClass}
                    >
                      <option value="">Choose your city</option>
                      {cities.map((city) => (
                        <option key={city} value={city}>
                          {city}
                        </option>
                      ))}
                      <option value={OTHER_CITY}>Other city</option>
                    </select>
                  ) : (
                    <input
                      id="homeCity"
                      value={draft.homeCity === OTHER_CITY ? draft.otherCity : draft.homeCity}
                      aria-invalid={Boolean(errors.homeCity)}
                      onChange={(event) => set("homeCity", event.target.value)}
                      placeholder="For example, Lahore"
                      className={inputClass}
                    />
                  )}
                </Field>
                {cities.length > 0 && draft.homeCity === OTHER_CITY && (
                  <Field label="Which city?" htmlFor="otherCity" error={errors.otherCity}>
                    <input
                      id="otherCity"
                      value={draft.otherCity}
                      aria-invalid={Boolean(errors.otherCity)}
                      onChange={(event) => set("otherCity", event.target.value)}
                      placeholder="For example, Multan"
                      className={inputClass}
                    />
                  </Field>
                )}
                <fieldset>
                  <legend className="font-bold">{t("Willing to relocate")}?</legend>
                  <div className="mt-2 grid grid-cols-2 gap-2.5">
                    <Choice selected={draft.willingToRelocate} onClick={() => set("willingToRelocate", true)}>
                      <span aria-hidden>🧳</span> Yes
                    </Choice>
                    <Choice selected={!draft.willingToRelocate} onClick={() => set("willingToRelocate", false)}>
                      <span aria-hidden>🏠</span> No
                    </Choice>
                  </div>
                  <p className="mt-1.5 text-sm text-muted">
                    {draft.willingToRelocate
                      ? "We show universities in every city."
                      : "We show only universities in your home city."}
                  </p>
                </fieldset>
              </>
            )}

            {step === 3 && (
              <>
                <Field
                  label={t("Total budget for the degree")}
                  htmlFor="budgetTotal"
                  hint={
                    budget > 0
                      ? `${formatPKR(budget)} is ${formatLakh(budget)}, for all years together.`
                      : "In rupees, for the whole degree. Not per semester."
                  }
                  error={errors.budgetTotal}
                >
                  <input
                    id="budgetTotal"
                    inputMode="numeric"
                    value={draft.budgetTotal}
                    aria-invalid={Boolean(errors.budgetTotal)}
                    onChange={(event) => set("budgetTotal", event.target.value)}
                    placeholder="1500000"
                    className={inputClass}
                  />
                  <div className="mt-2.5 flex flex-wrap gap-2">
                    {BUDGET_PICKS.map((amount) => (
                      <button
                        key={amount}
                        type="button"
                        onClick={() => set("budgetTotal", String(amount))}
                        className={`min-h-11 rounded-full border px-4 text-sm font-semibold ${
                          budget === amount ? "border-brand bg-brand-soft text-brand-dark" : "border-line hover:border-brand/50"
                        }`}
                      >
                        {formatLakh(amount)}
                      </button>
                    ))}
                  </div>
                </Field>
                <Field
                  label="Family monthly income (optional)"
                  htmlFor="familyIncomeMonthly"
                  hint="Used only to match need-based scholarships. Leave empty if you prefer."
                  error={errors.familyIncomeMonthly}
                >
                  <input
                    id="familyIncomeMonthly"
                    inputMode="numeric"
                    value={draft.familyIncomeMonthly}
                    aria-invalid={Boolean(errors.familyIncomeMonthly)}
                    onChange={(event) => set("familyIncomeMonthly", event.target.value)}
                    placeholder="60000"
                    className={inputClass}
                  />
                </Field>
              </>
            )}

            {step === 4 && (
              <>
                <Field
                  label="Expected entry-test score (optional)"
                  htmlFor="expectedTestPercent"
                  hint="A percentage. Leave empty if you have not taken a test: we show the score you need instead."
                  error={errors.expectedTestPercent}
                >
                  <input
                    id="expectedTestPercent"
                    inputMode="decimal"
                    value={draft.expectedTestPercent}
                    aria-invalid={Boolean(errors.expectedTestPercent)}
                    onChange={(event) => set("expectedTestPercent", event.target.value)}
                    placeholder="70"
                    className={inputClass}
                  />
                </Field>
                <div className="rounded-2xl bg-wash px-4 py-3.5">
                  <h2 className="font-bold">Check your answers</h2>
                  <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[15px]">
                    <dt className="text-muted">Matric</dt>
                    <dd className="num font-semibold">
                      {draft.matricObtained} / {draft.matricTotal}
                    </dd>
                    <dt className="text-muted">Inter</dt>
                    <dd className="num font-semibold">
                      {draft.interObtained} / {draft.interTotal}
                      {draft.interStatus === "part1" && " (Part 1)"}
                    </dd>
                    <dt className="text-muted">Group</dt>
                    <dd className="font-semibold">{GROUPS.find((group) => group.value === draft.group)?.label}</dd>
                    <dt className="text-muted">City</dt>
                    <dd className="font-semibold">
                      {cityOf(draft)}
                      {draft.willingToRelocate ? ", willing to relocate" : ", staying in this city"}
                    </dd>
                    <dt className="text-muted">Budget</dt>
                    <dd className="num font-semibold">{budget > 0 ? `${formatPKR(budget)} (${formatLakh(budget)})` : ""}</dd>
                  </dl>
                </div>
              </>
            )}
          </div>

          {failure && (
            <div role="alert" className="mt-6 rounded-xl bg-unlikely-soft px-4 py-3 text-[15px]">
              <p className="font-bold text-unlikely">We could not build your plan</p>
              <p>{failure}</p>
            </div>
          )}
          {submitting && (
            <p role="status" className="mt-6 text-[15px] font-semibold text-muted">
              Calculating from verified data…{slow && " The first plan can take a little longer."}
            </p>
          )}

          <div className="mt-7 flex items-center justify-between gap-3">
            {step > 0 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                disabled={submitting}
                className="min-h-12 rounded-xl px-4 font-bold text-muted hover:text-ink"
              >
                ← Back
              </button>
            ) : (
              <span />
            )}
            <button
              type="submit"
              disabled={submitting}
              className="min-h-12 rounded-xl bg-brand px-6 font-bold text-white hover:bg-brand-dark disabled:opacity-60"
            >
              {last ? (submitting ? "Building…" : `${t("Make my plan")} →`) : "Next →"}
            </button>
          </div>
        </form>

        <p className="mt-4 text-center text-sm text-muted">
          🔒 No login needed. Your plan stays in this browser session.
        </p>
      </div>
    </div>
  );
}

function MarksInputs({
  id,
  obtained,
  total,
  error,
  onObtained,
  onTotal,
}: {
  id: string;
  obtained: string;
  total: string;
  error?: string;
  onObtained: (value: string) => void;
  onTotal: (value: string) => void;
}) {
  return (
    <div className="flex items-center gap-2.5">
      <input
        id={id}
        inputMode="numeric"
        value={obtained}
        aria-invalid={Boolean(error)}
        onChange={(event) => onObtained(event.target.value)}
        placeholder="Obtained"
        className={inputClass}
      />
      <span className="shrink-0 text-muted">out of</span>
      <input
        aria-label="Total marks"
        inputMode="numeric"
        value={total}
        aria-invalid={Boolean(error && /total/i.test(error))}
        onChange={(event) => onTotal(event.target.value)}
        className={`${inputClass} max-w-24 text-center`}
      />
    </div>
  );
}
