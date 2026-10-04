import { CATEGORY_LABEL, type Category } from "@/lib/rehnuma";

// Colour always comes with the word, never alone.
const TONE: Record<Category, string> = {
  safe: "bg-safe-soft text-safe",
  target: "bg-target-soft text-target",
  reach: "bg-reach-soft text-reach",
  unlikely: "bg-unlikely-soft text-unlikely",
  "no-data": "bg-quiet-soft text-quiet",
  "not-eligible": "bg-quiet-soft text-quiet",
};

export function CategoryBadge({ category }: { category: Category }) {
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-bold ${TONE[category]}`}>
      {CATEGORY_LABEL[category]}
    </span>
  );
}
