import json
from pathlib import Path


class JsonRaceStore:
    """Salva la gara e i modelli su file: ogni modifica valida e' recuperabile dopo la chiusura del programma."""

    def __init__(self, path: Path):
        self._path = path

    def load(self) -> dict | None:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return data if "game" in data and "models" in data else None
        except (OSError, ValueError):
            return None

    def save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        temporary.replace(self._path)          # scrittura atomica: un file mai a meta'
