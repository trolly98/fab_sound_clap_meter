import numpy as np
from PySide6.QtMultimedia import QAudioFormat

_FORMATS = {
    QAudioFormat.SampleFormat.Int16: (np.int16, 32768.0),
    QAudioFormat.SampleFormat.Int32: (np.int32, 2147483648.0),
    QAudioFormat.SampleFormat.Float: (np.float32, 1.0),
}


class SampleDecoder:
    """Converte i byte grezzi del dispositivo in campioni float [-1, 1]."""

    def __init__(self, sample_format: QAudioFormat.SampleFormat):
        if sample_format not in _FORMATS:
            raise ValueError(f"Formato campioni non supportato: {sample_format}")
        self._dtype, self._scale = _FORMATS[sample_format]

    def decode(self, raw: bytes) -> np.ndarray:
        itemsize = np.dtype(self._dtype).itemsize
        usable = len(raw) - len(raw) % itemsize
        samples = np.frombuffer(raw[:usable], dtype=self._dtype)
        return samples.astype(np.float64) / self._scale
