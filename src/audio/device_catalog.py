from PySide6.QtMultimedia import QAudioDevice, QMediaDevices


class DeviceCatalog:
    def names(self) -> list[str]:
        return [d.description() for d in QMediaDevices.audioInputs()]

    def find(self, description: str) -> QAudioDevice | None:
        return next((d for d in QMediaDevices.audioInputs() if d.description() == description), None)

    def default_name(self) -> str:
        """Ingresso predefinito; stringa vuota se non c'e' nessun ingresso."""
        devices = QMediaDevices.audioInputs()
        preferred = next((d for d in devices if d.isDefault()), devices[0] if devices else None)
        return preferred.description() if preferred else ""
