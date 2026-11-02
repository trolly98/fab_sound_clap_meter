MIN_SCORE = 1.0
MAX_SCORE = 10.0


def round_score(value: float) -> float:
    return round(min(MAX_SCORE, max(MIN_SCORE, value)), 1)
