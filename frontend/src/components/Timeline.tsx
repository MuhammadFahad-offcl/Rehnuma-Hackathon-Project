// Every date for the shortlisted universities, in order. Past dates are greyed.
import { formatDate, type TimelineItem } from "@/lib/rehnuma";
import { SourceChip } from "./SourceChip";

export function Timeline({ items }: { items: TimelineItem[] }) {
  if (items.length === 0) {
    return <p className="text-muted">No dates have been announced for your options yet.</p>;
  }
  return (
    <ol className="space-y-0">
      {items.map((item, index) => (
        <li key={`${item.programId}-${item.date}-${index}`} className="relative flex gap-4 pb-5 last:pb-0">
          <span
            aria-hidden
            className={`mt-1.5 h-3 w-3 shrink-0 rounded-full border-2 ${
              item.isPast ? "border-line bg-white" : "border-brand bg-brand"
            }`}
          />
          {index < items.length - 1 && (
            <span aria-hidden className="absolute left-[5px] top-5 h-[calc(100%-1.25rem)] w-0.5 bg-line" />
          )}
          <div className={item.isPast ? "text-muted" : ""}>
            <p className="num font-extrabold">
              {formatDate(item.date)}
              {item.isPast && <span className="ml-2 text-xs font-medium">passed</span>}
            </p>
            <p className="text-[15px]">
              {item.label} — {item.universityName} <span className="text-sm text-muted">({item.cycle})</span>
            </p>
            <div className="mt-1">
              <SourceChip source={item.source} />
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
