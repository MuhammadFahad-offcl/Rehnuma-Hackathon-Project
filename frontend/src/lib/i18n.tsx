// UI language: English or Roman Urdu. Labels come from the AI member's labels.roman-ur.json;
// anything without a translation stays in English.
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import romanUrdu from "./rehnuma/labels.roman-ur.json";
import type { Language } from "./rehnuma/types";

const KEY = "rehnuma.language";
const LABELS: Record<string, string> = romanUrdu.labels;

interface LanguageValue {
  language: Language;
  setLanguage: (language: Language) => void;
  /** Translate a UI label. Pass the English text. */
  t: (english: string) => string;
}

const LanguageContext = createContext<LanguageValue | null>(null);

function stored(): Language {
  try {
    return sessionStorage.getItem(KEY) === "roman-ur" ? "roman-ur" : "en";
  } catch {
    return "en";
  }
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setState] = useState<Language>(stored);

  const setLanguage = useCallback((next: Language) => {
    setState(next);
    try {
      sessionStorage.setItem(KEY, next);
    } catch {
      // not persisted in private mode
    }
  }, []);

  const value = useMemo<LanguageValue>(
    () => ({
      language,
      setLanguage,
      t: (english) => (language === "roman-ur" ? (LABELS[english] ?? english) : english),
    }),
    [language, setLanguage],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageValue {
  const value = useContext(LanguageContext);
  if (!value) throw new Error("useLanguage must be used inside <LanguageProvider>");
  return value;
}

export const SUGGESTED_QUESTIONS: Record<Language, string>[] = romanUrdu.suggestedQuestions;
