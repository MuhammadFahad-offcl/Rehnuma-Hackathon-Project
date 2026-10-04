"""Rehnuma API - the backend the frontend talks to.

    POST /api/plan      profile -> finished plan (deterministic engine, no AI)
    GET  /api/sources   every sourced value with link, date and official/unofficial flag
    POST /api/explain   plan explanation from the AI mentor (fact tokens, digit guard, fallback)
    POST /api/chat      follow-up question to the mentor
    GET  /api/meta      dropdown options (groups, cities, languages)
    GET  /api/health    liveness + dataset/mentor status (also used to wake a sleeping free instance)

Run locally from the backend/ folder:

    uvicorn app.main:app --reload --port 8000

On Vercel this file is the entrypoint: Vercel looks for a FastAPI instance named
`app` in app/main.py.
"""
import logging
import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:  # local development convenience; in production the host sets real env vars
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

from data.loader import is_fixture, load_data, placeholder_markers
from engine.orchestrator import build_plan
from mentor import client as llm
from mentor import run_chat, run_explain

from app import settings
from app.schemas import (
    DEFAULT_PART1_TOTAL,
    DEFAULT_TOTAL,
    ChatRequest,
    ExplainRequest,
    Health,
    MentorAnswer,
    Meta,
    PlanResult,
    SourcesResponse,
    StudentProfile,
)
from app.sources import build_sources

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("rehnuma.api")

app = FastAPI(
    title="Rehnuma API",
    version="1.0.0",
    description=(
        "Marks + budget + city -> a transparent university plan. "
        "Every number comes from code and a sourced dataset; the AI mentor only explains."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allow_all_origins() else settings.allowed_origins(),
    allow_origin_regex=None if settings.allow_all_origins() else settings.origin_regex(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,  # the API uses no cookies or sessions
    max_age=600,
)


PROFILE_FIELDS = set(StudentProfile.model_fields) | {"question", "language", "profile"}


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, error: RequestValidationError):
    """Bad input -> 400 with {error, fields} (the PRD contract), so the form can show inline errors."""
    problems, fields = [], {}
    for item in error.errors():
        parts = [str(part) for part in item["loc"] if part not in ("body", "profile", "plan")]
        message = item["msg"].removeprefix("Value error, ")
        field = parts[-1] if parts else message.split(" ", 1)[0]
        if field not in PROFILE_FIELDS:
            field = "form"
        fields.setdefault(field, []).append(message)
        problems.append(message if message.startswith(field) else f"{field}: {message}")
    return JSONResponse(
        status_code=400,
        content={"error": "; ".join(problems), "fields": fields, "problems": problems},
    )


@app.exception_handler(HTTPException)
async def http_error(_: Request, error: HTTPException):
    return JSONResponse(status_code=error.status_code, content={"error": error.detail}, headers=error.headers)


# --- tiny in-memory rate limit for the two endpoints that spend LLM quota ----------------
_hits = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_limit(request: Request):
    limit = settings.mentor_rate_limit()
    if limit <= 0:
        return
    now = time.monotonic()
    window = _hits[_client_ip(request)]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many mentor questions. Please wait a minute and try again.",
            headers={"Retry-After": "60"},
        )
    window.append(now)
    if len(_hits) > 5000:  # keep memory bounded
        _hits.clear()


def _plan_for(profile: StudentProfile) -> dict:
    data = load_data()
    try:
        plan = build_plan(profile.model_dump(), data)
    except ValueError as error:  # QA agent refused the plan
        log.error("QA agent rejected a plan: %s", error)
        raise HTTPException(status_code=500, detail="The plan failed its quality check. Please try again.")
    plan["dataIsFixture"] = is_fixture(data)
    return plan


# --- routes ------------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    return {"name": "Rehnuma API", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health", response_model=Health)
def health():
    data = load_data()
    providers = llm.providers()
    return {
        "status": "ok",
        "dataset": {
            "universities": len(data["universities"]),
            "programs": len(data["programs"]),
            "scholarships": len(data["scholarships"]),
            "isFixture": is_fixture(data),
            "placeholders": placeholder_markers(data),
        },
        "mentor": {
            "llmConfigured": bool(providers),
            "model": providers[0].model if providers else None,
            "backupConfigured": len(providers) > 1,
        },
    }


@app.get("/api/meta", response_model=Meta)
def meta():
    data = load_data()
    return {
        "groups": [
            {"value": "pre-engineering", "label": "Pre-Engineering"},
            {"value": "ics", "label": "ICS"},
            {"value": "pre-medical", "label": "Pre-Medical"},
            {"value": "icom", "label": "I.Com"},
            {"value": "fa", "label": "FA"},
        ],
        "cities": sorted({u["city"] for u in data["universities"]}),
        "languages": [
            {"value": "en", "label": "English"},
            {"value": "roman-ur", "label": "Roman Urdu"},
        ],
        "categories": [
            {"value": "safe", "label": "Safe"},
            {"value": "target", "label": "Target"},
            {"value": "reach", "label": "Reach"},
            {"value": "unlikely", "label": "Unlikely"},
            {"value": "no-data", "label": "No data"},
            {"value": "not-eligible", "label": "Not eligible"},
        ],
        "defaults": {"matricTotal": DEFAULT_TOTAL, "interTotal": DEFAULT_TOTAL, "interPart1Total": DEFAULT_PART1_TOTAL},
    }


@app.post("/api/plan", response_model=PlanResult)
def plan(profile: StudentProfile):
    return _plan_for(profile)


@app.get("/api/sources", response_model=SourcesResponse)
def sources():
    data = load_data()
    return {"dataIsFixture": is_fixture(data), "universities": build_sources(data)}


@app.post("/api/explain", response_model=MentorAnswer)
def explain(body: ExplainRequest, request: Request):
    _rate_limit(request)
    # The plan is always rebuilt on the server from the profile, so a tampered
    # plan sent by a browser can never put fake numbers in front of the model.
    return run_explain(_plan_for(body.student()), body.language)


@app.post("/api/chat", response_model=MentorAnswer)
def chat(body: ChatRequest, request: Request):
    _rate_limit(request)
    return run_chat(_plan_for(body.student()), body.language, body.question)
