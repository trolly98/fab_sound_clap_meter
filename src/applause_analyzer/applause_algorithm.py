from abc import ABC, abstractmethod

from .algorithm_parameter import AlgorithmParameter


class ApplauseAlgorithm(ABC):
    """Contratto di un algoritmo: riceve il punteggio live 1-10 e restituisce l'applause_score."""

    name: str = ""
    definitions: tuple[AlgorithmParameter, ...] = ()

    def __init__(self):
        self._values = {d.key: d.default for d in self.definitions}

    def value(self, key: str) -> float:
        return self._values[key]

    def values(self) -> dict[str, float]:
        return dict(self._values)

    def set_value(self, key: str, value: float) -> None:
        definition = next(d for d in self.definitions if d.key == key)
        self._values[key] = definition.clamp(value)

    def apply_values(self, values: dict[str, float]) -> None:
        for key, value in values.items():
            if key in self._values:
                self.set_value(key, value)

    def describe_parameters(self) -> list[dict]:
        return [d.describe(self._values[d.key]) for d in self.definitions]

    @abstractmethod
    def reset(self) -> None:
        """Azzera lo stato interno all'avvio di una nuova analisi."""

    @abstractmethod
    def feed(self, elapsed_s: float, score: float) -> float:
        """Riceve un punteggio (1-10) al secondo `elapsed_s` dall'avvio; restituisce l'applause_score."""
