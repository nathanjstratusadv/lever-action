from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from lever_action.storage.settings import (
    SETTINGS_VERSION,
    SettingsStorage,
    _get_old_settings_path,
    _get_settings_dir,
    _get_settings_path,
    _needs_migration,
)


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

    def test_save_includes_version(self, tmp_path: Path) -> None:
        SettingsStorage._instance = None
        with patch(
            "lever_action.storage.settings._get_settings_path",
            return_value=tmp_path / "settings.json",
        ):
            storage = SettingsStorage.get_instance()
            storage.save({"key": "value"})
            data = json.loads((tmp_path / "settings.json").read_text())
            assert data["_version"] == SETTINGS_VERSION
            assert data["key"] == "value"
        SettingsStorage._instance = None

    def test_migration_occurs_on_version_mismatch(self, tmp_path: Path) -> None:
        SettingsStorage._instance = None
        settings_path = tmp_path / "settings.json"
        old_path = tmp_path / "settings.old.json"
        settings_path.write_text(json.dumps({"_version": 0, "key": "old"}))
        with (
            patch(
                "lever_action.storage.settings._get_settings_path",
                return_value=settings_path,
            ),
            patch(
                "lever_action.storage.settings._get_old_settings_path",
                return_value=old_path,
            ),
        ):
            storage = SettingsStorage.get_instance()
            assert not settings_path.exists()
            assert old_path.exists()
            assert storage._settings == {}
        SettingsStorage._instance = None

    def test_no_migration_when_version_matches(self, tmp_path: Path) -> None:
        SettingsStorage._instance = None
        settings_path = tmp_path / "settings.json"
        old_path = tmp_path / "settings.old.json"
        settings_path.write_text(
            json.dumps({"_version": SETTINGS_VERSION, "key": "val"})
        )
        with (
            patch(
                "lever_action.storage.settings._get_settings_path",
                return_value=settings_path,
            ),
            patch(
                "lever_action.storage.settings._get_old_settings_path",
                return_value=old_path,
            ),
        ):
            storage = SettingsStorage.get_instance()
            assert settings_path.exists()
            assert not old_path.exists()
            assert storage._settings["key"] == "val"
        SettingsStorage._instance = None

    def test_starts_empty_when_no_config_exists(self, tmp_path: Path) -> None:
        SettingsStorage._instance = None
        config_path = tmp_path / "config" / "settings.json"
        with patch(
            "lever_action.storage.settings._get_settings_path",
            return_value=config_path,
        ):
            storage = SettingsStorage.get_instance()
            assert storage._settings == {}
        SettingsStorage._instance = None


class TestNeedsMigration:
    def test_no_migration_when_version_matches(self) -> None:
        assert not _needs_migration({"_version": SETTINGS_VERSION})

    def test_migration_when_version_mismatch(self) -> None:
        assert _needs_migration({"_version": 0})

    def test_migration_when_version_missing(self) -> None:
        assert _needs_migration({})


class TestPaths:
    def test_settings_dir_uses_dot_config(self) -> None:
        path = _get_settings_dir()
        assert ".config" in path.parts
        assert "lever_action" in path.parts

    def test_settings_path_is_in_settings_dir(self) -> None:
        path = _get_settings_path()
        assert path.name == "settings.json"
        assert ".config" in path.parts

    def test_old_settings_path_is_in_settings_dir(self) -> None:
        path = _get_old_settings_path()
        assert path.name == "settings.old.json"
        assert ".config" in path.parts
