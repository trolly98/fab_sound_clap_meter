import re
from pathlib import Path

from PySide6.QtCore import QUrl


class QmlFileCatalog:
    """Scopre i file `<Nome><suffisso>.qml` di una cartella: ogni file e' una scelta selezionabile.

    Serve sia per gli stili (suffisso "Style") sia per le palette (suffisso "Palette"):
    per aggiungere una scelta basta copiare un file, senza toccare il codice.
    """

    def __init__(self, folder: Path, suffix: str, preferred_default: str | None = None):
        self._folder = folder
        self._suffix = suffix
        self._preferred_default = preferred_default

    def names(self) -> list[str]:
        return sorted(p.stem.removesuffix(self._suffix) for p in self._folder.glob(f"*{self._suffix}.qml"))

    def default(self) -> str:
        names = self.names()
        return self._preferred_default if self._preferred_default in names else names[0]

    @staticmethod
    def label(name: str) -> str:
        """'PorporaStyle' -> 'Porpora Style'."""
        return re.sub(r"(?<!^)(?=[A-Z])", " ", name)

    def options(self) -> list[dict]:
        return [{"id": name, "label": self.label(name)} for name in self.names()]

    def url(self, name: str) -> str:
        return QUrl.fromLocalFile(str(self._folder / f"{name}{self._suffix}.qml")).toString()
