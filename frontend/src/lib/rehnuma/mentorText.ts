// Splits a mentor answer into plain text and facts: every [[F#]] token becomes its fact.
import type { Fact } from "./types";

const TOKEN = /\[\[(F\d+)\]\]/g;

export function splitMentorText(text: string, facts: Fact[]): Array<string | Fact> {
  const byId = new Map(facts.map((fact) => [fact.id, fact]));
  const parts: Array<string | Fact> = [];
  let last = 0;
  for (const match of text.matchAll(TOKEN)) {
    const index = match.index ?? 0;
    if (index > last) parts.push(text.slice(last, index));
    const fact = byId.get(match[1]);
    if (fact) parts.push(fact);
    last = index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
