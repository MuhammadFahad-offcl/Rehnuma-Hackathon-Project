# Rehnuma — a sourced university plan for Pakistani students

A student enters matric/inter marks, group, budget and home city. Rehnuma returns a plan:
which universities are **Safe / Target / Reach**, what the whole degree costs, which
scholarships to check and which deadlines are next — with a source and a date next to every number.

**The rule the whole project is built on: numbers come from code and a sourced dataset, never from the AI.**
The AI mentor only explains a plan that is already calculated, and it cannot type a number
(see [How the mentor is kept honest](#how-the-mentor-is-kept-honest)).

> **Dataset status: demo data.** `backend/data/` currently holds three placeholder universities
> ("Demo University … (FIXTURE)"). The app says so on screen and `python validate_data.py --strict`
> fails until the verified dataset is added. See [docs/DATA.md](docs/DATA.md).

## Two folders, two deployments

```text
frontend/   React + TypeScript + Tailwind (Vite)      → Vercel project 1
backend/    FastAPI: engine + AI mentor + dataset     → Vercel project 2
```

```text
 frontend                                     backend
 /          landing page
 /profile   5-step form   ── POST /api/plan ──►  engine/   deterministic agents ──► plan
 /plan      cards, timeline ◄─── plan JSON ────  data/     sourced JSON dataset
            mentor panel  ── POST /api/chat ──►  mentor/   facts → LLM → digit guard → fallback
 /sources   tables        ── GET /api/sources ►  app/      routes, validation, CORS
                                                      │
                                                      └─ Groq (or any OpenAI-compatible LLM)
```

Step-by-step deployment: **[docs/DEPLOY.md](docs/DEPLOY.md)**.

## Repository layout

```text
backend/
  app/          FastAPI app (Vercel entrypoint: app/main.py), schemas, sources table
  engine/       pure calculation: aggregate, category, cost, eligibility, scholarships, timeline
  agents/       one deterministic agent per decision + the QA agent
  mentor/       AI mentor: facts, prompts, digit guard, fallback, LLM client, optional CrewAI crew
  data/         universities.json, programs.json, scholarships.json + loader + validator
  tests/        85 tests against a frozen fixture dataset
  demo_ui/      Streamlit backup UI (same engine and mentor, no server needed)
  validate_data.py · requirements.txt · vercel.json · .env.example
frontend/
  src/pages/        Landing, Profile (5-step form), Plan, Sources
  src/components/   OptionCard, SourceChip, CostBlock, RequiredTestMeter, MentorPanel, Timeline …
  src/lib/rehnuma/  typed API client (api.ts, types.ts, format.ts)
  package.json · vite.config.ts · vercel.json · .env.example
docs/           DEPLOY.md · DATA.md · INTEGRATION_NOTES.md
```

## Run it on your computer

Backend (Python 3.12+):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-dev.txt

python validate_data.py           # dataset check, must print OK
pytest -q                         # 85 tests
uvicorn app.main:app --reload --port 8000
```

Frontend (Node 20+), in a second terminal:

```bash
cd frontend
copy .env.example .env.local      # macOS/Linux: cp .env.example .env.local
npm install
npm run dev                       # http://localhost:5173
```

To turn on the AI mentor locally, copy `backend/.env.example` to `backend/.env` and add a Groq key.
Without a key everything still works: the mentor answers from a template.

## API

Interactive docs are at `<backend URL>/docs`.

| Route | What it does |
|---|---|
| `POST /api/plan` | Profile → finished plan. Deterministic, no AI. |
| `GET /api/sources` | Every sourced value with link, verification date and official/unofficial flag. |
| `POST /api/explain` | Mentor explains the plan. Body `{ profile, language }`. |
| `POST /api/chat` | Mentor answers one question. Body `{ profile, language, question }`. |
| `GET /api/meta` | Dropdown options: groups, cities, languages. |
| `GET /api/health` | Liveness, dataset status (`isFixture`), whether a mentor key is set. |

Bad input returns status 400 with `{ error, fields }`, where `fields` maps each field name to its messages.
`language` is `"en"` or `"roman-ur"`. The exact shapes are in
[`frontend/src/lib/rehnuma/types.ts`](frontend/src/lib/rehnuma/types.ts) and
[`backend/app/schemas.py`](backend/app/schemas.py) — change both together.

## How the plan is calculated

```text
percent      = obtained / total × 100
academic     = matric% × matricWeight/100 + inter% × interWeight/100
aggregate    = academic + test% × testWeight/100
requiredTest = (closingMerit − academic) × 100 / testWeight        (may be < 0 or > 100)

tuition = feePerSemester × semesters
hostel  = hostelPerYear × semesters/2      only when the university is in another city
total   = admissionFee + tuition + hostel  (scholarships are listed, never subtracted)
gap     = total − budget
```

| Category | No expected test score | With an expected test score |
|---|---|---|
| Safe | test needed ≤ 60% | aggregate ≥ closing merit + 3 |
| Target | > 60% and ≤ 75% | from −2 up to under +3 |
| Reach | > 75% and ≤ 90% | from −7 up to under −2 |
| Unlikely | > 90% | below −7 |
| No data | formula or closing merit not officially published | same |
| Not eligible | wrong group, or below the minimum inter % | same |

Categories compare the student with **last year's closing merit**. They are not admission predictions.

## How the mentor is kept honest

1. Code turns the finished plan into numbered facts: `F4 | … score needed | 74.0%`.
2. The model is told to never type a digit; to mention a number it writes `[[F4]]`.
3. A **digit guard** rejects any answer with a raw digit (Latin, Arabic or Urdu), an amount in words
   ("lakh", "crore", "thousand") or an unknown fact ID.
4. One retry. A second failure, a timeout or a provider error → a **template answer** built from the same facts.
5. The frontend swaps each token for the verified value and shows its source chip.
6. The server rebuilds the plan from the profile on every mentor call, so a tampered plan from a
   browser can never reach the model.

## Team

Add each member's name before submitting.

| Member | Role | Folder | Name |
|---|---|---|---|
| 1 | Team Lead and Integration | `backend/app`, deploy config, `docs/` | Muhammad Fahad |
| 2 | Data and Sources | `backend/data/*.json` | |
| 3 | Engine | `backend/engine`, `backend/agents`, `backend/tests` | |
| 4 | Frontend | `frontend/` | |
| 5 | AI Mentor | `backend/mentor` (ported from the TypeScript original) | |

What was merged from each submission, and what changed, is in
[docs/INTEGRATION_NOTES.md](docs/INTEGRATION_NOTES.md).

## Data sources

Every value in `backend/data/` carries its source name, link, the date a team member read it on the
official page, and an Official/Unofficial flag. Anything not officially published is stored as `null`
and shown as "not officially published". No value is estimated and none comes from an AI.
The app lists every source on the `/sources` page.

## Known issues

- The dataset is still demo data (see the note at the top).
- The mentor's digit guard blocks digits and common number words, not every spelled-out number.
- There is no login: the plan lives in the browser session only (login is a non-goal in the PRD).
