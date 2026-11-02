import time
from typing import Callable

from PySide6.QtCore import Property, QObject, Signal, Slot

from applause_analyzer.algorithm_registry import ApplauseAlgorithmRegistry
from applause_analyzer.applause_analyzer import ApplauseAnalyzer


class ApplauseAnalyzerController(QObject):
    """Espone a QML la scelta dell'algoritmo, i suoi parametri e start/stop."""

    stateChanged = Signal()
    parametersChanged = Signal()

    def __init__(self, registry: ApplauseAlgorithmRegistry, clock: Callable[[], float] = time.monotonic, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._clock = clock
        self._saved_values: dict[str, dict[str, float]] = {}
        self._analyzer = ApplauseAnalyzer(registry.create(registry.names()[0]))

    # ---- uso da Python ----
    @property
    def live_score(self) -> float:
        return self._analyzer.live_score

    @property
    def final_score(self) -> float:
        return self._analyzer.final_score

    @property
    def running(self) -> bool:
        return self._analyzer.running

    def feed(self, score: float) -> None:
        self._analyzer.feed(self._clock(), score)

    def snapshot(self) -> dict:
        self._remember_current_values()
        return {"algorithm": self._analyzer.algorithm.name, "parameters": self._saved_values}

    def restore(self, data: dict) -> None:
        self._saved_values = dict(data.get("parameters", {}))
        name = data.get("algorithm")
        if name in self._registry.names():
            self._activate(name)

    def _remember_current_values(self) -> None:
        algorithm = self._analyzer.algorithm
        self._saved_values[algorithm.name] = algorithm.values()

    def _activate(self, name: str) -> None:
        algorithm = self._registry.create(name)
        algorithm.apply_values(self._saved_values.get(name, {}))
        self._analyzer.set_algorithm(algorithm)
        self.parametersChanged.emit()
        self.stateChanged.emit()

    # ---- uso da QML ----
    @Slot()
    def start(self) -> None:
        self._analyzer.start(self._clock())
        self.stateChanged.emit()

    @Slot()
    def stop(self) -> None:
        self._analyzer.stop()
        self.stateChanged.emit()

    @Slot(str)
    def selectAlgorithm(self, name: str) -> None:
        if name in self._registry.names() and name != self._analyzer.algorithm.name:
            self._remember_current_values()
            self._activate(name)

    @Slot(str, float)
    def setParameter(self, key: str, value: float) -> None:
        self._analyzer.algorithm.set_value(key, value)

    algorithmNames = Property(list, lambda s: s._registry.names(), constant=True)
    algorithmName = Property(str, lambda s: s._analyzer.algorithm.name, notify=parametersChanged)
    parameters = Property(list, lambda s: s._analyzer.algorithm.describe_parameters(), notify=parametersChanged)
