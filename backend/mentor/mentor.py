"""runMentor(): prompt -> call -> guard -> retry -> fallback."""
import logging
import os

from . import client
from .facts import build_facts
from .fallback import fallback_answer
from .guard import check_answer, render
from .prompts import EXPLAIN_TASK, chat_task, system_prompt

log = logging.getLogger("rehnuma.mentor")

MAX_QUESTION_CHARS = 500
CHAT_FALLBACK_PREFIX = {
    "en": "I cannot answer that right now, but here is your plan in short. ",
    "roman-ur": "Main abhi is ka jawab nahi de sakta, lekin yeh raha aap ka plan mukhtasar me. ",
}


def normalise_language(value) -> str:
    text = str(value or "").strip().lower().replace("_", "-").replace(" ", "-")
    return "roman-ur" if text in {"roman-ur", "roman-urdu", "ur", "urdu"} else "en"


def _default_caller():
    """The function that talks to the model, or None when no key is configured."""
    if not client.providers():
        return None
    if os.getenv("MENTOR_ENGINE", "").strip().lower() == "crewai":
        try:
            import crewai  # noqa: F401
            from .crew import call_crew
            return call_crew
        except ImportError:
            log.warning("MENTOR_ENGINE=crewai but crewai is not installed; using the direct mentor")
    return client.call_model


def _finish(answer, facts):
    answer["rendered"] = render(answer["text"], facts)
    return answer


def run_mentor(plan, language, task, call_model=None):
    """Return MentorAnswer: {text, rendered, facts, usedFallback}.

    ``text`` contains [[F#]] tokens and never a raw digit; ``facts`` are only
    the ones used in ``text``; ``rendered`` is the plain-text version.
    """
    language = normalise_language(language)
    facts, ids = build_facts(plan)
    call_model = call_model or _default_caller()

    if call_model is not None:
        system = system_prompt(plan, facts, language)
        try:
            text = call_model(system, task)
            check = check_answer(text, facts)

            if not check["ok"]:
                retry = (
                    f"{task}\n\nYour last answer broke the rules: {' '.join(check['problems'])} "
                    "Write it again and follow every rule."
                )
                text = call_model(system, retry)
                check = check_answer(text, facts)

            if check["ok"]:
                return _finish({
                    "text": text,
                    "facts": [f for f in facts if f["id"] in check["usedIds"]],
                    "usedFallback": False,
                }, facts)
            log.warning("mentor answer rejected by the guard twice: %s", check["problems"])
        except Exception as error:
            log.warning("mentor failed, using fallback: %s", type(error).__name__)

    return _finish(fallback_answer(plan, facts, ids, language), facts)


def run_explain(plan, language, call_model=None):
    return run_mentor(plan, language, EXPLAIN_TASK, call_model)


def run_chat(plan, language, question, call_model=None):
    language = normalise_language(language)
    question = str(question or "")[:MAX_QUESTION_CHARS].strip()
    answer = run_mentor(plan, language, chat_task(question), call_model)

    # If the chat answer fell back, prefix one sentence so the student knows
    # the plan is still there even when the model could not reply.
    if answer["usedFallback"]:
        answer["text"] = CHAT_FALLBACK_PREFIX[language] + answer["text"]
        answer["rendered"] = CHAT_FALLBACK_PREFIX[language] + answer["rendered"]
    return answer
