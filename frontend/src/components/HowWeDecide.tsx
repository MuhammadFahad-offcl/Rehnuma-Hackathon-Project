// The category rules, in a collapsible box. These are our own product rules, so we show them.
const RULES = [
  ["Safe", "Test score needed is 60% or less.", "Aggregate is 3 or more points above closing merit."],
  ["Target", "Needed score is above 60% and up to 75%.", "From 2 points below to under 3 points above."],
  ["Reach", "Needed score is above 75% and up to 90%.", "From 7 points below to under 2 points below."],
  ["Unlikely", "Needed score is above 90%.", "More than 7 points below."],
] as const;

export function HowWeDecide() {
  return (
    <details className="group rounded-2xl border border-line bg-white">
      <summary className="flex min-h-12 cursor-pointer list-none items-center justify-between gap-3 px-5 py-3 font-bold">
        How we decide
        <span aria-hidden className="text-muted transition-transform group-open:rotate-180">
          ▾
        </span>
      </summary>
      <div className="border-t border-line px-5 py-4 text-[15px]">
        <p className="text-muted">
          Categories compare you with last year's closing merit. They are rules, not admission predictions.
        </p>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[30rem] text-left">
            <thead className="text-sm text-muted">
              <tr>
                <th className="py-1.5 pr-3 font-medium">Category</th>
                <th className="py-1.5 pr-3 font-medium">No expected test score</th>
                <th className="py-1.5 font-medium">With an expected test score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {RULES.map(([name, withoutScore, withScore]) => (
                <tr key={name}>
                  <th className="py-2 pr-3 font-bold">{name}</th>
                  <td className="py-2 pr-3">{withoutScore}</td>
                  <td className="py-2">{withScore}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="mt-3 list-disc space-y-1 pl-5">
          <li>No data: the formula or closing merit is not officially published. We never guess.</li>
          <li>Not eligible: your group is not accepted, or your inter percentage is below the minimum.</li>
          <li>Total cost is admission fee + tuition + hostel. Hostel counts only outside your home city.</li>
          <li>Scholarships are listed, not subtracted from the cost, because coverage differs by student.</li>
        </ul>
      </div>
    </details>
  );
}
