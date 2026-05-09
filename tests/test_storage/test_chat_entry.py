from __future__ import annotations

from lever_action.storage.history import ChatEntry


class TestChatEntry:
    def test_create_entry(self) -> None:
        entry = ChatEntry(
            prompt="What is AI?",
            response="AI is artificial intelligence.",
            timestamp="2024-01-01T00:00:00+00:00",
        )

        assert entry.prompt == "What is AI?"
        assert entry.response == "AI is artificial intelligence."
        assert entry.timestamp == "2024-01-01T00:00:00+00:00"
