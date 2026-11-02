from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from audio.device_catalog import DeviceCatalog
from domain.calibration_capture import CalibrationCapture
from domain.calibration_mode import CalibrationMode
from domain.decibel import SILENCE_DB
from domain.level_smoother import LevelSmoother
from domain.score import round_score
from domain.weighted_power_mixer import WeightedLevel, WeightedPowerMixer
from infrastructure.json_settings_store import JsonSettingsStore
from infrastructure.style_catalog import StyleCatalog

from .channel_controller import ChannelController

TICK_MS = 50
CAPTURE_MS = 3000
FLOOR_MARGIN_DB = 3.0
DEFAULT_WEIGHT = 5.0


class ClapMeterEngine(QObject):
    """Facciata del backend per QML: tutti gli stili pubblico leggono solo da qui."""

    channelsChanged = Signal()
    levelChanged = Signal()
    calibrationChanged = Signal()
    captureChanged = Signal()
    styleChanged = Signal()

    def __init__(self, devices: DeviceCatalog, styles: StyleCatalog, store: JsonSettingsStore):
        super().__init__()
        self._devices, self._styles, self._store = devices, styles, store
        self._mixer, self._smoother = WeightedPowerMixer(), LevelSmoother()
        self._combined_db, self._score = SILENCE_DB, 1.0
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
        if self._capture:
            self._capture.add(raw_db)
        self._combined_db = self._smoother.smooth(raw_db)
        self._score = round_score(self._mapper.map(self._combined_db))
        self.levelChanged.emit()

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
        for item in data.get("channels", []):
            self._append_channel(item["device"], item["weight"], item["enabled"])
        if not self._channels:
            self._append_channel(self._devices.default_name(), DEFAULT_WEIGHT, True)

    @Slot()
    def save(self) -> None:
        self._store.save({
            "mode": self._mode.key, "floorDb": self._floor_db, "peakDb": self._peak_db,
            "curve": self._curve, "style": self._style,
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
    def setStyle(self, name: str) -> None:
        self._style = name
        self.styleChanged.emit()

    @Slot(result=list)
    def deviceNames(self) -> list:
        return self._devices.names()

    # ---- proprieta' per QML ----
    channels = Property(list, lambda s: list(s._channels), notify=channelsChanged)
    combinedDb = Property(float, lambda s: s._combined_db, notify=levelChanged)
    score = Property(float, lambda s: s._score, notify=levelChanged)
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
    styleUrl = Property(str, lambda s: s._styles.url(s._style), notify=styleChanged)
