from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


@dataclass
class ChatEntry:
    prompt: str
    response: str
    timestamp: str


def _get_data_dir() -> Path:
    data_dir = Path(user_data_dir("lever_action", "lever_action", ensure_exists=True))
    return data_dir


class HistoryStorage:
    def __init__(self, user_id: str | None = None) -> None:
        self._user_id = user_id
        data_dir = _get_data_dir()
        if user_id:
            user_dir = data_dir / "users" / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            self._file_path = user_dir / "history.json"
        else:
            self._file_path = data_dir / "history.json"

    def _load(self) -> list[dict[str, str]]:
        if not self._file_path.exists():
            return []
        try:
            with open(self._file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, entries: list[dict[str, str]]) -> None:
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(
                    entries,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except OSError:
            logger.exception("Failed to save history")
            raise

    def add_entry(self, prompt: str, response: str) -> ChatEntry:
        entry = ChatEntry(
            prompt=prompt,
            response=response,
            timestamp=datetime.now(UTC).isoformat(),
        )
        entries = self._load()
        entries.append(entry.__dict__)
        self._save(entries)
        return entry

    def get_all(self) -> list[ChatEntry]:
        raw = self._load()
        return [ChatEntry(**e) for e in raw]

    def clear(self) -> None:
        self._save([])

    @classmethod
    def get_instance(cls, user_id: str | None = None) -> Self:
        instance_key = f"_instance_{user_id}"
        if not hasattr(cls, instance_key):
            setattr(cls, instance_key, cls(user_id=user_id))
        return getattr(cls, instance_key)
