MIN_SCORE = 1.0
MAX_SCORE = 10.0


def round_score(value: float, decimals: int = 1) -> float:
    return round(min(MAX_SCORE, max(MIN_SCORE, value)), decimals)
