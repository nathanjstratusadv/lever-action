from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from typing import Self


@dataclass
class SessionInfo:
    token: str
    created_at: float
    expires_at: float


class SessionStore:
    DEFAULT_MAX_AGE = 2592000

    def __init__(self, max_age: int | None = None) -> None:
        self._sessions: dict[str, SessionInfo] = {}
        self._max_age = max_age or self.DEFAULT_MAX_AGE

    def create(self) -> str:
        token = secrets.token_hex(32)
        now = time.time()
        self._sessions[token] = SessionInfo(
            token=token,
            created_at=now,
            expires_at=now + self._max_age,
        )
        return token

    def verify(self, token: str) -> bool:
        info = self._sessions.get(token)
        if info is None:
            return False
        if time.time() > info.expires_at:
            self.revoke(token)
            return False
        return True

    def revoke(self, token: str) -> None:
        self._sessions.pop(token, None)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [
            token for token, info in self._sessions.items() if now > info.expires_at
        ]
        for token in expired:
            del self._sessions[token]
        return len(expired)

    @classmethod
    def get_instance(cls) -> Self:
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
