"""Tests run against a frozen fixture dataset (tests/fixtures), never against data/.

That way the suite keeps passing when the real, verified dataset replaces the
demo data in data/.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(BACKEND))
os.environ["REHNUMA_DATA_DIR"] = str(FIXTURES)
os.environ["MENTOR_RATE_LIMIT_PER_MIN"] = "0"
for key in ("GROQ_API_KEY", "LLM_API_KEY", "BACKUP_LLM_API_KEY", "MENTOR_ENGINE", "GROQ_MODEL", "LLM_MODEL_ID"):
    os.environ.pop(key, None)

import pytest  # noqa: E402

from data.loader import load_data  # noqa: E402

TODAY = "2026-06-01"


@pytest.fixture
def data():
    return load_data(FIXTURES)


@pytest.fixture
def profile():
    return {
        "matricObtained": 990,
        "matricTotal": 1100,
        "interObtained": 880,
        "interTotal": 1100,
        "interStatus": "complete",
        "group": "ics",
        "homeCity": "Lahore",
        "willingToRelocate": True,
        "budgetTotal": 1500000,
        "familyIncomeMonthly": 60000,
        "expectedTestPercent": None,
    }


@pytest.fixture
def plan(profile, data):
    from engine.orchestrator import build_plan

    return build_plan(profile, data, today=TODAY)
