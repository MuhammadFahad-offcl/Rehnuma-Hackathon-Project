"""Coordinator for the deterministic Rehnuma agents.

No network call and no LLM call happens anywhere in this module.
"""
from datetime import datetime, timedelta, timezone

from agents.aggregate_agent import AggregateAgent
from agents.budget_agent import BudgetAgent
from agents.category_agent import CategoryAgent
from agents.eligibility_agent import EligibilityAgent
from agents.qa_agent import CATEGORY_ORDER, QAAgent
from agents.scholarship_agent import ScholarshipAgent
from agents.timeline_agent import TimelineAgent

from .aggregate import to_percent
from .refs import same_city, to_ref

PKT = timezone(timedelta(hours=5))  # Pakistan Standard Time, no DST

SUMMARY_KEY = {
    "safe": "safe",
    "target": "target",
    "reach": "reach",
    "unlikely": "unlikely",
    "no-data": "noData",
    "not-eligible": "notEligible",
}

# Sourced program fields surfaced as "source chips" on every option card.
SOURCED_FIELDS = (
    "weights",
    "closingMerit",
    "minInterPercent",
    "admissionFee",
    "feePerSemester",
    "hostelPerYear",
)


def _round2(value):
    return None if value is None else round(value, 2)


class RehnumaEngine:
    """Runs each agent in sequence; every agent owns exactly one decision."""

    def __init__(self):
        self.eligibility = EligibilityAgent()
        self.aggregate = AggregateAgent()
        self.category = CategoryAgent()
        self.budget = BudgetAgent()
        self.scholarship = ScholarshipAgent()
        self.timeline = TimelineAgent()
        self.qa = QAAgent()

    def run(self, profile, data, today=None):
        now = datetime.now(PKT)
        today = today or now.date().isoformat()

        result = {
            "profile": profile,
            "generatedAt": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {key: 0 for key in SUMMARY_KEY.values()} | {"withinBudget": 0},
            "options": [],
            "timeline": [],
        }

        universities = {u["id"]: u for u in data["universities"]}
        matric_pct = to_percent(profile["matricObtained"], profile["matricTotal"])
        inter_pct = to_percent(profile["interObtained"], profile["interTotal"])
        expected = profile.get("expectedTestPercent")

        for program in data["programs"]:
            university = universities.get(program["universityId"])
            if university is None:
                continue

            if not profile["willingToRelocate"] and not same_city(
                university["city"], profile["homeCity"]
            ):
                continue

            eligibility = self.eligibility.run(profile, program, inter_pct)

            weights = program.get("weights")
            closing = program.get("closingMerit")
            weights_value = weights["value"] if weights else None
            closing_value = closing["value"] if closing else None

            numbers = self.aggregate.run(
                matric_pct, inter_pct, weights_value, closing_value, expected
            )
            verdict = self.category.run(
                eligibility["eligible"],
                closing_value,
                numbers["aggregate"],
                numbers["required"],
                program["testName"],
                program.get("closingMeritCycle"),
                eligibility["reason"],
            )

            result["options"].append({
                "programId": program["id"],
                "universityId": university["id"],
                "universityName": university["name"],
                "universityShortName": university.get("shortName"),
                "sector": university.get("sector"),
                "website": university.get("website"),
                "programName": program["name"],
                "city": university["city"],
                "testName": program["testName"],
                "eligible": eligibility["eligible"],
                "ineligibleReason": eligibility["reason"],
                "category": verdict["category"],
                "categoryReason": verdict["reason"],
                "matricPercent": _round2(matric_pct),
                "interPercent": _round2(inter_pct),
                "academicPart": _round2(numbers["academic"]),
                "aggregate": _round2(numbers["aggregate"]),
                "requiredTestPercent": _round2(numbers["required"]),
                "closingMerit": closing_value,
                "closingMeritCycle": program.get("closingMeritCycle"),
                "weights": weights_value,
                "semesters": program["semesters"],
                "cost": self.budget.run(profile, program, university["city"]),
                "scholarships": (
                    self.scholarship.run(
                        profile, university["id"], inter_pct, data["scholarships"]
                    )
                    if eligibility["eligible"]
                    else []
                ),
                "nextDeadline": self.timeline.next(program, today),
                "sources": {
                    field: to_ref(program[field])
                    for field in SOURCED_FIELDS
                    if program.get(field)
                },
            })

        result["options"].sort(
            key=lambda o: (
                CATEGORY_ORDER[o["category"]],
                -int(o["cost"]["withinBudget"]),
                o["cost"]["total"],
            )
        )

        for option in result["options"]:
            result["summary"][SUMMARY_KEY[option["category"]]] += 1
            if option["eligible"] and option["cost"]["withinBudget"]:
                result["summary"]["withinBudget"] += 1

        result["timeline"] = self.timeline.run(result["options"], data, today)

        return self.qa.validate(result)


def build_plan(profile, data, today=None):
    """Public API: profile + dataset -> finished plan.

    ``today`` (ISO date) is only for tests; production uses the current date
    in Pakistan.
    """
    return RehnumaEngine().run(profile, data, today=today)
