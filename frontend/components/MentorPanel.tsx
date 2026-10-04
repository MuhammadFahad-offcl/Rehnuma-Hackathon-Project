// The AI mentor: a short explanation of the plan, then a question box with three suggested
// questions. The model never sends a raw number; MentorText fills in verified values.
import { useEffect, useRef, useState, type FormEvent } from "react";
import { SUGGESTED_QUESTIONS, useLanguage } from "@/lib/i18n";
import { askMentor, explainPlan, RehnumaApiError, type MentorAnswer, type PlanResult } from "@/lib/rehnuma";
import { MentorText } from "./MentorText";

const UNAVAILABLE = "The mentor is unavailable right now. Your plan above is complete.";
const MAX_QUESTION = 500;

type Status = "loading" | "ready" | "failed";
interface Exchange {
  question: string;
  answer: MentorAnswer | null;
  error: string | null;
}

function messageOf(error: unknown) {
  return error instanceof RehnumaApiError && error.status === 429 ? error.message : UNAVAILABLE;
}

function Answer({ answer }: { answer: MentorAnswer }) {
  return (
    <>
      <MentorText answer={answer} />
      {answer.usedFallback && (
        <p className="mt-1.5 text-xs text-muted">Quick summary. The AI model was not used for this reply.</p>
      )}
    </>
  );
}

export function MentorPanel({ plan }: { plan: PlanResult }) {
  const { language, t } = useLanguage();
  const [status, setStatus] = useState<Status>("loading");
  const [explanation, setExplanation] = useState<MentorAnswer | null>(null);
  const [explainError, setExplainError] = useState(UNAVAILABLE);
  const [chat, setChat] = useState<Exchange[]>([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const endOfChat = useRef<HTMLDivElement>(null);

  // The cards are already on screen; the explanation fills in when it arrives.
  // Changing the language asks again in the new language.
  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    explainPlan(plan.profile, language)
      .then((answer) => {
        if (cancelled) return;
        setExplanation(answer);
        setStatus("ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setExplainError(messageOf(error));
        setStatus("failed");
      });
    return () => {
      cancelled = true;
    };
  }, [plan, language]);

  async function ask(text: string) {
    const asked = text.trim().slice(0, MAX_QUESTION);
    if (!asked || asking) return;
    setAsking(true);
    setQuestion("");
    setChat((previous) => [...previous, { question: asked, answer: null, error: null }]);
    let result: Pick<Exchange, "answer" | "error">;
    try {
      result = { answer: await askMentor(plan.profile, language, asked), error: null };
    } catch (error) {
      result = { answer: null, error: messageOf(error) };
    }
    setChat((previous) => previous.map((item, index) => (index === previous.length - 1 ? { ...item, ...result } : item)));
    setAsking(false);
    endOfChat.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  return (
    <section aria-labelledby="mentor-heading" className="rounded-2xl border border-brand/20 bg-brand-soft/60 p-5 sm:p-6">
      <h2 id="mentor-heading" className="flex items-center gap-2 text-lg font-extrabold">
        <span aria-hidden>🧑‍🏫</span> Your mentor
      </h2>

      <div className="mt-3 text-[15px]" aria-live="polite">
        {status === "loading" && <p className="text-muted">Mentor is reading your plan…</p>}
        {status === "failed" && <p className="text-muted">{explainError}</p>}
        {status === "ready" && explanation && <Answer answer={explanation} />}
      </div>

      {chat.length > 0 && (
        <ul className="mt-4 space-y-3">
          {chat.map((item, index) => (
            <li key={index} className="space-y-2">
              <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-brand px-3.5 py-2 text-[15px] text-white">
                {item.question}
              </p>
              <div className="max-w-[95%] rounded-2xl rounded-bl-md bg-white px-3.5 py-2.5 text-[15px]">
                {item.answer ? (
                  <Answer answer={item.answer} />
                ) : item.error ? (
                  <p className="text-muted">{item.error}</p>
                ) : (
                  <p className="text-muted">Thinking…</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      <div ref={endOfChat} />

      <div className="mt-4 flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((suggestion) => (
          <button
            key={suggestion.en}
            type="button"
            disabled={asking}
            onClick={() => void ask(suggestion[language])}
            className="min-h-11 rounded-full border border-brand/30 bg-white px-3.5 text-left text-sm font-medium text-brand-dark hover:border-brand disabled:opacity-60"
          >
            {suggestion[language]}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="mt-3 flex flex-col gap-2 sm:flex-row">
        <label htmlFor="mentor-question" className="sr-only">
          {t("Ask the mentor")}
        </label>
        <input
          id="mentor-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          maxLength={MAX_QUESTION}
          placeholder="Ask about your plan"
          className="min-h-12 min-w-0 rounded-xl border border-line bg-white px-3.5 text-base outline-none focus:border-brand sm:flex-1"
        />
        <button
          type="submit"
          disabled={asking || !question.trim()}
          className="min-h-12 shrink-0 rounded-xl bg-brand px-4 font-bold text-white hover:bg-brand-dark disabled:opacity-50"
        >
          {asking ? "Asking…" : t("Ask the mentor")}
        </button>
      </form>
      <p className="mt-2 text-xs text-muted">
        The mentor explains your plan in words. Every number it shows is filled in by code from verified data.
      </p>
    </section>
  );
}
