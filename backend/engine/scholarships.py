from .refs import to_ref


def match_scholarships(profile, university_id, inter_pct, scholarships):
    """Scholarships this student may apply for at this university.

    A need-based scholarship is hidden only when the student gave an income
    that is above its cap. If income was not given, it is still listed so the
    student can check it themselves.
    """
    matches = []

    for s in scholarships:
        university_match = (
            s["universityIds"] == "all"
            or university_id in s["universityIds"]
        )
        if not university_match:
            continue

        minimum = s.get("minInterPercent")
        if minimum is not None and inter_pct < minimum:
            continue

        income_limit = s.get("maxFamilyIncomeMonthly")
        if (
            income_limit is not None
            and profile.get("familyIncomeMonthly") is not None
            and profile["familyIncomeMonthly"] > income_limit
        ):
            continue

        matches.append({
            "id": s["id"],
            "name": s["name"],
            "provider": s.get("provider"),
            "type": s.get("type"),
            "summary": s["summary"]["value"],
            "applyUrl": s["applyUrl"],
            "source": to_ref(s["summary"]),
        })

    return matches
