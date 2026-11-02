from PySide6.QtCore import Property, QObject, Signal

from audio.audio_input_channel import AudioInputChannel
from audio.device_catalog import DeviceCatalog
from domain.decibel import SILENCE_DB


class ChannelController(QObject):
    """Ingresso audio configurabile (dispositivo, peso, attivo) esposto a QML."""

    changed = Signal()
    levelChanged = Signal()

    def __init__(self, devices: DeviceCatalog, device_name: str, weight: float, enabled: bool, parent=None):
        super().__init__(parent)
        self._devices = devices
        self._device_name = device_name
        self._weight = weight
        self._enabled = enabled
        self._level_db = SILENCE_DB
        self._input: AudioInputChannel | None = None
        self._reopen()

    def _reopen(self) -> None:
        if self._input:
            self._input.stop()
            self._input = None
        device = self._devices.find(self._device_name) if self._enabled else None
        if device:
            self._input = AudioInputChannel(device)
            self._input.start()

    def read_level(self) -> float:
        self._level_db = self._input.read_level_db() if self._input else SILENCE_DB
        self.levelChanged.emit()
        return self._level_db

    @property
    def effective_weight(self) -> float:
        return self._weight if self._enabled else 0.0

    def snapshot(self) -> dict:
        return {"device": self._device_name, "weight": self._weight, "enabled": self._enabled}

    def close(self) -> None:
        if self._input:
            self._input.stop()

    def _get_device(self) -> str:
        return self._device_name

    def _set_device(self, name: str) -> None:
        self._device_name = name
        self._reopen()
        self.changed.emit()

    def _get_weight(self) -> float:
        return self._weight

    def _set_weight(self, weight: float) -> None:
        self._weight = weight
        self.changed.emit()

    def _get_enabled(self) -> bool:
        return self._enabled

    def _set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._reopen()
        self.changed.emit()

    deviceName = Property(str, _get_device, _set_device, notify=changed)
    weight = Property(float, _get_weight, _set_weight, notify=changed)
    enabled = Property(bool, _get_enabled, _set_enabled, notify=changed)
    levelDb = Property(float, lambda self: self._level_db, notify=levelChanged)
