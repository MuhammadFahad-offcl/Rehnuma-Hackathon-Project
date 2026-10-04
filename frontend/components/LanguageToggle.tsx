import { useLanguage } from "@/lib/i18n";
import type { Language } from "@/lib/rehnuma";

const OPTIONS: { value: Language; label: string }[] = [
  { value: "en", label: "English" },
  { value: "roman-ur", label: "Roman Urdu" },
];

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();
  return (
    <div role="group" aria-label="Language" className="inline-flex rounded-full border border-line bg-white p-0.5">
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={language === option.value}
          onClick={() => setLanguage(option.value)}
          className={`min-h-9 rounded-full px-3 text-sm font-semibold transition-colors ${
            language === option.value ? "bg-brand text-white" : "text-muted hover:text-ink"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
