import { useEffect } from "react";
import { Link } from "react-router-dom";
import { OptionCard } from "@/components/OptionCard";
import { warmUp, type PlanOption, type SourceRef } from "@/lib/rehnuma";

const STEPS = [
  {
    emoji: "✍️",
    title: "Enter your profile",
    text: "Your marks, group, budget and home city. No account needed.",
  },
  {
    emoji: "🗺️",
    title: "Get your plan",
    text: "See Safe, Target and Reach universities with costs and deadlines.",
  },
  {
    emoji: "🔍",
    title: "Check every source",
    text: "Tap any chip to open the official page the number came from.",
  },
];

const TRUST = [
  {
    emoji: "🔗",
    title: "Sources, not guesses",
    text: "Each figure links to where it was published and when we verified it.",
  },
  {
    emoji: "🧮",
    title: "Code does the maths",
    text: "Aggregates and costs are calculated by fixed formulas. AI only explains them.",
  },
  {
    emoji: "🙅",
    title: "Honest about gaps",
    text: "If a university hasn't published a number, we say so instead of inventing one.",
  },
];

// The sample card is an illustration with made-up numbers, so it uses a made-up university.
const exampleSource = (confidence: SourceRef["confidence"] = "official"): SourceRef => ({
  sourceName: "Example source",
  sourceUrl: "#",
  verifiedOn: "2026-09-12",
  confidence,
});

const EXAMPLE: PlanOption = {
  programId: "example",
  universityId: "example",
  universityName: "Sample University",
  universityShortName: "SU",
  sector: "private",
  website: null,
  programName: "BS Computer Science",
  city: "Islamabad",
  testName: "Sample Entry Test",
  eligible: true,
  ineligibleReason: null,
  category: "target",
  categoryReason: "You need 74.0% in Sample Entry Test to reach the last closing merit of 78.0% (Fall 2026).",
  matricPercent: 90,
  interPercent: 80,
  academicPart: 41,
  aggregate: null,
  requiredTestPercent: 74,
  closingMerit: 78,
  closingMeritCycle: "Fall 2026",
  weights: { matric: 10, inter: 40, test: 50 },
  semesters: 8,
  cost: {
    tuition: 960000,
    admissionFee: 30000,
    hostel: 0,
    total: 990000,
    withinBudget: true,
    gap: -510000,
    hostelApplies: true,
    hostelUnknown: true,
  },
  scholarships: [
    {
      id: "example-merit",
      name: "Merit Scholarship",
      provider: "Sample University",
      type: "merit",
      summary: "Tuition support for top-ranked admitted students.",
      applyUrl: "#",
      source: exampleSource(),
    },
  ],
  nextDeadline: { label: "Admission test registration", date: "2027-06-10", cycle: "Fall 2027" },
  sources: {
    weights: exampleSource(),
    closingMerit: exampleSource("unofficial"),
    admissionFee: exampleSource(),
    feePerSemester: exampleSource(),
  },
};

const buttonPrimary =
  "inline-flex min-h-12 items-center justify-center rounded-xl bg-brand px-6 text-base font-bold text-white hover:bg-brand-dark";
const buttonQuiet =
  "inline-flex min-h-12 items-center justify-center rounded-xl border border-line bg-white px-6 text-base font-bold text-ink hover:border-brand";

export default function Landing() {
  useEffect(() => warmUp(), []);

  return (
    <>
      <section className="bg-wash">
        <div className="mx-auto grid max-w-5xl items-center gap-10 px-4 py-14 md:grid-cols-[1.25fr_1fr] md:py-20">
          <div>
            <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight sm:text-5xl">
              Find the university that fits your marks, budget and city.
            </h1>
            <p className="mt-5 max-w-xl text-lg text-muted">
              Rehnuma shows university options built only from published university data, with a source beside
              every number.
            </p>
            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <Link to="/profile" className={buttonPrimary}>
                Build my plan →
              </Link>
              <Link to="/#how" className={buttonQuiet}>
                See how it works
              </Link>
            </div>
            <ul className="mt-7 flex flex-wrap gap-2 text-sm font-semibold">
              {["✅ Every number has a source", "🧮 Calculated by code, not AI", "📱 Made for phones"].map((point) => (
                <li key={point} className="rounded-full border border-line bg-white px-3 py-1.5">
                  {point}
                </li>
              ))}
            </ul>
          </div>

          <div aria-hidden className="mx-auto w-full max-w-sm rounded-3xl border border-line bg-white p-6">
            <p className="text-center text-5xl leading-none tracking-wide sm:text-6xl">🧑🏽‍🎓👩🏻‍💻🧕🏽👨🏾‍🎓</p>
            <dl className="mt-6 space-y-3 text-[15px]">
              <div className="flex items-center justify-between rounded-xl bg-safe-soft px-3.5 py-2.5 font-bold text-safe">
                <dt>Safe</dt>
                <dd>marks already close to merit</dd>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-target-soft px-3.5 py-2.5 font-bold text-target">
                <dt>Target</dt>
                <dd>a good test gets you there</dd>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-reach-soft px-3.5 py-2.5 font-bold text-reach">
                <dt>Reach</dt>
                <dd>needs a very strong test</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <section id="how" className="scroll-mt-20">
        <div className="mx-auto max-w-5xl px-4 py-14">
          <h2 className="text-3xl font-extrabold tracking-tight">How it works</h2>
          <ol className="mt-8 grid gap-5 md:grid-cols-3">
            {STEPS.map((step, index) => (
              <li key={step.title} className="rounded-2xl border border-line p-5">
                <p className="text-3xl" aria-hidden>
                  {step.emoji}
                </p>
                <p className="mt-3 text-sm font-bold text-brand">Step {index + 1}</p>
                <h3 className="text-xl font-extrabold">{step.title}</h3>
                <p className="mt-1.5 text-muted">{step.text}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="preview" className="scroll-mt-20 bg-wash">
        <div className="mx-auto max-w-5xl px-4 py-14">
          <h2 className="text-3xl font-extrabold tracking-tight">This is what a result looks like</h2>
          <p className="mt-2 max-w-2xl text-muted">
            An example card with made-up numbers. Your plan shows real universities, and every chip opens the page
            the number came from.
          </p>
          <div className="mt-8 max-w-2xl">
            <OptionCard option={EXAMPLE} position={1} example />
          </div>
        </div>
      </section>

      <section id="trust" className="scroll-mt-20">
        <div className="mx-auto max-w-5xl px-4 py-14">
          <h2 className="text-3xl font-extrabold tracking-tight">Why trust Rehnuma</h2>
          <ul className="mt-8 grid gap-8 md:grid-cols-3">
            {TRUST.map((item) => (
              <li key={item.title}>
                <p className="text-3xl" aria-hidden>
                  {item.emoji}
                </p>
                <h3 className="mt-3 text-xl font-extrabold">{item.title}</h3>
                <p className="mt-1.5 text-muted">{item.text}</p>
              </li>
            ))}
          </ul>
          <div className="mt-12 flex flex-col items-start gap-4 rounded-3xl bg-brand px-6 py-8 text-white sm:flex-row sm:items-center sm:justify-between sm:px-8">
            <p className="text-2xl font-extrabold leading-tight">Ready? It takes under a minute.</p>
            <Link
              to="/profile"
              className="inline-flex min-h-12 items-center rounded-xl bg-white px-6 font-bold text-brand hover:bg-brand-soft"
            >
              Build my plan →
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
