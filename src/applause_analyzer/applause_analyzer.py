from collections import deque

from domain.score import MIN_SCORE, round_score

from .applause_algorithm import ApplauseAlgorithm


class ApplauseAnalyzer:
    """Avvia/ferma l'analisi. Punteggio live continuo; punteggio finale = media degli ultimi secondi."""

    FINAL_AVERAGE_S = 2.5

    def __init__(self, algorithm: ApplauseAlgorithm):
        self._algorithm = algorithm
        self._reset_state()

    def _reset_state(self) -> None:
        self._running = False
        self._started_at = 0.0
        self._live = MIN_SCORE
        self._final = MIN_SCORE
        self._history: deque[tuple[float, float]] = deque()

    @property
    def algorithm(self) -> ApplauseAlgorithm:
        return self._algorithm

    def set_algorithm(self, algorithm: ApplauseAlgorithm) -> None:
        self._algorithm = algorithm
        self._reset_state()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def live_score(self) -> float:
        return self._live

    @property
    def final_score(self) -> float:
        return self._final

    def start(self, now_s: float) -> None:
        self._reset_state()
        self._algorithm.reset()
        self._running = True
        self._started_at = now_s

    def feed(self, now_s: float, score: float) -> None:
        if not self._running:
            return
        elapsed = now_s - self._started_at
        self._live = round_score(self._algorithm.feed(elapsed, score))
        self._history.append((elapsed, self._live))
        while self._history[0][0] < elapsed - self.FINAL_AVERAGE_S:
            self._history.popleft()

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        values = [live for _, live in self._history]
        self._final = round_score(sum(values) / len(values)) if values else self._live
