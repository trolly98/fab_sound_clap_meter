from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSource

from .power_accumulator import PowerAccumulator
from .sample_decoder import SampleDecoder


class AudioInputChannel:
    """Un singolo ingresso audio aperto: espone solo il livello in dBFS."""

    def __init__(self, device: QAudioDevice):
        fmt = self._choose_format(device)
        self._decoder = SampleDecoder(fmt.sampleFormat())
        self._accumulator = PowerAccumulator()
        self._source = QAudioSource(device, fmt)
        self._stream = None

    @staticmethod
    def _choose_format(device: QAudioDevice) -> QAudioFormat:
        preferred = device.preferredFormat()
        candidate = QAudioFormat()
        candidate.setSampleRate(preferred.sampleRate())
        candidate.setChannelCount(preferred.channelCount())
        candidate.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        return candidate if device.isFormatSupported(candidate) else preferred

    def start(self) -> None:
        self._stream = self._source.start()
        self._stream.readyRead.connect(self._on_ready_read)

    def stop(self) -> None:
        self._source.stop()
        self._stream = None

    def read_level_db(self) -> float:
        return self._accumulator.consume_db()

    def _on_ready_read(self) -> None:
        self._accumulator.add(self._decoder.decode(bytes(self._stream.readAll())))
