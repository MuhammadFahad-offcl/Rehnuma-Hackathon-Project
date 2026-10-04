def categorize(eligible, closing_merit, aggregate_value, required_test):
    if not eligible:
        return "not-eligible"
    if closing_merit is None:
        return "no-data"

    if aggregate_value is not None:
        margin = aggregate_value - closing_merit
        if margin >= 3:
            return "safe"
        if margin >= -2:
            return "target"
        if margin >= -7:
            return "reach"
        return "unlikely"

    if required_test is None:
        return "no-data"
    if required_test <= 60:
        return "safe"
    if required_test <= 75:
        return "target"
    if required_test <= 90:
        return "reach"
    return "unlikely"


def category_reason(category, test_name, required_test, aggregate_value,
                    closing_merit, cycle, ineligible_reason=None):
    f = lambda n: f"{n:.1f}"

    if category == "not-eligible":
        return ineligible_reason or "You do not meet the admission criteria."

    if category == "no-data":
        return "The aggregate formula or closing merit is not officially published."

    merit = f"{closing_merit}%"
    if cycle:
        merit += f" ({cycle})"

    if aggregate_value is not None:
        margin = aggregate_value - closing_merit
        side = "above" if margin >= 0 else "below"
        return (
            f"Your aggregate {f(aggregate_value)}% is "
            f"{f(abs(margin))} points {side} the last closing merit of {merit}."
        )

    if required_test <= 0:
        return f"Your matric and inter marks alone are above the last closing merit of {merit}."
    if required_test > 100:
        return f"Even 100% in {test_name} would not reach the last closing merit of {merit}."
    return f"You need {f(required_test)}% in {test_name} to reach the last closing merit of {merit}."
