// Where every number comes from: one table per university.
import { useEffect, useState } from "react";
import { LanguageToggle } from "@/components/LanguageToggle";
import { SourceChip } from "@/components/SourceChip";
import { DemoBanner, ErrorState, LoadingState } from "@/components/States";
import { getSources, type SourcesResponse } from "@/lib/rehnuma";

export default function Sources() {
  const [data, setData] = useState<SourcesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getSources()
      .then((response) => !cancelled && setData(response))
      .catch((reason: unknown) => !cancelled && setError(reason instanceof Error ? reason.message : "Could not load the sources."));
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-extrabold tracking-tight">Where every number comes from</h1>
        <LanguageToggle />
      </div>
      <p className="mt-2 text-muted">
        Each value lists the page it was read on, the date a team member checked it, and whether that page is
        official. A value a university has not published is left empty, never estimated.
      </p>

      <div className="mt-6 space-y-8">
        {error && <ErrorState message={error} onRetry={() => setAttempt((count) => count + 1)} />}
        {!data && !error && <LoadingState message="Loading the sources" />}
        {data?.dataIsFixture && <DemoBanner />}

        {data?.universities.map((university) => (
          <section key={university.programId} aria-labelledby={`u-${university.programId}`}>
            <h2 id={`u-${university.programId}`} className="text-xl font-extrabold">
              {university.universityName}
            </h2>
            <p className="text-sm text-muted">
              {university.programName}, {university.city}
              {university.website && (
                <>
                  {" · "}
                  <a
                    href={university.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-brand underline underline-offset-2"
                  >
                    official website
                  </a>
                </>
              )}
            </p>
            <div className="mt-3 overflow-hidden rounded-2xl border border-line">
              <table className="w-full text-left text-[15px]">
                <thead className="bg-wash text-sm text-muted">
                  <tr>
                    <th className="px-4 py-2.5 font-medium">Field</th>
                    <th className="px-4 py-2.5 font-medium">Value and source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {university.rows.map((row, index) => (
                    <tr key={`${row.field}-${index}`} className="align-top">
                      <th className="w-2/5 px-4 py-3 font-medium text-muted">{row.label}</th>
                      <td className="px-4 py-3">
                        {row.published ? (
                          <>
                            <p className="num font-bold">{row.display}</p>
                            <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted">
                              <SourceChip source={row.source} />
                              <span>{row.source?.sourceName}</span>
                            </p>
                          </>
                        ) : (
                          <SourceChip source={null} />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
