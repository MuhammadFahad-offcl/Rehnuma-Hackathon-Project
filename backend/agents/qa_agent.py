import math

CATEGORY_ORDER = {
    "safe": 0,
    "target": 1,
    "reach": 2,
    "unlikely": 3,
    "no-data": 4,
    "not-eligible": 5,
}


class QAAgent:
    """Last gate before a plan leaves the engine: no NaN/Infinity, correct ordering."""

    name = "QA Agent"

    @staticmethod
    def _walk(value, path="plan"):
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(f"QA failed: non-finite number at {path}")
        elif isinstance(value, dict):
            for key, item in value.items():
                QAAgent._walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                QAAgent._walk(item, f"{path}[{index}]")

    @staticmethod
    def validate(plan):
        QAAgent._walk(plan)

        ranks = [CATEGORY_ORDER[o["category"]] for o in plan["options"]]
        if ranks != sorted(ranks):
            raise ValueError("QA failed: options are not in category order")

        dates = [item["date"] for item in plan["timeline"]]
        if dates != sorted(dates):
            raise ValueError("QA failed: timeline is not in date order")

        return plan
