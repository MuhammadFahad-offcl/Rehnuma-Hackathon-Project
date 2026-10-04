"""checkAnswer(text, facts): the digit guard.

Known limit: it blocks digits in any script and the common number words
(lakh, crore, thousand...), not every possible spelled-out number. The prompt
rule and the rehearsed demo questions cover the rest.
"""
import re

TOKEN = re.compile(r"\[\[(F\d+)\]\]")
ANY_DIGIT = re.compile(r"\d")  # \d is Unicode-aware: Latin, Arabic-Indic and Urdu digits
NUMBER_WORD = re.compile(r"\b(lakh|lakhs|lac|lacs|crore|crores|hazar|hazaar|thousand|million)\b", re.IGNORECASE)
MIN_LENGTH = 20


def check_answer(text: str, facts):
    ids = TOKEN.findall(text)
    known = {f["id"] for f in facts}
    without_tokens = TOKEN.sub("", text)
    problems = []

    if any(i not in known for i in ids):
        problems.append("You used a fact ID that is not in the FACTS list.")
    if ANY_DIGIT.search(without_tokens):
        problems.append("You typed a digit. Use fact IDs only.")
    if NUMBER_WORD.search(without_tokens):
        problems.append("You wrote an amount in words. Use fact IDs only.")
    if len(text.strip()) < MIN_LENGTH:
        problems.append("The answer was empty.")

    return {
        "ok": not problems,
        "problems": problems,
        "usedIds": list(dict.fromkeys(ids)),
    }


def render(text: str, facts) -> str:
    """Plain-text version: every [[F#]] token replaced by its verified display value."""
    display = {f["id"]: f["display"] for f in facts}
    return TOKEN.sub(lambda m: display.get(m.group(1), ""), text)
