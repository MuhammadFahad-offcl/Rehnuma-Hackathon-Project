def to_percent(obtained: float, total: float) -> float:
    return (obtained / total) * 100


def academic_part(matric_pct: float, inter_pct: float, weights: dict) -> float:
    return (matric_pct * weights["matric"] + inter_pct * weights["inter"]) / 100


def aggregate(academic: float, test_pct: float, test_weight: float) -> float:
    return academic + (test_pct * test_weight) / 100


def required_test_percent(closing_merit: float, academic: float, test_weight: float):
    if test_weight == 0:
        return None
    return ((closing_merit - academic) * 100) / test_weight
