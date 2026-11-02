from collections import deque

from domain.score import MAX_SCORE, MIN_SCORE

from .algorithm_parameter import AlgorithmParameter
from .applause_algorithm import ApplauseAlgorithm
from .percentile import percentile

_SPAN = MAX_SCORE - MIN_SCORE


class WeightedSlidingWindowAlgorithm(ApplauseAlgorithm):
    """Finestra mobile sugli ultimi N secondi: score = (wM*M + wP*P + wC*C) / (wM+wP+wC)

    M = media dei punteggi, P = 90o percentile, C = 1 + 9 * (quota di tempo sopra la soglia di costanza).
    Prima della stabilizzazione e prima che si superi la soglia di attivazione il risultato resta 1.
    """

    name = "Weighted Sliding Window Algorithm"
    definitions = (
        AlgorithmParameter("window_s", "Durata finestra mobile", "s", 1, 10, 0.5, 4.0),
        AlgorithmParameter("update_interval_s", "Frequenza di aggiornamento", "s", 0.1, 2.0, 0.1, 0.5, advanced=True),
        AlgorithmParameter("constancy_threshold", "Soglia di costanza", "/10", 1, 10, 0.5, 6.0, advanced=True),
        AlgorithmParameter("activation_threshold", "Soglia di attivazione", "/10", 1, 10, 0.5, 3.0, advanced=True),
        AlgorithmParameter("stabilization_s", "Tempo di stabilizzazione iniziale", "s", 0, 3, 0.1, 0.5, advanced=True),
        AlgorithmParameter("weight_mean", "Peso intensita' media", "%", 0, 100, 5, 50, advanced=True),
        AlgorithmParameter("weight_peak", "Peso picco (90o percentile)", "%", 0, 100, 5, 30, advanced=True),
        AlgorithmParameter("weight_constancy", "Peso costanza", "%", 0, 100, 5, 20, advanced=True),
    )

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self._window: deque[tuple[float, float]] = deque()
        self._activated = False
        self._last_update: float | None = None
        self._output = MIN_SCORE

    def feed(self, elapsed_s: float, score: float) -> float:
        if elapsed_s < self.value("stabilization_s") or not self._is_active(score):
            return self._output
        self._window.append((elapsed_s, score))
        self._drop_samples_older_than(elapsed_s - self.value("window_s"))
        if self._update_is_due(elapsed_s):
            self._output = self._compute()
            self._last_update = elapsed_s
        return self._output

    def _is_active(self, score: float) -> bool:
        self._activated = self._activated or score >= self.value("activation_threshold")
        return self._activated

    def _drop_samples_older_than(self, limit_s: float) -> None:
        while self._window and self._window[0][0] < limit_s:
            self._window.popleft()

    def _update_is_due(self, elapsed_s: float) -> bool:
        return self._last_update is None or elapsed_s - self._last_update >= self.value("update_interval_s")

    def _compute(self) -> float:
        scores = [s for _, s in self._window]
        mean = sum(scores) / len(scores)
        peak = percentile(scores, 0.9)
        above = sum(1 for s in scores if s >= self.value("constancy_threshold"))
        constancy = MIN_SCORE + _SPAN * above / len(scores)
        weights = (self.value("weight_mean"), self.value("weight_peak"), self.value("weight_constancy"))
        total = sum(weights)
        if total == 0:
            return mean
        return (weights[0] * mean + weights[1] * peak + weights[2] * constancy) / total
