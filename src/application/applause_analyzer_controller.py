import time
from typing import Callable

from PySide6.QtCore import Property, QObject, Signal, Slot

from applause_analyzer.algorithm_registry import ApplauseAlgorithmRegistry
from applause_analyzer.applause_analyzer import ApplauseAnalyzer

DEFAULT_SESSION_S = 10.0
MIN_SESSION_S, MAX_SESSION_S = 2.0, 120.0


class ApplauseAnalyzerController(QObject):
    """Espone a QML l'algoritmo scelto, i suoi parametri e le sessioni di ascolto.

    Una sessione ha un esito esplicito, comunicato UNA volta con `sessionFinished(token, status, voto, secondi)`:
      valid      ha ricevuto segnale: il voto e' il punteggio finale dell'analizzatore
      empty      nessun ingresso audio attivo durante la sessione
      cancelled  annullata dall'operatore
    Il valore 1.0 non dice nulla sulla validita': conta solo `status`.
    """

    stateChanged = Signal()
    parametersChanged = Signal()
    progressChanged = Signal()
    sessionDurationChanged = Signal()
    sessionFinished = Signal(str, str, float, float)

    def __init__(self, registry: ApplauseAlgorithmRegistry, clock: Callable[[], float] = time.monotonic, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._clock = clock
        self._saved_values: dict[str, dict[str, float]] = {}
        self._analyzer = ApplauseAnalyzer(registry.create(registry.names()[0]))
        self._session_duration_s = DEFAULT_SESSION_S
        self._token = ""
        self._timed_s: float | None = None
        self._started_at = 0.0
        self._input_samples = 0

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

    @property
    def session_duration_s(self) -> float:
        return self._session_duration_s

    def feed(self, score: float, has_input: bool = True) -> None:
        if not self.running:
            return
        self._analyzer.feed(self._clock(), score)
        self._input_samples += has_input
        if self._timed_s is not None and self._elapsed() >= self._timed_s:
            self.finish()
        else:
            self.progressChanged.emit()

    def begin(self, token: str, timed_s: float | None = None) -> None:
        """Avvia una sessione. Con `timed_s` si ferma da sola dopo quei secondi."""
        self._token, self._timed_s, self._input_samples = token, timed_s, 0
        self._started_at = self._clock()
        self._analyzer.start(self._started_at)
        self.stateChanged.emit()
        self.progressChanged.emit()

    def finish(self, cancelled: bool = False) -> None:
        if not self.running:
            return
        elapsed, token = self._elapsed(), self._token
        self._analyzer.stop()
        status = "cancelled" if cancelled else "valid" if self._input_samples else "empty"
        self._token, self._timed_s = "", None
        self.stateChanged.emit()
        self.progressChanged.emit()
        self.sessionFinished.emit(token, status, self._analyzer.final_score, elapsed)

    def _elapsed(self) -> float:
        return self._clock() - self._started_at if self.running else 0.0

    def snapshot(self) -> dict:
        self._remember_current_values()
        return {"algorithm": self._analyzer.algorithm.name, "parameters": self._saved_values,
                "sessionDurationS": self._session_duration_s}

    def restore(self, data: dict) -> None:
        self._saved_values = dict(data.get("parameters", {}))
        self._session_duration_s = min(MAX_SESSION_S, max(MIN_SESSION_S, data.get("sessionDurationS", DEFAULT_SESSION_S)))
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
        self.begin("")

    @Slot()
    def stop(self) -> None:
        self.finish()

    @Slot()
    def cancel(self) -> None:
        self.finish(cancelled=True)

    @Slot(str)
    def selectAlgorithm(self, name: str) -> None:
        if name in self._registry.names() and name != self._analyzer.algorithm.name:
            if self.running:
                self.finish(cancelled=True)
            self._remember_current_values()
            self._activate(name)

    @Slot(str, float)
    def setParameter(self, key: str, value: float) -> None:
        self._analyzer.algorithm.set_value(key, value)

    @Slot(float)
    def setSessionDurationS(self, seconds: float) -> None:
        self._session_duration_s = min(MAX_SESSION_S, max(MIN_SESSION_S, float(seconds)))
        self.sessionDurationChanged.emit()

    algorithmNames = Property(list, lambda s: s._registry.names(), constant=True)
    algorithmName = Property(str, lambda s: s._analyzer.algorithm.name, notify=parametersChanged)
    parameters = Property(list, lambda s: s._analyzer.algorithm.describe_parameters(), notify=parametersChanged)
    sessionDurationS = Property(float, lambda s: s._session_duration_s, notify=sessionDurationChanged)
    sessionMinS = Property(float, lambda s: MIN_SESSION_S, constant=True)
    sessionMaxS = Property(float, lambda s: MAX_SESSION_S, constant=True)
    running_ = Property(bool, lambda s: s.running, notify=stateChanged)
    timed = Property(bool, lambda s: s._timed_s is not None, notify=stateChanged)
    elapsedS = Property(float, lambda s: s._elapsed(), notify=progressChanged)
    remainingS = Property(float, lambda s: max(0.0, s._timed_s - s._elapsed()) if s._timed_s is not None else 0.0,
                          notify=progressChanged)
