from .decibel import db_to_power, power_to_db


class CalibrationCapture:
    """Raccoglie livelli durante una cattura e ne ricava fondo o picco."""

    def __init__(self):
        self._levels: list[float] = []

    def add(self, db: float) -> None:
        self._levels.append(db)

    def floor_db(self, margin_db: float) -> float:
        mean_power = sum(db_to_power(d) for d in self._levels) / len(self._levels)
        return power_to_db(mean_power) + margin_db

    def peak_db(self, percentile: float = 0.9) -> float:
        ordered = sorted(self._levels)
        return ordered[min(len(ordered) - 1, int(len(ordered) * percentile))]

    @property
    def is_empty(self) -> bool:
        return not self._levels
