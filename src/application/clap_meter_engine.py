from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from applause_analyzer.algorithm_registry import ApplauseAlgorithmRegistry
from audio.device_catalog import DeviceCatalog
from domain.calibration_capture import CalibrationCapture
from domain.calibration_mode import CalibrationMode
from domain.decibel import SILENCE_DB
from domain.level_smoother import LevelSmoother
from domain.score import MAX_SCORE, MIN_SCORE, round_score
from domain.score_extremes import ScoreExtremes
from domain.spike_filter import SpikeFilter
from domain.weighted_power_mixer import WeightedLevel, WeightedPowerMixer
from infrastructure.json_settings_store import JsonSettingsStore
from infrastructure.qml_file_catalog import QmlFileCatalog

from .applause_analyzer_controller import ApplauseAnalyzerController
from .channel_controller import ChannelController

TICK_MS = 50
CAPTURE_MS = 3000
FLOOR_MARGIN_DB = 3.0
DEFAULT_WEIGHT = 5.0
DEFAULT_SPIKE_MAX_MS = 300
SPIKE_QUIET_MS = 200
DEFAULT_SPIKE_THRESHOLD_DB = 12.0


class ClapMeterEngine(QObject):
    """Facciata del backend per QML: tutti gli stili pubblico leggono solo da qui."""

    channelsChanged = Signal()
    levelChanged = Signal()
    calibrationChanged = Signal()
    captureChanged = Signal()
    styleChanged = Signal()
    applauseChanged = Signal()
    paletteChanged = Signal()

    def __init__(self, devices: DeviceCatalog, styles: QmlFileCatalog, palettes: QmlFileCatalog,
                 store: JsonSettingsStore,
                 applause_registry: ApplauseAlgorithmRegistry):
        super().__init__()
        self._devices, self._styles, self._palettes, self._store = devices, styles, palettes, store
        self._mixer, self._smoother = WeightedPowerMixer(), LevelSmoother()
        self._spike_enabled = False
        self._spike_max_ms = DEFAULT_SPIKE_MAX_MS
        self._spike_threshold_db = DEFAULT_SPIKE_THRESHOLD_DB
        self._build_spike_filter()
        self._extremes = ScoreExtremes()
        self._applause = ApplauseAnalyzerController(applause_registry, parent=self)
        self._applause.stateChanged.connect(self.applauseChanged)
        self._combined_db, self._score = SILENCE_DB, MIN_SCORE
        self._capture: CalibrationCapture | None = None
        self._capture_kind = ""
        self._channels: list[ChannelController] = []
        self._restore(store.load())
        self._rebuild_mapper()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(TICK_MS)

    # ---- ciclo di misura ----
    def _tick(self) -> None:
        levels = [WeightedLevel(c.read_level(), c.effective_weight) for c in self._channels]
        raw_db = self._mixer.mix(levels)
        clean_db = self._spike_filter.filter(raw_db) if self._spike_enabled else raw_db
        if self._capture:
            self._capture.add(clean_db)
        self._combined_db = self._smoother.smooth(clean_db)
        self._score = round_score(self._mapper.map(self._combined_db))
        self._extremes.update(self._score)
        self._applause.feed(self._score)
        self.levelChanged.emit()

    def _build_spike_filter(self) -> None:
        self._spike_filter = SpikeFilter(self._spike_max_ms // TICK_MS, SPIKE_QUIET_MS // TICK_MS, self._spike_threshold_db)

    def _rebuild_mapper(self) -> None:
        self._mapper = self._mode.create_mapper(self._floor_db, self._peak_db, self._curve)
        self.calibrationChanged.emit()

    # ---- persistenza ----
    def _restore(self, data: dict) -> None:
        self._mode = CalibrationMode.from_key(data.get("mode"))
        self._floor_db = data.get("floorDb", -60.0)
        self._peak_db = data.get("peakDb", -20.0)
        self._curve = data.get("curve", 1.8)
        style = data.get("style")
        self._style = style if style in self._styles.names() else self._styles.default()
        palette = data.get("palette")
        self._palette = palette if palette in self._palettes.names() else self._palettes.default()
        spike = data.get("spikeFilter", {})
        self._spike_enabled = spike.get("enabled", False)
        self._spike_threshold_db = spike.get("thresholdDb", DEFAULT_SPIKE_THRESHOLD_DB)
        self._spike_max_ms = spike.get("maxDurationMs", DEFAULT_SPIKE_MAX_MS)
        self._build_spike_filter()
        self._applause.restore(data.get("applause", {}))
        for item in data.get("channels", []):
            self._append_channel(item["device"], item["weight"], item["enabled"])
        if not self._channels:
            self._append_channel(self._devices.default_name(), DEFAULT_WEIGHT, True)

    @Slot()
    def save(self) -> None:
        self._store.save({
            "mode": self._mode.key, "floorDb": self._floor_db, "peakDb": self._peak_db,
            "curve": self._curve, "style": self._style, "palette": self._palette,
            "spikeFilter": {"enabled": self._spike_enabled, "thresholdDb": self._spike_threshold_db,
                            "maxDurationMs": self._spike_max_ms},
            "applause": self._applause.snapshot(),
            "channels": [c.snapshot() for c in self._channels],
        })

    # ---- ingressi ----
    def _append_channel(self, device: str, weight: float, enabled: bool) -> None:
        self._channels.append(ChannelController(self._devices, device, weight, enabled, self))

    @Slot()
    def addChannel(self) -> None:
        self._append_channel(self._devices.default_name(), DEFAULT_WEIGHT, True)
        self.channelsChanged.emit()

    @Slot(int)
    def removeChannel(self, index: int) -> None:
        if len(self._channels) > 1:
            self._channels.pop(index).close()
            self.channelsChanged.emit()

    # ---- calibrazione ----
    @Slot()
    def captureFloor(self) -> None:
        self._start_capture("floor")

    @Slot()
    def capturePeak(self) -> None:
        self._start_capture("peak")

    def _start_capture(self, kind: str) -> None:
        if self._capture:
            return
        self._capture, self._capture_kind = CalibrationCapture(), kind
        self.captureChanged.emit()
        QTimer.singleShot(CAPTURE_MS, self._finish_capture)

    def _finish_capture(self) -> None:
        capture, kind = self._capture, self._capture_kind
        self._capture, self._capture_kind = None, ""
        if not capture.is_empty:
            if kind == "floor":
                self._floor_db = capture.floor_db(FLOOR_MARGIN_DB)
            else:
                self._peak_db = capture.peak_db()
        self.captureChanged.emit()
        self._rebuild_mapper()

    @Slot(bool)
    def setSpikeFilterEnabled(self, enabled: bool) -> None:
        self._spike_enabled = enabled
        self._build_spike_filter()
        self.calibrationChanged.emit()

    @Slot(float)
    def setSpikeThresholdDb(self, db: float) -> None:
        self._spike_threshold_db = db
        self._build_spike_filter()
        self.calibrationChanged.emit()

    @Slot(float)
    def setSpikeMaxDurationMs(self, milliseconds: float) -> None:
        self._spike_max_ms = int(milliseconds)
        self._build_spike_filter()
        self.calibrationChanged.emit()

    @Slot()
    def resetExtremes(self) -> None:
        self._extremes.reset()

    @Slot()
    def startApplauseAnalyzer(self) -> None:
        self._applause.start()

    @Slot()
    def stopApplauseAnalyzer(self) -> None:
        self._applause.stop()

    @Slot(int)
    def setModeIndex(self, index: int) -> None:
        self._mode = list(CalibrationMode)[index]
        self._rebuild_mapper()

    @Slot(float)
    def setFloorDb(self, db: float) -> None:
        self._floor_db = db
        self._rebuild_mapper()

    @Slot(float)
    def setPeakDb(self, db: float) -> None:
        self._peak_db = db
        self._rebuild_mapper()

    @Slot(float)
    def setCurveExponent(self, exponent: float) -> None:
        self._curve = exponent
        self._rebuild_mapper()

    @Slot(str)
    def setPalette(self, name: str) -> None:
        if name in self._palettes.names():
            self._palette = name
            self.paletteChanged.emit()

    @Slot(str)
    def setStyle(self, name: str) -> None:
        self._style = name
        self.styleChanged.emit()

    @Slot(result=list)
    def deviceNames(self) -> list:
        return self._devices.names()

    # ---- proprieta' per QML ----
    channels = Property(list, lambda s: list(s._channels), notify=channelsChanged)
    combinedDb = Property(float, lambda s: s._combined_db, notify=levelChanged)
    score = Property(float, lambda s: s._score, notify=levelChanged)  # alias di actual_score
    actual_score = Property(float, lambda s: s._score, notify=levelChanged)
    max_score = Property(float, lambda s: s._extremes.maximum, notify=levelChanged)
    min_score = Property(float, lambda s: s._extremes.minimum, notify=levelChanged)
    scale_max = Property(float, lambda s: MAX_SCORE, constant=True)
    scale_min = Property(float, lambda s: MIN_SCORE, constant=True)
    applause_score = Property(float, lambda s: s._applause.live_score, notify=levelChanged)
    applause_final_score = Property(float, lambda s: s._applause.final_score, notify=applauseChanged)
    applause_running = Property(bool, lambda s: s._applause.running, notify=applauseChanged)
    applause = Property(QObject, lambda s: s._applause, constant=True)
    spikeFilterEnabled = Property(bool, lambda s: s._spike_enabled, notify=calibrationChanged)
    spikeThresholdDb = Property(float, lambda s: s._spike_threshold_db, notify=calibrationChanged)
    spikeMaxDurationMs = Property(float, lambda s: float(s._spike_max_ms), notify=calibrationChanged)
    spikeDelayMs = Property(float, lambda s: float(s._spike_max_ms + SPIKE_QUIET_MS), notify=calibrationChanged)
    scoreText = Property(str, lambda s: f"{s._score:.1f}", notify=levelChanged)
    floorDb = Property(float, lambda s: s._floor_db, notify=calibrationChanged)
    peakDb = Property(float, lambda s: s._peak_db, notify=calibrationChanged)
    curveExponent = Property(float, lambda s: s._curve, notify=calibrationChanged)
    modeLabels = Property(list, lambda s: [m.label for m in CalibrationMode], constant=True)
    modeIndex = Property(int, lambda s: list(CalibrationMode).index(s._mode), notify=calibrationChanged)
    usesCapture = Property(bool, lambda s: s._mode.uses_capture, notify=calibrationChanged)
    usesCurve = Property(bool, lambda s: s._mode.uses_curve, notify=calibrationChanged)
    captureLabel = Property(str, lambda s: {"floor": "Ascolto del fondo...", "peak": "Ascolto dell'applauso..."}.get(s._capture_kind, ""), notify=captureChanged)
    styleNames = Property(list, lambda s: s._styles.names(), constant=True)
    styleName = Property(str, lambda s: s._style, notify=styleChanged)
    paletteOptions = Property(list, lambda s: s._palettes.options(), constant=True)
    paletteName = Property(str, lambda s: s._palette, notify=paletteChanged)
    paletteUrl = Property(str, lambda s: s._palettes.url(s._palette), notify=paletteChanged)
    styleUrl = Property(str, lambda s: s._styles.url(s._style), notify=styleChanged)
