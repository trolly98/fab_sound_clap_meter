import math

SILENCE_DB = -100.0
_MIN_POWER = 10 ** (SILENCE_DB / 10)


def power_to_db(power: float) -> float:
    return SILENCE_DB if power <= _MIN_POWER else 10.0 * math.log10(power)


def db_to_power(db: float) -> float:
    return 10.0 ** (db / 10.0)
