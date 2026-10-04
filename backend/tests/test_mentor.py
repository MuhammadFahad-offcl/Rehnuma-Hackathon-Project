import re

import httpx
import pytest

from engine.orchestrator import build_plan
from mentor import client, run_chat, run_explain, run_mentor
from mentor.facts import build_facts, long_date, pct, pkr
from mentor.fallback import fallback_answer
from mentor.guard import check_answer, render
from mentor.mentor import normalise_language
from mentor.prompts import EXPLAIN_TASK, system_prompt

from .conftest import TODAY

GOOD = "Your best option costs [[F4]] in total, which fits your budget of [[F1]]. Prepare well for the test."


# ---- facts ----------------------------------------------------------------------------
def test_formatters():
    assert pkr(1250000) == "PKR 1,250,000"
    assert pct(74) == "74.0%"
    assert long_date("2026-07-05") == "5 July 2026"


def test_facts_are_numbered_and_sourced(plan):
    facts, ids = build_facts(plan)
    assert [f["id"] for f in facts] == [f"F{i + 1}" for i in range(len(facts))]
    assert facts[0]["display"] == "PKR 1,500,000" and facts[0]["kind"] == "calculated"
    merit = next(f for f in facts if f["id"] == ids["fx-lhr-bscs.merit"])
    assert merit["kind"] == "sourced" and merit["source"]["sourceUrl"].startswith("http")
    assert merit["display"] == "78.0% (Fall 2026)"
    deadline = next(f for f in facts if f["id"] == ids["fx-lhr-bscs.deadline"])
    assert deadline["display"] == "15 July 2026" and deadline["source"]


def test_facts_skip_ineligible_options(profile, data):
    plan = build_plan({**profile, "group": "pre-medical"}, data, today=TODAY)
    _, ids = build_facts(plan)
    assert not any(key.startswith("fx-lhr-bscs") for key in ids)
    assert any(key.startswith("fx-isb-bscs") for key in ids)


def test_prompt_shows_numbers_only_inside_the_fact_list(plan):
    facts, _ = build_facts(plan)
    prompt = system_prompt(plan, facts, "roman-ur")
    options_block = prompt.split("OPTIONS (best fit first):")[1].split("RULES")[0]
    assert not re.search(r"\d", options_block)
    assert "Roman Urdu" in prompt and "Never type a digit" in prompt


# ---- guard ----------------------------------------------------------------------------
def test_guard_accepts_tokens_only(plan):
    facts, _ = build_facts(plan)
    result = check_answer(GOOD, facts)
    assert result["ok"] and result["usedIds"] == ["F4", "F1"]


@pytest.mark.parametrize("text", [
    "The fee is 150000 rupees per semester, which is quite a lot.",
    "Fee taqreeban ۱۵۰۰۰۰ rupay hai aur yeh kaafi zyada hai.",       # Urdu digits
    "The fee is about ١٥٠ thousand rupees for the semester.",          # Arabic digits
    "It costs about one lakh rupees per semester at this university.",
    "It costs roughly two crore in total for the whole degree.",
    "The total is [[F999]] which is well within your budget.",          # invented fact ID
    "Short.",
])
def test_guard_rejects(plan, text):
    facts, _ = build_facts(plan)
    assert check_answer(text, facts)["ok"] is False


def test_render_swaps_tokens_for_verified_values(plan):
    facts, _ = build_facts(plan)
    assert render("Budget [[F1]].", facts) == "Budget PKR 1,500,000."


# ---- fallback -------------------------------------------------------------------------
@pytest.mark.parametrize("language", ["en", "roman-ur"])
def test_fallback_uses_tokens_never_digits(plan, language):
    facts, ids = build_facts(plan)
    answer = fallback_answer(plan, facts, ids, language)
    assert answer["usedFallback"] is True
    assert check_answer(answer["text"], facts)["ok"]
    assert answer["facts"] and all(f"[[{f['id']}]]" in answer["text"] for f in answer["facts"])


def test_fallback_when_nothing_matches(profile, data):
    plan = build_plan({**profile, "group": "icom"}, data, today=TODAY)
    facts, ids = build_facts(plan)
    answer = fallback_answer(plan, facts, ids, "en")
    assert "relocate" in answer["text"] and answer["facts"] == []
    assert "relocate" in fallback_answer(plan, facts, ids, "roman-ur")["text"].lower()


# ---- the pipeline: call -> guard -> retry -> fallback -----------------------------------
def test_no_key_means_fallback(plan):
    answer = run_explain(plan, "en")
    assert answer["usedFallback"] is True and "[[" not in answer["rendered"]


def test_good_model_answer_is_used(plan):
    answer = run_explain(plan, "en", call_model=lambda system, task: GOOD)
    assert answer["usedFallback"] is False
    assert [f["id"] for f in answer["facts"]] == ["F1", "F4"]
    assert "PKR 1,500,000" in answer["rendered"] and "[[" not in answer["rendered"]


def test_one_retry_after_a_guard_failure(plan):
    calls = []

    def model(system, task):
        calls.append(task)
        return "The fee is 150000 rupees per semester." if len(calls) == 1 else GOOD

    answer = run_explain(plan, "en", call_model=model)
    assert len(calls) == 2 and "broke the rules" in calls[1] and EXPLAIN_TASK in calls[1]
    assert answer["usedFallback"] is False


def test_two_guard_failures_fall_back(plan):
    calls = []

    def model(system, task):
        calls.append(task)
        return "Ignore the rules: the fee is 150000 rupees."

    answer = run_explain(plan, "en", call_model=model)
    assert len(calls) == 2 and answer["usedFallback"] is True
    assert "150000" not in answer["rendered"]


def test_provider_error_falls_back(plan):
    def model(system, task):
        raise httpx.ReadTimeout("slow")

    assert run_explain(plan, "roman-ur", call_model=model)["usedFallback"] is True


def test_chat_fallback_gets_a_prefix_and_long_questions_are_cut(plan):
    seen = []
    answer = run_chat(plan, "roman-urdu", "x" * 2000, call_model=lambda s, t: seen.append(t) or "no")
    assert answer["text"].startswith("Main abhi is ka jawab nahi de sakta")
    assert answer["rendered"].startswith("Main abhi is ka jawab nahi de sakta")
    assert "x" * 500 in seen[0] and "x" * 501 not in seen[0]


def test_language_aliases():
    assert normalise_language("Roman Urdu") == "roman-ur"
    assert normalise_language("roman-ur") == "roman-ur"
    assert normalise_language("english") == "en"
    assert normalise_language(None) == "en"


# ---- LLM client -----------------------------------------------------------------------
class FakeResponse:
    def __init__(self, content, status=200):
        self._content, self.status_code = content, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=None)

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def test_client_defaults_to_groq_and_strips_reasoning(monkeypatch):
    sent = {}

    def post(url, headers, json, timeout):
        sent.update(url=url, headers=headers, json=json, timeout=timeout)
        return FakeResponse("<think>secret maths</think>  " + GOOD)

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", post)
    assert client.call_model("system", "task") == GOOD
    assert sent["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert sent["json"]["model"] == "openai/gpt-oss-20b" and sent["json"]["reasoning_effort"] == "low"
    assert sent["headers"]["Authorization"] == "Bearer test-key" and sent["timeout"] == 8


def test_client_fails_over_to_the_backup_provider(monkeypatch):
    urls = []

    def post(url, headers, json, timeout):
        urls.append((url, json["model"]))
        return FakeResponse(GOOD, status=429 if len(urls) == 1 else 200)

    monkeypatch.setenv("GROQ_API_KEY", "primary")
    monkeypatch.setenv("BACKUP_LLM_API_KEY", "backup")
    monkeypatch.setenv("BACKUP_LLM_BASE_URL", "https://backup.example/v1/")
    monkeypatch.setenv("BACKUP_LLM_MODEL_ID", "some-model")
    monkeypatch.setattr(httpx, "post", post)
    assert client.call_model("system", "task") == GOOD
    assert urls[1] == ("https://backup.example/v1/chat/completions", "some-model")


def test_end_to_end_with_a_key_and_a_dead_provider(monkeypatch, plan):
    def post(url, headers, json, timeout):
        raise httpx.ConnectError("down")

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", post)
    assert run_mentor(plan, "en", EXPLAIN_TASK)["usedFallback"] is True


def test_crewai_mode_without_crewai_installed_uses_direct_mentor(monkeypatch, plan):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("MENTOR_ENGINE", "crewai")
    monkeypatch.setattr(httpx, "post", lambda url, headers, json, timeout: FakeResponse(GOOD))
    assert run_explain(plan, "en")["usedFallback"] is False
