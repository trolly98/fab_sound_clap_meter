import numpy as np

from domain.decibel import SILENCE_DB, power_to_db


class PowerAccumulator:
    """Accumula l'energia dei campioni e restituisce i dB (RMS) dall'ultima lettura."""

    def __init__(self):
        self._energy = 0.0
        self._count = 0
        self._last_db = SILENCE_DB

    def add(self, samples: np.ndarray) -> None:
        self._energy += float(np.dot(samples, samples))
        self._count += samples.size

    def consume_db(self) -> float:
        if self._count:
            self._last_db = power_to_db(self._energy / self._count)
            self._energy, self._count = 0.0, 0
        return self._last_db
