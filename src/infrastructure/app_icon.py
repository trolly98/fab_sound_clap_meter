import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon

WINDOWS_APP_ID = "fabsound.clapmeter"


class AppIcon:
    """Icona dell'app per tutte le finestre: barra del titolo e barra delle applicazioni.

    Se il file non c'e' (o non e' valido) l'app parte lo stesso con l'icona di sistema.
    """

    def __init__(self, path: Path):
        self._path = path

    def apply(self, app: QGuiApplication) -> bool:
        self._claim_windows_taskbar_identity()
        if not self._path.is_file():
            return False
        icon = QIcon(str(self._path))
        if icon.isNull():
            return False
        app.setWindowIcon(icon)
        return True

    @staticmethod
    def _claim_windows_taskbar_identity() -> None:
        """Su Windows, senza un identificativo proprio, la barra applicazioni mostra l'icona di Python."""
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_ID)
