import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from application.clap_meter_engine import ClapMeterEngine
from audio.device_catalog import DeviceCatalog
from infrastructure.json_settings_store import JsonSettingsStore
from infrastructure.style_catalog import StyleCatalog

QML_DIR = Path(__file__).parent / "ui" / "qml"
SETTINGS_PATH = Path.home() / ".fab_sound_clap_meter" / "settings.json"


def main() -> int:
    app = QGuiApplication(sys.argv)
    meter = ClapMeterEngine(DeviceCatalog(), StyleCatalog(QML_DIR / "styles"), JsonSettingsStore(SETTINGS_PATH))
    app.aboutToQuit.connect(meter.save)

    qml = QQmlApplicationEngine()
    qml.rootContext().setContextProperty("clapMeter", meter)
    qml.load(QUrl.fromLocalFile(str(QML_DIR / "OperatorWindow.qml")))
    return app.exec() if qml.rootObjects() else 1


if __name__ == "__main__":
    sys.exit(main())
