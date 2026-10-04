# Integration notes

What came in, what was kept, and what changed while merging. Written for the team so everyone can
find their own work in the final repo.

## What was submitted

| Submission | Contents |
|---|---|
| `Rehnuma_Complete_Project.rar` | Python engine + agents + Streamlit app, 15 tests, fixture data, Groq mentor |
| `rehnuma-final.zip` | A shorter rewrite of the same engine + data validator + Sources page + CrewAI mentor, 6 tests, fixture data |
| `rehnuma-member5-ai.zip` | AI mentor as Next.js/TypeScript API routes (`lib/ai/*`, `/api/explain`, `/api/chat`) |
| Lovable frontend (live link only) | `/`, `/login`, `/profile` (5-step wizard), `/plan`. Its source code was not submitted |

## Against the original plan (PRD)

The PRD planned **one Next.js + TypeScript repo deployed on Vercel**: TypeScript engine, Zod-checked JSON
data, the mentor as Next.js routes, and a no-login UI with the form on `/`. What was actually built is a
Python engine, a Lovable prototype of the frontend, and only the mentor in the planned stack. This repo
integrates what was built rather than rebuilding to the plan, and keeps the PRD's contract:
`lib/types.ts` field names, the three API routes and their bodies, status 400 with `{ error, fields }`,
every calculation rule, the sorting order and the three "rules that protect the demo".

## Decisions

**Two folders, two Vercel projects.** `backend/` is one FastAPI service; `frontend/` is a React app that
calls it. Both deploy on Vercel from the same repo.

**One Python service.** The engine is Python and the mentor was TypeScript for Next.js, which cannot
run next to a Python engine. The mentor was ported to Python, file for file, so engine and mentor live in
one FastAPI service.

**Frontend rebuilt as code.** The Lovable project's source was never available, so `frontend/` is a new
React + TypeScript + Tailwind app. It reproduces the Lovable pages' structure and wording (landing page
sections, the 5-step profile form, the plan page) and implements every component in the Frontend member's
document: `SourceChip`, `OptionCard`, `RequiredTestMeter`, `CostBlock`, `Timeline`, `MentorPanel`,
`MentorText`, `HowWeDecide`, the language toggle and the loading/error/empty states. Colours and fonts are
chosen to that document's design rules, because the Lovable styling could not be read from here.

**Engine: the RAR version is the base.** Its plan output matches the contract Member 5's mentor reads
(`profile`, `eligible`, `testName`, `closingMerit`, `timeline[].programId`, `timeline[].source`). The
`final.zip` rewrite dropped those fields, so the mentor could not have built its facts from it. It also
crashed on a program with no entry test (`None <= 60`) and counted not-eligible options as "within budget".

**From `final.zip`:** the data validator (now `backend/data/validate.py` + `validate_data.py`, with more
checks), the Sources page (now `GET /api/sources` and the Streamlit page), the `note` field on sources,
the demo dataset (clearly labelled FIXTURE, with a no-data university and an unknown-hostel case), and the
CrewAI crew (kept as an optional mode).

**Mentor: Member 5's design, unchanged in behaviour.** Fact IDs → system prompt → one call with an
8-second timeout → digit guard → one retry → template fallback. Prompts, guard rules and fallback
sentences are the originals.

## Changes worth knowing about

| Change | Why |
|---|---|
| Default model `openai/gpt-oss-20b` instead of `llama-3.1-8b-instant` | Groq removed `llama-3.1-8b-instant` from free and developer tiers on 16 Aug 2026. With the old default every mentor call would have silently fallen back to the template. |
| Mentor routes take `profile` and rebuild the plan on the server | Closes the weakness Member 5 documented ("the request sends the plan from the browser"). The old body `{ plan, language }` still works; only `plan.profile` is read. |
| LLM client talks to any OpenAI-compatible endpoint, with an optional backup provider | Member 5's note: keep a second provider key ready. Failover is now automatic. |
| Guard also blocks `lakhs` / `crores`; `<think>…</think>` blocks are stripped | Small hardening for reasoning models. |
| `MentorAnswer` gained `rendered` | Plain-text answer with tokens already replaced, for the Streamlit UI and logs. |
| CrewAI is optional (`MENTOR_ENGINE=crewai`, `requirements-crew.txt`) | It is a very large dependency for a serverless function. Its output still passes through the same digit guard. |
| `POST /api/plan` returns 400 with `{ error, fields }` on bad input | PRD contract; the form shows `fields` beside the inputs. |
| Persona A, B and C tests; validator checks for scholarship `type`, `provider`, semesters 2–12; stale-value warning | Listed in the Engine and Data member documents but missing from the submissions. |
| Tests use `tests/fixtures/`, not `data/` | Both submissions' tests asserted exact numbers from the demo data, so adding the real dataset would have broken them. |
| Totals are optional in the API (default 1100, or 550 for inter part 1) | The form pre-fills them; a student only changes the total if their board's differs. |
| Language codes are `en` / `roman-ur` everywhere | The submissions disagreed (`roman-ur` vs `roman-urdu`, `en` vs `english`); in the RAR app this meant the Roman Urdu template was never selected. Old spellings are still accepted. |
| Dates use Pakistan time; `datetime.utcnow()` removed | Deadline "is past" should flip at midnight in Pakistan; `utcnow()` is deprecated. |
| Per-visitor rate limit on mentor routes, strict input validation, CORS allow-list | The API is public and spends LLM quota. On Vercel the rate limit is per running instance, so treat it as best-effort. |
| No login page; the sample card on the landing page uses a made-up "Sample University" | Login is a non-goal in the PRD and would need a database. The Lovable sample card showed a real university with invented numbers and "Official" chips, which contradicts "no number without a source". |
| Fixture deadline cycle relabelled `Fall 2027` | The fixture date was 2027-07-15 but labelled Fall 2026. |

## Not verified here

- **Live LLM calls.** No API key was available while integrating, so the Groq call is covered by tests with
  a mocked HTTP layer only. Check `/api/health` → `llmConfigured: true` and ask one question after deploying.
- **CrewAI mode** was not run (not installed). Only the "crewai missing → direct mentor" path is tested.
- **The Vercel deployments.** No Vercel account was available here. `backend/` follows Vercel's FastAPI
  guide (entrypoint `app/main.py`, `requirements.txt`, `vercel.json`) and was loaded that way from a clean
  install; `frontend/` builds from a clean `npm ci`. Neither was actually deployed.
- **Visual match with Lovable.** Text and page structure were read from the live Lovable site; its colours,
  fonts and steps 2 to 5 of its form could not be seen, so those are new.

## Tested in a browser

The built frontend was run against the local backend in Chromium at 375 px and 1280 px: landing page →
5-step form (with validation errors) → plan → suggested mentor question → Roman Urdu → Sources, plus the
empty state. No console errors, no horizontal scrolling, and every source chip on the plan links out.

## Open items

1. **No verified dataset was submitted.** Every archive contains placeholder universities only. This is the
   project's core claim (PRD feature F2: 8 universities, at least 5 scholarships), so it is the top priority.
   The Data document's rule applies: a person reads each number on the official page; a number from an AI
   assistant or a search snippet is never allowed. See `DATA.md`.
2. Still to come from the member documents: pitch deck and submission text (Data), backup demo video
   (Frontend), personas tested on the live URL (Engine).
