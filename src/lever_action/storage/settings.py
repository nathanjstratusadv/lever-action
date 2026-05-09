from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import Any


def _get_settings_path() -> Path:
    exe_dir = Path(sys.executable).parent
    if getattr(sys, "frozen", False):
        base = (
            exe_dir / "_internal" if not (exe_dir / "templates").exists() else exe_dir
        )
    else:
        base = Path(__file__).parent.parent
    return base / "settings.json"


class SettingsStorage:
    _instance: SettingsStorage | None = None
    _lock = threading.Lock()
    _settings: dict[str, Any]

    def __init__(self) -> None:
        self._settings = {}
        self._path = _get_settings_path()
        self._load()

    @classmethod
    def get_instance(cls) -> SettingsStorage:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._settings = {}
        else:
            self._settings = {}

    def get_all(self) -> dict[str, Any]:
        return dict(self._settings)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def save(self, settings: dict[str, Any]) -> None:
        self._settings = dict(settings)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=4)

    def reload(self) -> None:
        self._load()
