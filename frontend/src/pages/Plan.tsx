// The plan: summary, mentor, one card per university (best fit first), timeline, rules.
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { HowWeDecide } from "@/components/HowWeDecide";
import { LanguageToggle } from "@/components/LanguageToggle";
import { MentorPanel } from "@/components/MentorPanel";
import { OptionCard } from "@/components/OptionCard";
import { DemoBanner, EmptyState, LoadingState } from "@/components/States";
import { SummaryBar } from "@/components/SummaryBar";
import { Timeline } from "@/components/Timeline";
import { loadPlan, PART1_NOTE, type PlanResult } from "@/lib/rehnuma";

export default function Plan() {
  const navigate = useNavigate();
  const [plan, setPlan] = useState<PlanResult | null>(null);

  useEffect(() => {
    const saved = loadPlan();
    if (saved) setPlan(saved);
    else navigate("/profile", { replace: true });
  }, [navigate]);

  if (!plan) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <LoadingState message="Calculating from verified data" />
      </div>
    );
  }

  return (
    <div className="bg-wash">
      <div className="mx-auto max-w-2xl space-y-6 px-4 py-8 sm:py-10">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Your admission plan</h1>
            <p className="mt-1 text-muted">
              Universities that fit you best come first.{" "}
              <Link to="/profile" className="font-semibold text-brand underline underline-offset-2">
                Change my answers
              </Link>
            </p>
          </div>
          <LanguageToggle />
        </div>

        {plan.dataIsFixture && <DemoBanner />}

        <SummaryBar summary={plan.summary} />
        <p className="text-sm text-muted">
          Categories compare you with last year's closing merit. They are not admission predictions.
          {plan.profile.interStatus === "part1" && <strong className="text-ink"> {PART1_NOTE}.</strong>}
        </p>

        {plan.options.length === 0 ? (
          <EmptyState>
            <p className="font-bold">No university in our verified list is in your city.</p>
            <p className="mt-1 text-muted">Turn on "willing to relocate" to see more.</p>
            <Link
              to="/profile"
              className="mt-4 inline-flex min-h-11 items-center rounded-xl bg-brand px-5 font-bold text-white"
            >
              Change my answers
            </Link>
          </EmptyState>
        ) : (
          <>
            <MentorPanel plan={plan} />

            <section aria-label="Universities" className="space-y-5">
              {plan.options.map((option, index) => (
                <OptionCard key={option.programId} option={option} position={index + 1} />
              ))}
            </section>

            <section aria-labelledby="timeline-heading" className="rounded-2xl border border-line bg-white p-5 sm:p-6">
              <h2 id="timeline-heading" className="text-lg font-extrabold">
                Admission timeline
              </h2>
              <div className="mt-4">
                <Timeline items={plan.timeline} />
              </div>
            </section>
          </>
        )}

        <HowWeDecide />

        <p className="text-center text-sm text-muted">
          Every number comes from{" "}
          <Link to="/sources" className="font-semibold text-brand underline underline-offset-2">
            a published source
          </Link>
          . Nothing here is an admission guarantee.
        </p>
      </div>
    </div>
  );
}
