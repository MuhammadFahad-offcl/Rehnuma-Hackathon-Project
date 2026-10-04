import math

from engine.aggregate import academic_part, aggregate, required_test_percent, to_percent
from engine.category import categorize, category_reason
from engine.cost import compute_cost
from engine.eligibility import check_eligibility
from engine.orchestrator import build_plan
from engine.scholarships import match_scholarships

from .conftest import TODAY

W = {"matric": 10, "inter": 40, "test": 50}


# ---- formulas -------------------------------------------------------------------------
def test_percent():
    assert to_percent(550, 1100) == 50
    assert round(to_percent(990, 1100), 2) == 90.0


def test_academic_part():
    assert academic_part(90, 80, W) == 41


def test_aggregate():
    assert aggregate(41, 80, 50) == 81


def test_required_test():
    assert required_test_percent(78, 41, 50) == 74


def test_required_test_may_be_below_zero_or_above_hundred():
    assert required_test_percent(30, 41, 50) < 0
    assert required_test_percent(99, 41, 50) > 100


def test_required_test_when_there_is_no_test():
    assert required_test_percent(78, 41, 0) is None


# ---- categories -----------------------------------------------------------------------
def test_category_boundaries_without_expected_test():
    assert categorize(True, 78, None, 60) == "safe"
    assert categorize(True, 78, None, 60.01) == "target"
    assert categorize(True, 78, None, 75) == "target"
    assert categorize(True, 78, None, 75.01) == "reach"
    assert categorize(True, 78, None, 90) == "reach"
    assert categorize(True, 78, None, 90.01) == "unlikely"


def test_category_boundaries_with_expected_test():
    assert categorize(True, 78, 81, None) == "safe"
    assert categorize(True, 78, 80.99, None) == "target"
    assert categorize(True, 78, 76, None) == "target"
    assert categorize(True, 78, 75.99, None) == "reach"
    assert categorize(True, 78, 71, None) == "reach"
    assert categorize(True, 78, 70.99, None) == "unlikely"


def test_category_missing_data_and_ineligible():
    assert categorize(True, None, None, None) == "no-data"
    assert categorize(True, 78, None, None) == "no-data"
    assert categorize(False, 78, 90, 10) == "not-eligible"


def test_category_reason_never_promises_admission():
    text = category_reason("safe", "Fixture Test", 55.0, None, 78, "Fall 2026")
    assert "55.0%" in text and "Fall 2026" in text
    assert "guarantee" not in text.lower() and "will get" not in text.lower()
    assert "100%" in category_reason("unlikely", "Fixture Test", 120.0, None, 78, None)
    assert "alone" in category_reason("safe", "Fixture Test", -5.0, None, 78, None)


# ---- eligibility ----------------------------------------------------------------------
def test_eligibility_group_and_minimum(profile, data):
    program = data["programs"][0]
    assert check_eligibility(profile, program, 80)["eligible"] is True
    assert check_eligibility({**profile, "group": "icom"}, program, 80)["eligible"] is False
    low = check_eligibility(profile, program, 59.99)
    assert low["eligible"] is False and "60" in low["reason"]


# ---- cost -----------------------------------------------------------------------------
def test_cost_same_city(profile, data):
    result = compute_cost(profile, data["programs"][0], "Lahore")
    assert result["total"] == 1250000
    assert result["gap"] == -250000
    assert result["withinBudget"] is True
    assert result["hostelApplies"] is False and result["hostel"] == 0


def test_cost_other_city_adds_hostel(profile, data):
    result = compute_cost(profile, data["programs"][0], "Islamabad")
    assert result["hostel"] == 480000
    assert result["total"] == 1730000
    assert result["gap"] == 230000
    assert result["withinBudget"] is False


def test_cost_hostel_unknown_is_flagged_not_guessed(profile, data):
    multan = next(p for p in data["programs"] if p["id"] == "fx-mul-bscs")
    result = compute_cost(profile, multan, "Multan")
    assert result["hostelApplies"] is True
    assert result["hostelUnknown"] is True
    assert result["hostel"] == 0


def test_cost_exactly_on_budget_is_within_budget(profile, data):
    result = compute_cost({**profile, "budgetTotal": 1250000}, data["programs"][0], "Lahore")
    assert result["gap"] == 0 and result["withinBudget"] is True


# ---- scholarships ---------------------------------------------------------------------
def test_scholarship_income_rules(profile, data):
    s = data["scholarships"]
    assert len(match_scholarships(profile, "fx-lhr", 80, s)) == 1
    assert match_scholarships({**profile, "familyIncomeMonthly": 80001}, "fx-lhr", 80, s) == []
    # unknown income: still listed so the student can check it
    assert len(match_scholarships({**profile, "familyIncomeMonthly": None}, "fx-lhr", 80, s)) == 1
    # below the minimum inter percentage
    assert match_scholarships(profile, "fx-lhr", 59, s) == []


def test_scholarships_are_never_subtracted_from_cost(plan):
    for option in plan["options"]:
        cost = option["cost"]
        assert cost["total"] == cost["tuition"] + cost["admissionFee"] + cost["hostel"]


# ---- whole plan -----------------------------------------------------------------------
def test_plan_shape_matches_the_contract(plan):
    assert set(plan) == {"profile", "generatedAt", "summary", "options", "timeline"}
    assert set(plan["summary"]) == {"safe", "target", "reach", "unlikely", "noData", "notEligible", "withinBudget"}
    option = plan["options"][0]
    for key in ("programId", "universityId", "universityName", "programName", "city", "testName", "eligible",
                "category", "categoryReason", "matricPercent", "interPercent", "academicPart", "aggregate",
                "requiredTestPercent", "closingMerit", "closingMeritCycle", "cost", "scholarships",
                "nextDeadline", "sources"):
        assert key in option, key


def test_plan_summary_counts(plan):
    s = plan["summary"]
    assert s["safe"] + s["target"] + s["reach"] + s["unlikely"] + s["noData"] + s["notEligible"] == len(plan["options"])
    assert s["withinBudget"] == sum(o["eligible"] and o["cost"]["withinBudget"] for o in plan["options"])


def test_no_relocation_keeps_only_home_city(profile, data):
    plan = build_plan({**profile, "willingToRelocate": False}, data, today=TODAY)
    assert plan["options"] and all(o["city"] == "Lahore" for o in plan["options"])


def test_home_city_match_ignores_case_and_spaces(profile, data):
    plan = build_plan({**profile, "homeCity": "  lahore ", "willingToRelocate": False}, data, today=TODAY)
    assert len(plan["options"]) == 1


def test_no_data_option_still_has_cost(plan):
    multan = next(o for o in plan["options"] if o["city"] == "Multan")
    assert multan["category"] == "no-data"
    assert multan["requiredTestPercent"] is None and multan["aggregate"] is None
    assert multan["cost"]["total"] > 0


def test_ineligible_group(profile, data):
    plan = build_plan({**profile, "group": "pre-medical"}, data, today=TODAY)
    lahore = next(o for o in plan["options"] if o["city"] == "Lahore")
    assert lahore["category"] == "not-eligible"
    assert lahore["scholarships"] == []
    assert all(t["programId"] != lahore["programId"] for t in plan["timeline"])
    everything = build_plan({**profile, "group": "icom"}, data, today=TODAY)
    assert all(o["category"] == "not-eligible" for o in everything["options"])


def test_zero_expected_test_is_a_real_score(profile, data):
    plan = build_plan({**profile, "expectedTestPercent": 0}, data, today=TODAY)
    lahore = next(o for o in plan["options"] if o["city"] == "Lahore")
    assert lahore["aggregate"] == lahore["academicPart"]


def test_expected_test_changes_category(profile, data):
    high = build_plan({**profile, "expectedTestPercent": 95}, data, today=TODAY)
    low = build_plan({**profile, "expectedTestPercent": 20}, data, today=TODAY)
    category = lambda p: next(o for o in p["options"] if o["city"] == "Lahore")["category"]
    assert category(high) == "safe" and category(low) == "unlikely"


def test_program_without_an_entry_test(profile, data):
    import copy

    changed = copy.deepcopy(data)
    changed["programs"][0]["weights"]["value"] = {"matric": 30, "inter": 70, "test": 0}
    plan = build_plan(profile, changed, today=TODAY)
    lahore = next(o for o in plan["options"] if o["city"] == "Lahore")
    assert lahore["requiredTestPercent"] is None
    assert lahore["aggregate"] == lahore["academicPart"] == 83.0
    assert lahore["category"] == "safe"


def test_options_are_sorted_best_first(plan):
    order = ["safe", "target", "reach", "unlikely", "no-data", "not-eligible"]
    ranks = [order.index(o["category"]) for o in plan["options"]]
    assert ranks == sorted(ranks)


def test_sources_travel_with_every_number(plan):
    lahore = next(o for o in plan["options"] if o["city"] == "Lahore")
    for field in ("weights", "closingMerit", "minInterPercent", "admissionFee", "feePerSemester", "hostelPerYear"):
        ref = lahore["sources"][field]
        assert ref["sourceUrl"].startswith("http") and ref["verifiedOn"] and ref["confidence"]
    multan = next(o for o in plan["options"] if o["city"] == "Multan")
    assert "closingMerit" not in multan["sources"]


def test_timeline_sorted_with_past_flag(plan, profile, data):
    dates = [item["date"] for item in plan["timeline"]]
    assert dates == sorted(dates) and dates
    assert all(item["isPast"] is False for item in plan["timeline"])
    later = build_plan(profile, data, today="2026-07-20")
    assert [item["isPast"] for item in later["timeline"]] == [True, False]
    lahore = next(o for o in later["options"] if o["city"] == "Lahore")
    assert lahore["nextDeadline"] is None


def test_no_nan_or_infinity(plan):
    def walk(value):
        if isinstance(value, float):
            assert math.isfinite(value)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(plan)


def test_qa_agent_rejects_bad_plans(plan):
    import pytest
    from agents.qa_agent import QAAgent

    broken = {**plan, "options": list(reversed(plan["options"]))}
    with pytest.raises(ValueError):
        QAAgent.validate(broken)
    with pytest.raises(ValueError):
        QAAgent.validate({**plan, "summary": {"safe": float("nan")}})


# ---- the three demo personas from the PRD (structure checks: real numbers depend on the dataset) ----
PERSONA_A = dict(matricObtained=1020, matricTotal=1100, interObtained=940, interTotal=1100, interStatus="complete",
                 group="ics", homeCity="Lahore", willingToRelocate=False, budgetTotal=1500000)
PERSONA_B = dict(matricObtained=890, matricTotal=1100, interObtained=780, interTotal=1100, interStatus="complete",
                 group="pre-engineering", homeCity="Multan", willingToRelocate=True, budgetTotal=800000,
                 familyIncomeMonthly=60000)
PERSONA_C = dict(matricObtained=950, matricTotal=1100, interObtained=900, interTotal=1100, interStatus="complete",
                 group="pre-medical", homeCity="Lahore", willingToRelocate=True, budgetTotal=2500000)


def test_persona_a_stays_in_lahore(data):
    plan = build_plan(PERSONA_A, data, today=TODAY)
    assert plan["options"] and all(o["city"] == "Lahore" for o in plan["options"])
    assert all(o["cost"]["hostelApplies"] is False for o in plan["options"])


def test_persona_b_pays_hostel_away_from_home_and_sees_need_scholarships(data):
    plan = build_plan(PERSONA_B, data, today=TODAY)
    away = [o for o in plan["options"] if o["city"] != "Multan"]
    assert away and all(o["cost"]["hostelApplies"] for o in away)
    assert any(o["cost"]["gap"] > 0 for o in plan["options"])                      # over-budget gaps show
    assert any(s["type"] == "need" for o in plan["options"] for s in o["scholarships"])


def test_persona_c_is_not_eligible_where_pre_medical_is_not_accepted(data):
    plan = build_plan(PERSONA_C, data, today=TODAY)
    accepts = {p["id"]: "pre-medical" in p["eligibleGroups"] for p in data["programs"]}
    for option in plan["options"]:
        assert (option["category"] == "not-eligible") == (not accepts[option["programId"]])
        if not option["eligible"]:
            assert option["ineligibleReason"]
