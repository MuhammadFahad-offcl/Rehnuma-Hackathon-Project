"""One LLM call with a hard timeout, against any OpenAI-compatible endpoint.

Default provider is Groq. An optional backup provider is tried when the
primary fails (rate limit, outage), so the demo does not depend on one key.

Environment:
    GROQ_API_KEY / LLM_API_KEY     key for the primary provider
    LLM_BASE_URL                   default https://api.groq.com/openai/v1
    LLM_MODEL_ID  (or GROQ_MODEL)  default openai/gpt-oss-20b
    LLM_TIMEOUT_SECONDS            default 8
    LLM_REASONING_EFFORT           optional; defaults to "low" for gpt-oss models
    BACKUP_LLM_API_KEY, BACKUP_LLM_BASE_URL, BACKUP_LLM_MODEL_ID   optional second provider
"""
import logging
import os
import re
from dataclasses import dataclass
from typing import Optional

import httpx

log = logging.getLogger("rehnuma.mentor")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# llama-3.1-8b-instant left Groq's free/developer tiers on 2026-08-16;
# openai/gpt-oss-20b is Groq's listed replacement.
DEFAULT_MODEL = "openai/gpt-oss-20b"
THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_key: str
    model: str
    reasoning_effort: Optional[str] = None


def _env(*names) -> Optional[str]:
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value:
            return value
    return None


def timeout_seconds() -> float:
    try:
        return float(os.getenv("LLM_TIMEOUT_SECONDS", "8"))
    except ValueError:
        return 8.0


def providers() -> list:
    """Configured providers in the order they are tried. Empty list == no key set."""
    found = []

    key = _env("LLM_API_KEY", "GROQ_API_KEY")
    if key:
        model = _env("LLM_MODEL_ID", "GROQ_MODEL") or DEFAULT_MODEL
        effort = _env("LLM_REASONING_EFFORT") or ("low" if "gpt-oss" in model else None)
        found.append(Provider("primary", (_env("LLM_BASE_URL") or GROQ_BASE_URL).rstrip("/"), key, model, effort))

    backup_key = _env("BACKUP_LLM_API_KEY")
    backup_model = _env("BACKUP_LLM_MODEL_ID")
    if backup_key and backup_model:
        found.append(Provider(
            "backup",
            (_env("BACKUP_LLM_BASE_URL") or GROQ_BASE_URL).rstrip("/"),
            backup_key,
            backup_model,
            _env("BACKUP_LLM_REASONING_EFFORT") or ("low" if "gpt-oss" in backup_model else None),
        ))

    return found


def _call(provider: Provider, system: str, prompt: str) -> str:
    payload = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1500,
    }
    if provider.reasoning_effort:
        payload["reasoning_effort"] = provider.reasoning_effort

    response = httpx.post(
        f"{provider.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {provider.api_key}"},
        json=payload,
        timeout=timeout_seconds(),
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"].get("content") or ""
    return THINK_BLOCK.sub("", content).strip()


def call_model(system: str, prompt: str) -> str:
    """Try each configured provider in order; raise if all of them fail."""
    configured = providers()
    if not configured:
        raise RuntimeError("no LLM provider configured")

    last_error = None
    for provider in configured:
        try:
            return _call(provider, system, prompt)
        except Exception as error:  # timeout, 4xx/5xx, malformed body
            # Never log the key or the prompt - only which provider failed and why.
            log.warning("LLM provider '%s' (%s) failed: %s", provider.name, provider.model, type(error).__name__)
            last_error = error
    raise last_error
