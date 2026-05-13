from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

SETTINGS_VERSION = 1


def _get_settings_dir() -> Path:
    return Path.home() / ".config" / "lever_action"


def _get_settings_path() -> Path:
    return _get_settings_dir() / "settings.json"


def _needs_migration(settings: dict[str, Any]) -> bool:
    stored_version = settings.get("_version")
    return stored_version is None or stored_version != SETTINGS_VERSION


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
        self._path.parent.mkdir(parents=True, exist_ok=True)

        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._settings = {}

            if _needs_migration(self._settings):
                self._settings["_version"] = SETTINGS_VERSION
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._path, "w", encoding="utf-8") as f:
                    json.dump(self._settings, f, indent=4)

    def get_all(self) -> dict[str, Any]:
        return {k: v for k, v in self._settings.items() if not k.startswith("_")}

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def save(self, settings: dict[str, Any]) -> None:
        self._settings = dict(settings)
        self._settings["_version"] = SETTINGS_VERSION
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=4)

    def reload(self) -> None:
        self._load()
