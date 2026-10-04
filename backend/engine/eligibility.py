def check_eligibility(profile: dict, program: dict, inter_pct: float) -> dict:
    if profile["group"] not in program["eligibleGroups"]:
        return {
            "eligible": False,
            "reason": "Your inter group is not accepted for this program."
        }

    minimum = program.get("minInterPercent")
    if minimum is not None and inter_pct < minimum["value"]:
        return {
            "eligible": False,
            "reason": f"This program needs at least {minimum['value']}% in inter."
        }

    return {"eligible": True, "reason": None}
