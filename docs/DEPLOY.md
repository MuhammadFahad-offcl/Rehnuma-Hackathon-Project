# Deploying Rehnuma on Vercel — step by step

The repo has two folders and each becomes its own Vercel project:

| Folder | What it is | Vercel project |
|---|---|---|
| `backend/` | Python API: calculates the plan, runs the AI mentor | Project 1, e.g. `rehnuma-api` |
| `frontend/` | The website students open | Project 2, e.g. `rehnuma` |

Do the steps in order: the frontend needs the backend's address. You need three free accounts:
**GitHub**, **Vercel** (sign in with GitHub) and **Groq**. No terminal is needed.

---

## Step 1 — Put the code on GitHub (5 minutes)

1. Unzip `rehnuma.zip`. Open the `rehnuma` folder. You should see `backend`, `frontend`, `docs`,
   `.github`, `README.md` and `.gitignore`.
2. Go to <https://github.com/new>. Repository name: `rehnuma`. Leave everything else as it is and
   click **Create repository**.
3. On the next page click the link **uploading an existing file**.
4. Drag the `backend` folder onto the page, wait for it to finish, and click **Commit changes**.
5. Click **Add file → Upload files** and do the same for `frontend`. Then once more for `docs`,
   `.github`, `README.md` and `.gitignore` together.

GitHub accepts at most 100 files per upload, which is why the folders go up one at a time.
Your repo should now show two main folders, `backend` and `frontend`.

<details>
<summary>Prefer the terminal?</summary>

```bash
cd rehnuma
git init -b main
git add .
git commit -m "Rehnuma: frontend and backend"
git remote add origin https://github.com/<you>/rehnuma.git
git push -u origin main
```
</details>

## Step 2 — Get a Groq key (2 minutes)

1. Sign in at <https://console.groq.com/keys>.
2. **Create API Key** and copy it. Keep it private; never put it in the repo.

Without a key the app still works, but the mentor only gives a fixed template answer.

## Step 3 — Deploy the backend (5 minutes)

1. Go to <https://vercel.com/new> and sign in with GitHub.
2. Find the `rehnuma` repo in the list and click **Import**.
3. On the configure screen:
   - **Project Name:** `rehnuma-api`
   - **Root Directory:** click **Edit**, choose `backend`
   - **Framework Preset:** Vercel should show **FastAPI** by itself
   - **Environment Variables:** add `GROQ_API_KEY` with your key from step 2
4. Click **Deploy** and wait about a minute.
5. Open the project and copy its address (under **Domains**), for example
   `https://rehnuma-api.vercel.app`.
6. Check it: open `<that address>/api/health`. You should see `"status":"ok"` and
   `"llmConfigured":true`.

## Step 4 — Deploy the frontend (5 minutes)

1. Go to <https://vercel.com/new> again and **Import** the same `rehnuma` repo a second time.
2. On the configure screen:
   - **Project Name:** `rehnuma`
   - **Root Directory:** click **Edit**, choose `frontend`
   - **Framework Preset:** Vercel should show **Vite** by itself
   - **Environment Variables:** add `VITE_REHNUMA_API_URL` with the backend address from step 3
     (no `/` at the end)
3. Click **Deploy**.
4. Open the address Vercel gives you. Click **Build my plan**, fill in the five steps, and you should
   see three demo universities with source chips and a mentor answer.

That address is your public demo URL. From now on, every change you commit to GitHub redeploys both
projects by themselves.

## Step 5 — Replace the demo data (the Data member's job)

The app works end to end, but on three placeholder universities. Fill in `backend/data/*.json`
following [DATA.md](DATA.md) and commit. The orange "Demo data" banner disappears once no
placeholder is left.

## Optional — a backup demo on Streamlit Cloud (5 minutes)

If something misbehaves on demo day, this runs the same engine and mentor on its own.

1. <https://share.streamlit.io> → **Create app** → pick the repo, branch `main`.
2. Main file path: `backend/demo_ui/streamlit_app.py`.
3. **Advanced settings → Secrets**: paste the two lines from
   `backend/demo_ui/.streamlit/secrets.toml.example` with your real key.
4. **Deploy**.

---

## If something goes wrong

| You see | Cause | Fix |
|---|---|---|
| "The backend address is not set" | `VITE_REHNUMA_API_URL` missing in the frontend project | Frontend project → Settings → Environment Variables → add it → Deployments → ⋯ → **Redeploy** |
| "Could not reach the Rehnuma server" | The address is wrong or has a `/` at the end | Open `<backend>/api/health` in the browser; fix the variable; redeploy |
| Changed a variable but nothing changed | Variables are read when the project is built | Deployments → ⋯ → **Redeploy** |
| Mentor always says "Quick summary" | No key, or an old model name | Backend project → Environment Variables: `GROQ_API_KEY` set; remove `LLM_MODEL_ID`/`GROQ_MODEL` if you added one, or set `LLM_MODEL_ID` to `openai/gpt-oss-20b` |
| Backend build fails or shows 404 | Root Directory is not `backend` | Backend project → Settings → General → Root Directory |
| Frontend page refresh shows 404 | Root Directory is not `frontend` | Frontend project → Settings → General → Root Directory |
| The site uses your own domain and the plan will not load | The backend only trusts `*.vercel.app` and localhost | Backend project → add `ALLOWED_ORIGINS` = `https://your-domain.com` → redeploy |

## Before the demo

- [ ] `<backend>/api/health` shows `"isFixture": false` (real data is in) and `"llmConfigured": true`.
- [ ] Personas A, B and C load without an error on a phone.
- [ ] Every number on persona A's plan opens a working source link.
- [ ] The mentor answers in English and Roman Urdu.
- [ ] Remove `GROQ_API_KEY` in Vercel, redeploy, and confirm the mentor still answers (template). Put it back.
- [ ] No API key in the repo, screenshots or slides.

## Backend settings (all optional except the key)

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | none | Key for the AI mentor |
| `LLM_MODEL_ID` | `openai/gpt-oss-20b` | Model name |
| `LLM_BASE_URL` | Groq | Any OpenAI-compatible endpoint |
| `BACKUP_LLM_API_KEY`, `BACKUP_LLM_BASE_URL`, `BACKUP_LLM_MODEL_ID` | none | Second provider, tried when the first fails |
| `ALLOWED_ORIGINS` | none | Extra website addresses allowed to call the API |
| `MENTOR_RATE_LIMIT_PER_MIN` | `20` | Mentor questions per visitor per minute |
