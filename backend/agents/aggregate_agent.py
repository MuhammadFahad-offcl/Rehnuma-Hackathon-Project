from engine.aggregate import academic_part, aggregate, required_test_percent

class AggregateAgent:
    name = "Aggregate Agent"

    def run(self, matric_pct, inter_pct, weights, closing_merit, expected_test):
        if not weights:
            return {"academic": None, "required": None, "aggregate": None}

        academic = academic_part(matric_pct, inter_pct, weights)
        required = (
            required_test_percent(closing_merit, academic, weights["test"])
            if closing_merit is not None else None
        )

        aggregate_value = None
        if weights["test"] == 0:
            aggregate_value = academic
        elif expected_test is not None:
            aggregate_value = aggregate(
                academic, expected_test, weights["test"]
            )

        return {
            "academic": academic,
            "required": required,
            "aggregate": aggregate_value,
        }
