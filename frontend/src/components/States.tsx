// What the student sees while waiting, when something fails, and when there is nothing to show.
import type { ReactNode } from "react";

export function LoadingState({ message }: { message: string }) {
  return (
    <div role="status" aria-live="polite" className="space-y-4">
      <p className="font-semibold text-muted">{message}</p>
      <div className="skeleton h-20" />
      <div className="skeleton h-64" />
      <div className="skeleton h-64" />
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="rounded-2xl border border-unlikely/30 bg-unlikely-soft px-5 py-4">
      <p className="font-bold text-unlikely">That did not work</p>
      <p className="mt-1 text-[15px]">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 min-h-11 rounded-xl bg-white px-4 font-semibold text-unlikely ring-1 ring-unlikely/40"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="rounded-2xl border border-dashed border-line bg-wash px-5 py-8 text-center">{children}</div>;
}

export function DemoBanner() {
  return (
    <div role="note" className="rounded-xl border border-reach/30 bg-reach-soft px-4 py-3 text-[15px] text-ink">
      <strong className="text-reach">Demo data.</strong> These universities and figures are placeholders, not real
      numbers. They will be replaced by the verified dataset.
    </div>
  );
}
