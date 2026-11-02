from abc import ABC, abstractmethod

from .score import MAX_SCORE, MIN_SCORE

_MIN_SPAN_DB = 0.1


class ScaleMapper(ABC):
    @abstractmethod
    def map(self, db: float) -> float:
        """Trasforma dB in un punteggio grezzo tra 1 e 10."""


class LinearScaleMapper(ScaleMapper):
    def __init__(self, floor_db: float, peak_db: float):
        self._floor_db = floor_db
        self._span = max(peak_db - floor_db, _MIN_SPAN_DB)

    def _progress(self, db: float) -> float:
        return min(1.0, max(0.0, (db - self._floor_db) / self._span))

    def map(self, db: float) -> float:
        return MIN_SCORE + (MAX_SCORE - MIN_SCORE) * self._progress(db)


class CurvedScaleMapper(LinearScaleMapper):
    """exponent > 1: scala piu' severa sui valori alti; < 1: piu' generosa."""

    def __init__(self, floor_db: float, peak_db: float, exponent: float):
        super().__init__(floor_db, peak_db)
        self._exponent = exponent

    def map(self, db: float) -> float:
        curved = self._progress(db) ** self._exponent
        return MIN_SCORE + (MAX_SCORE - MIN_SCORE) * curved
