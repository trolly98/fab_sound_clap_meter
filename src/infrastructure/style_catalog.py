from pathlib import Path

from PySide6.QtCore import QUrl


class StyleCatalog:
    """Scopre gli stili pubblico: ogni file *Style.qml nella cartella e' uno stile."""

    SUFFIX = "Style"

    def __init__(self, folder: Path):
        self._folder = folder

    def names(self) -> list[str]:
        return sorted(p.stem.removesuffix(self.SUFFIX) for p in self._folder.glob(f"*{self.SUFFIX}.qml"))

    def default(self) -> str:
        return self.names()[0]

    def url(self, name: str) -> str:
        return QUrl.fromLocalFile(str(self._folder / f"{name}{self.SUFFIX}.qml")).toString()
