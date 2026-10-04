# Dataset guide

The three files in `backend/data/` are the only place university facts live. Right now they hold
**demo fixtures**. Replace them with verified data; no code change is needed.

```bash
cd backend
python validate_data.py            # structure and sources: must print OK
python validate_data.py --strict   # also fails while FIXTURE / example.com / TODO / sample remain
```

CI runs the first command on every push. Run `--strict` yourself before the demo.

## What to collect (from the PRD)

Eight universities, one program (BS Computer Science), at least five scholarships.
Starting list, with a backup when an official fee page cannot be found in 15 minutes:

| # | University | City | Backup |
|---|---|---|---|
| 1 | NUST | Islamabad | Air University |
| 2 | FAST-NUCES | Lahore | Bahria University |
| 3 | UET Lahore | Lahore | |
| 4 | Punjab University (FCIT) | Lahore | |
| 5 | COMSATS University | Lahore | |
| 6 | ITU | Lahore | UCP |
| 7 | GIKI | Topi | LUMS |
| 8 | UMT | Lahore | |

For each one: eligible groups and minimum inter %, entry test name, aggregate weights, last closing
merit and its cycle, admission fee, fee per semester, hostel per year, and deadlines (test registration,
test date, application deadline). About 40 minutes per university. If the plan slips, drop to five.

## Where a number may come from

| Source type | Examples | Allowed for |
|---|---|---|
| Official | University website, prospectus or fee PDF, HEC, a government scholarship portal | Every field |
| Unofficial | News sites, student forums, academy pages | Closing merit only, with `"confidence": "unofficial"` |
| Never | A number from an AI assistant or a search-result snippet | Nothing |

Use search or an AI assistant only to *find* the official page. A team member reads the number on the
page and types it in; `verifiedOn` is the date that person read it. For a PDF, write the page number in `note`.

Common traps: a fee quoted per credit hour (multiply by a regular semester's credit hours and write the
maths in `note`); fees that differ by campus (use the campus in the listed city); several merit lists
(use the final list's last aggregate); merit published as positions, not percentages (store `null`).

## Rules

1. **Every number a student sees is a sourced value**:

   ```json
   {
     "value": 78.0,
     "sourceName": "University admissions page",
     "sourceUrl": "https://…official page…",
     "verifiedOn": "2026-10-04",
     "confidence": "official"
   }
   ```

   `confidence` is `official` (the university's or HEC's own page/PDF) or `unofficial` (anything else).
   `verifiedOn` is the day a team member opened the link and checked the number, as `YYYY-MM-DD`.
2. **Unknown is `null`** — never `0`, never an estimate. The engine shows "No data" or
   "Not officially published".
3. Weights must add up to 100.
4. Put years and cycles in `closingMeritCycle` / `cycle`, not in names.
5. Avoid digits in university and test names where possible: the mentor's digit guard rejects any
   AI answer that contains a digit, so a name with a digit forces the template answer.

## `universities.json`

```json
{ "id": "uni-id", "name": "Full name", "shortName": "ABC", "city": "Lahore",
  "sector": "public", "website": "https://…" }
```

`sector` is `public` or `private`. `city` is compared with the student's home city (case-insensitive)
to decide whether hostel cost applies.

## `programs.json`

| Field | Type | Notes |
|---|---|---|
| `id` | string | unique, e.g. `uni-id-bscs` |
| `universityId` | string | must exist in `universities.json` |
| `name` | string | e.g. `BS Computer Science` |
| `eligibleGroups` | list | from `pre-engineering`, `ics`, `pre-medical`, `icom`, `fa` |
| `testName` | string | entry test name |
| `semesters` | integer | usually 8 |
| `minInterPercent` | sourced number or `null` | minimum inter % to apply |
| `weights` | sourced `{matric, inter, test}` or `null` | aggregate formula, sums to 100 |
| `closingMerit` | sourced number or `null` | last closing merit, 0–100 |
| `closingMeritCycle` | string or `null` | required when `closingMerit` is set, e.g. `Fall 2026` |
| `admissionFee` | sourced number | one-time fee, **required** |
| `feePerSemester` | sourced number | **required**, must be > 0 |
| `hostelPerYear` | sourced number or `null` | `null` when not published |
| `deadlines` | list | `{ "label", "cycle", "date": sourced "YYYY-MM-DD" }` |

## `scholarships.json`

```json
{
  "id": "sch-id",
  "name": "Scholarship name",
  "provider": "Who gives it",
  "universityIds": "all",
  "type": "need",
  "minInterPercent": 60,
  "maxFamilyIncomeMonthly": 80000,
  "summary": { "value": "One plain sentence.", "sourceName": "…", "sourceUrl": "https://…",
               "verifiedOn": "2026-10-04", "confidence": "official" },
  "applyUrl": "https://…"
}
```

`universityIds` is `"all"` or a list of university ids. `minInterPercent` and
`maxFamilyIncomeMonthly` may be `null`. A need-based scholarship is hidden only when the student
entered an income above the cap; with no income entered it is still listed.

## Tests do not depend on this folder

The test suite uses its own frozen copy in `backend/tests/fixtures/`, so replacing the real dataset
never breaks tests. One test (`test_shipped_dataset_is_structurally_valid`) runs the validator on
whatever is in `backend/data/`.
