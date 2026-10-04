"""Runtime settings, all from environment variables (see .env.example)."""
import os

DEFAULT_ORIGINS = ("http://localhost:5173",)
# Always allowed: any *.vercel.app deployment (the frontend's production and preview URLs),
# Lovable previews, and localhost. Add a custom domain with ALLOWED_ORIGINS.
DEFAULT_ORIGIN_REGEX = (
    r"https://([a-z0-9-]+\.)*(vercel\.app|lovable\.app|lovableproject\.com)"
    r"|http://(localhost|127\.0\.0\.1)(:\d+)?"
)


def allowed_origins() -> list:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    extra = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return list(dict.fromkeys([*DEFAULT_ORIGINS, *extra]))


def allow_all_origins() -> bool:
    return "*" in allowed_origins()


def origin_regex() -> str:
    return os.getenv("ALLOWED_ORIGIN_REGEX") or DEFAULT_ORIGIN_REGEX


def mentor_rate_limit() -> int:
    """Mentor calls allowed per client IP per minute (0 disables the limit)."""
    try:
        return int(os.getenv("MENTOR_RATE_LIMIT_PER_MIN", "20"))
    except ValueError:
        return 20
