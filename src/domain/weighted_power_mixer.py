from dataclasses import dataclass
from typing import Iterable

from .decibel import SILENCE_DB, db_to_power, power_to_db


@dataclass(frozen=True)
class WeightedLevel:
    db: float
    weight: float


class WeightedPowerMixer:
    """Media pesata sulle potenze lineari, riconvertita in dB:

        P = sum(w_i * 10^(dB_i/10)) / sum(w_i)      dB = 10 * log10(P)
    """

    def mix(self, levels: Iterable[WeightedLevel]) -> float:
        active = [level for level in levels if level.weight > 0]
        total_weight = sum(level.weight for level in active)
        if total_weight == 0:
            return SILENCE_DB
        power = sum(l.weight * db_to_power(l.db) for l in active) / total_weight
        return power_to_db(power)
