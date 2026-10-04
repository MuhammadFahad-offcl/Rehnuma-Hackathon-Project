"""Loads the dataset once. Set REHNUMA_DATA_DIR to point at another folder of JSON files."""
import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ("universities", "programs", "scholarships")
PLACEHOLDER_MARKERS = ("FIXTURE", "example.com", "TODO", "sample")


def data_dir() -> Path:
    return Path(os.getenv("REHNUMA_DATA_DIR") or ROOT)


def _read(folder: Path, name: str):
    with open(folder / f"{name}.json", "r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=4)
def _load(folder: str):
    return {name: _read(Path(folder), name) for name in FILES}


def load_data(folder=None):
    """Return {"universities": [...], "programs": [...], "scholarships": [...]}."""
    return _load(str(folder or data_dir()))


def placeholder_markers(data) -> list:
    """Which placeholder markers are still present. Empty list == real data."""
    raw = json.dumps(data, ensure_ascii=False)
    return [marker for marker in PLACEHOLDER_MARKERS if marker in raw]


def is_fixture(data) -> bool:
    return bool(placeholder_markers(data))
