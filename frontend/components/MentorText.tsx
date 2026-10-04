// Mentor text with each [[F7]] token replaced by the fact's verified value and its source.
import { splitMentorText, type MentorAnswer } from "@/lib/rehnuma";
import { SourceChip } from "./SourceChip";

export function MentorText({ answer }: { answer: MentorAnswer }) {
  return (
    <p className="leading-7">
      {splitMentorText(answer.text, answer.facts).map((part, index) =>
        typeof part === "string" ? (
          <span key={index}>{part}</span>
        ) : (
          <span key={index} className="num font-bold" title={part.label}>
            {part.display}{" "}
            {part.kind === "sourced" ? (
              <SourceChip source={part.source} />
            ) : (
              <span className="text-xs font-normal text-muted">calculated</span>
            )}
          </span>
        ),
      )}
    </p>
  );
}
