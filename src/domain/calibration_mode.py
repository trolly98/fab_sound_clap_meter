from enum import Enum

from .scale_mappers import CurvedScaleMapper, LinearScaleMapper, ScaleMapper


class CalibrationMode(Enum):
    SIMPLE = ("simple", "Calibrazione semplice")
    CURVED = ("curved", "Calibrazione con curva non lineare")
    MANUAL = ("manual", "Calibrazione manuale")

    def __init__(self, key: str, label: str):
        self.key = key
        self.label = label

    @property
    def uses_capture(self) -> bool:
        return self is not CalibrationMode.MANUAL

    @property
    def uses_curve(self) -> bool:
        return self is CalibrationMode.CURVED

    @classmethod
    def from_key(cls, key: str | None) -> "CalibrationMode":
        return next((m for m in cls if m.key == key), cls.SIMPLE)

    def create_mapper(self, floor_db: float, peak_db: float, exponent: float) -> ScaleMapper:
        if self.uses_curve:
            return CurvedScaleMapper(floor_db, peak_db, exponent)
        return LinearScaleMapper(floor_db, peak_db)
