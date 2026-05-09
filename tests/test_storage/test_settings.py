from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from lever_action.storage.settings import SettingsStorage


class TestSettingsStorage:
    def test_get_all_returns_settings(self, tmp_path: Path) -> None:
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({"llm_provider": "openai"}))
        with patch.object(SettingsStorage, "__init__", lambda self: None):
            storage = SettingsStorage.__new__(SettingsStorage)
            storage._settings = {"llm_provider": "openai"}
            assert storage.get_all() == {"llm_provider": "openai"}

    def test_get_returns_default_when_missing(self) -> None:
        with patch.object(SettingsStorage, "__init__", lambda self: None):
            storage = SettingsStorage.__new__(SettingsStorage)
            storage._settings = {}
            assert storage.get("missing_key", "default") == "default"

    def test_set_updates_settings(self) -> None:
        with patch.object(SettingsStorage, "__init__", lambda self: None):
            storage = SettingsStorage.__new__(SettingsStorage)
            storage._settings = {}
            storage.set("key", "value")
            assert storage._settings["key"] == "value"

    def test_singleton_returns_same_instance(self) -> None:
        SettingsStorage._instance = None
        instance1 = SettingsStorage.get_instance()
        instance2 = SettingsStorage.get_instance()
        assert instance1 is instance2
        SettingsStorage._instance = None
