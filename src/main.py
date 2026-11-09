import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from applause_analyzer.default_registry import build_default_registry
from application.clap_meter_engine import ClapMeterEngine
from audio.device_catalog import DeviceCatalog
from infrastructure.json_settings_store import JsonSettingsStore
from application.manche_controller import MancheController
from infrastructure.app_icon import AppIcon
from infrastructure.json_race_store import JsonRaceStore
from manche.race import Race
from infrastructure.qml_file_catalog import QmlFileCatalog

QML_DIR = Path(__file__).parent / "ui" / "qml"
ASSETS_DIR = Path(__file__).parent / "assets"
SETTINGS_PATH = Path.home() / ".fab_sound_clap_meter" / "settings.json"
RACE_PATH = Path.home() / ".fab_sound_clap_meter" / "race.json"


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("FabSound Clap Meter")
    AppIcon(ASSETS_DIR / "icon.png").apply(app)
    meter = ClapMeterEngine(DeviceCatalog(), QmlFileCatalog(QML_DIR / "styles", "Style"),
                             QmlFileCatalog(QML_DIR / "palettes", "Palette", preferred_default="Default"), JsonSettingsStore(SETTINGS_PATH),
                             build_default_registry())
    app.aboutToQuit.connect(meter.save)

    race_store = JsonRaceStore(RACE_PATH)
    saved_race = race_store.load()
    manche = MancheController(Race.from_dict(saved_race) if saved_race else Race(), race_store, meter.applause_controller)
    app.aboutToQuit.connect(manche.save)

    qml = QQmlApplicationEngine()
    qml.rootContext().setContextProperty("clapMeter", meter)
    qml.rootContext().setContextProperty("manche", manche)
    qml.load(QUrl.fromLocalFile(str(QML_DIR / "OperatorWindow.qml")))
    if not qml.rootObjects():
        return 1
    exit_code = app.exec()
    del qml  # chiude prima la UI, poi il backend che essa legge
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
