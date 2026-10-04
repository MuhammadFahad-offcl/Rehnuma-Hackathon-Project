// The chip beside every number: Official/Unofficial, the date we verified it, and a link
// to the page it came from. No source = "not officially published".
import { useLanguage } from "@/lib/i18n";
import { formatDate, type SourceRef } from "@/lib/rehnuma";

interface SourceChipProps {
  source?: SourceRef | null;
  /** Example chips (landing page sample card) are not links. */
  example?: boolean;
}

const BASE = "inline-flex min-h-6 items-center whitespace-nowrap rounded-md px-1.5 py-0.5 text-xs font-medium";

export function SourceChip({ source, example = false }: SourceChipProps) {
  const { t } = useLanguage();

  if (!source) {
    return <span className={`${BASE} bg-quiet-soft text-quiet`}>{t("Not officially published").toLowerCase()}</span>;
  }

  const unofficial = source.confidence === "unofficial";
  const tone = unofficial ? "bg-reach-soft text-reach" : "bg-safe-soft text-safe";
  const label = `${unofficial ? "Unofficial" : "Official"} · verified ${formatDate(source.verifiedOn)}`;

  if (example) return <span className={`${BASE} ${tone}`}>{label}</span>;

  return (
    <a
      href={source.sourceUrl}
      target="_blank"
      rel="noopener noreferrer"
      title={`${source.sourceName} — opens the source page`}
      className={`${BASE} ${tone} underline decoration-current/40 underline-offset-2 hover:decoration-current`}
    >
      {label}
    </a>
  );
}
