from .refs import same_city


def compute_cost(profile, program, university_city):
    """Whole-degree cost. Hostel is added only when the student must relocate.

    Scholarships are never subtracted: they are listed, not assumed.
    """
    tuition = program["feePerSemester"]["value"] * program["semesters"]
    admission_fee = program["admissionFee"]["value"]

    hostel_applies = not same_city(university_city, profile["homeCity"])
    hostel_unknown = hostel_applies and program.get("hostelPerYear") is None

    hostel = 0
    if hostel_applies and program.get("hostelPerYear") is not None:
        hostel = program["hostelPerYear"]["value"] * (program["semesters"] / 2)

    total = tuition + admission_fee + hostel
    gap = total - profile["budgetTotal"]

    return {
        "tuition": tuition,
        "admissionFee": admission_fee,
        "hostel": hostel,
        "total": total,
        "withinBudget": gap <= 0,
        "gap": gap,
        "hostelApplies": hostel_applies,
        "hostelUnknown": hostel_unknown,
    }
