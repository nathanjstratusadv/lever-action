from __future__ import annotations

from pathlib import Path

import pytest

from lever_action.storage.history import ChatEntry, HistoryStorage


@pytest.fixture
def history_storage(tmp_path: Path) -> HistoryStorage:
    storage = HistoryStorage(user_id="test-user")
    storage._file_path = tmp_path / "history.json"
    return storage


class TestHistoryStorage:
    def test_load_returns_empty_list_when_no_file(
        self, history_storage: HistoryStorage
    ) -> None:
        entries = history_storage._load()
        assert entries == []

    def test_load_returns_empty_list_on_invalid_json(
        self, history_storage: HistoryStorage
    ) -> None:
        history_storage._file_path.write_text("not valid json")
        entries = history_storage._load()
        assert entries == []

    def test_add_entry_creates_file_and_returns_entry(
        self, history_storage: HistoryStorage
    ) -> None:
        entry = history_storage.add_entry(
            "What is Python?", "Python is a programming language."
        )

        assert entry.prompt == "What is Python?"
        assert entry.response == "Python is a programming language."
        assert entry.timestamp
        assert history_storage._file_path.exists()

    def test_add_entry_appends_to_existing_entries(
        self, history_storage: HistoryStorage
    ) -> None:
        history_storage.add_entry("First?", "First answer.")
        history_storage.add_entry("Second?", "Second answer.")

        entries = history_storage._load()
        assert len(entries) == 2
        assert entries[0]["prompt"] == "First?"
        assert entries[1]["prompt"] == "Second?"

    def test_get_all_returns_chat_entries(
        self, history_storage: HistoryStorage
    ) -> None:
        history_storage.add_entry("Q1", "A1")
        history_storage.add_entry("Q2", "A2")

        entries = history_storage.get_all()
        assert len(entries) == 2
        assert isinstance(entries[0], ChatEntry)
        assert entries[0].prompt == "Q1"
        assert entries[1].prompt == "Q2"

    def test_clear_removes_all_entries(self, history_storage: HistoryStorage) -> None:
        history_storage.add_entry("Q", "A")
        assert len(history_storage.get_all()) == 1

        history_storage.clear()
        assert len(history_storage.get_all()) == 0

    def test_get_all_returns_empty_when_no_file(
        self, history_storage: HistoryStorage
    ) -> None:
        entries = history_storage.get_all()
        assert entries == []

    def test_add_entry_preserves_unicode(self, history_storage: HistoryStorage) -> None:
        history_storage.add_entry("What is 你好?", "你好 means hello.")
        entry = history_storage.get_all()[0]
        assert entry.prompt == "What is 你好?"
        assert entry.response == "你好 means hello."

    def test_add_entry_preserves_multiline_text(
        self, history_storage: HistoryStorage
    ) -> None:
        response = "Line 1\nLine 2\nLine 3"
        history_storage.add_entry("Multi?", response)
        entry = history_storage.get_all()[0]
        assert entry.response == response

    def test_singleton_returns_same_instance(self) -> None:
        s1 = HistoryStorage.get_instance(user_id="user1")
        s2 = HistoryStorage.get_instance(user_id="user1")
        assert s1 is s2

    def test_different_users_get_different_instances(self) -> None:
        s1 = HistoryStorage.get_instance(user_id="user1")
        s2 = HistoryStorage.get_instance(user_id="user2")
        assert s1 is not s2
