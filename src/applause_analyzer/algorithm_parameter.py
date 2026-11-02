from dataclasses import dataclass


@dataclass(frozen=True)
class AlgorithmParameter:
    """Descrive un parametro regolabile: l'interfaccia dell'operatore si costruisce da qui."""

    key: str
    label: str
    unit: str
    minimum: float
    maximum: float
    step: float
    default: float
    advanced: bool = False   # mostrato dentro "Advanced settings"

    def clamp(self, value: float) -> float:
        return min(self.maximum, max(self.minimum, value))

    def describe(self, value: float) -> dict:
        return {"key": self.key, "label": self.label, "unit": self.unit, "minimum": self.minimum,
                "maximum": self.maximum, "step": self.step, "value": value, "advanced": self.advanced}
