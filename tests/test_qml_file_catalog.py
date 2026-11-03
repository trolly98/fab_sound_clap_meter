import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fab_sound_clap_meter"))

from infrastructure.qml_file_catalog import QmlFileCatalog

PALETTES = Path(__file__).parent.parent / "fab_sound_clap_meter" / "ui" / "qml" / "palettes"


def test_label_splits_camel_case():
    assert QmlFileCatalog.label("PorporaStyle") == "Porpora Style"
    assert QmlFileCatalog.label("Default") == "Default"


def test_palettes_are_discovered_and_default_comes_first():
    catalog = QmlFileCatalog(PALETTES, "Palette", preferred_default="Default")
    assert catalog.names() == ["Default", "PorporaStyle"]
    assert catalog.default() == "Default"
    assert [o["label"] for o in catalog.options()] == ["Default", "Porpora Style"]


def test_base_file_is_not_listed_as_a_palette():
    assert "ScoreBase" not in QmlFileCatalog(PALETTES, "Palette").names()
    assert all("Base" not in n for n in QmlFileCatalog(PALETTES, "Palette").names())
