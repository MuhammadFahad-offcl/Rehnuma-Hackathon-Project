"""Makes the backend packages importable and bridges Streamlit secrets to env vars."""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

SECRET_KEYS = (
    "GROQ_API_KEY", "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL_ID",
    "BACKUP_LLM_API_KEY", "BACKUP_LLM_BASE_URL", "BACKUP_LLM_MODEL_ID",
)


def load_secrets(st):
    """Streamlit Cloud keeps keys in st.secrets; the mentor reads environment variables."""
    try:
        for key in SECRET_KEYS:
            if key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass  # no secrets file locally - the mentor simply uses its fallback
