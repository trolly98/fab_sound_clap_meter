from .score import MIN_SCORE


class ScoreExtremes:
    """Voto piu' alto e piu' basso raggiunti dall'ultimo azzeramento."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._min: float | None = None
        self._max: float | None = None

    def update(self, score: float) -> None:
        self._min = score if self._min is None else min(self._min, score)
        self._max = score if self._max is None else max(self._max, score)

    @property
    def minimum(self) -> float:
        return MIN_SCORE if self._min is None else self._min

    @property
    def maximum(self) -> float:
        return MIN_SCORE if self._max is None else self._max
