from .decibel import SILENCE_DB, db_to_power, power_to_db


class LevelSmoother:
    """Attacco rapido, rilascio lento, nel dominio delle potenze."""

    def __init__(self, attack: float = 0.6, release: float = 0.12):
        self._attack = attack
        self._release = release
        self._power = db_to_power(SILENCE_DB)

    def smooth(self, db: float) -> float:
        target = db_to_power(db)
        rate = self._attack if target > self._power else self._release
        self._power += rate * (target - self._power)
        return power_to_db(self._power)
