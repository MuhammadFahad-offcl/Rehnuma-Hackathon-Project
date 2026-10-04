from engine.category import categorize, category_reason

class CategoryAgent:
    name = "Category Agent"

    def run(self, eligible, closing_merit, aggregate_value, required_test,
            test_name, cycle, ineligible_reason=None):
        category = categorize(
            eligible, closing_merit, aggregate_value, required_test
        )
        reason = category_reason(
            category, test_name, required_test, aggregate_value,
            closing_merit, cycle, ineligible_reason
        )
        return {"category": category, "reason": reason}
