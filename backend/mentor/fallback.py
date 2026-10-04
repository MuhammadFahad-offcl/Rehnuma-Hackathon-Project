"""Template answers built by code from the same facts. Used when the model fails."""
from .guard import TOKEN


def fallback_answer(plan, facts, ids, language):
    eligible = [o for o in plan["options"] if o["eligible"]]
    best = next((o for o in eligible if o["cost"]["withinBudget"]), None) or (eligible[0] if eligible else None)

    if best is None:
        text = (
            'None of the universities in our verified list match this profile yet. Try turning on '
            '"willing to relocate", or read the eligibility note on each card.'
            if language == "en"
            else 'Hamari verified list me abhi koi university is profile se match nahi hui. '
                 '"Willing to relocate" on kar ke dekhein, ya har card par eligibility note parhein.'
        )
        return {"text": text, "facts": [], "usedFallback": True}

    def t(key):
        fact_id = ids.get(f"{best['programId']}.{key}")
        return f"[[{fact_id}]]" if fact_id else ""

    over = best["cost"]["gap"] > 0
    name, test = best["universityName"], best["testName"]

    if language == "en":
        parts = [
            f"Your strongest option right now is {name}.",
            t("required") and f"You need {t('required')} in {test} to reach the last closing merit.",
            f"The whole degree costs about {t('total')}, which is {t('gap')} {'over' if over else 'under'} your budget.",
            t("deadline") and f"The next date to remember is {t('deadline')}.",
            "Open each card to see the official source of every number.",
        ]
    else:
        parts = [
            f"Is waqt aap ka sab se mazboot option {name} hai.",
            t("required") and f"Pichlay closing merit tak pohanchne ke liye {test} me {t('required')} chahiye.",
            f"Poori degree ka kharcha taqreeban {t('total')} hai, jo aap ke budget se {t('gap')} {'zyada' if over else 'kam'} hai.",
            t("deadline") and f"Agli ahem tareekh {t('deadline')} hai.",
            "Har number ka official source dekhne ke liye card kholein.",
        ]

    text = " ".join(part for part in parts if part)
    used = set(TOKEN.findall(text))
    return {
        "text": text,
        "facts": [f for f in facts if f["id"] in used],
        "usedFallback": True,
    }
