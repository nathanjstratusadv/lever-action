from __future__ import annotations

from lever_action.storage.sessions import SessionStore


class TestSessionStore:
    def test_create_returns_token(self) -> None:
        store = SessionStore()
        token = store.create()
        assert isinstance(token, str)
        assert len(token) == 64

    def test_verify_valid_token(self) -> None:
        store = SessionStore()
        token = store.create()
        assert store.verify(token) is True

    def test_verify_invalid_token(self) -> None:
        store = SessionStore()
        assert store.verify("invalid-token") is False

    def test_verify_revoked_token(self) -> None:
        store = SessionStore()
        token = store.create()
        store.revoke(token)
        assert store.verify(token) is False

    def test_expired_token_fails_verify(self) -> None:
        store = SessionStore(max_age=-1)
        token = store.create()
        assert store.verify(token) is False

    def test_cleanup_expired_removes_old_sessions(self) -> None:
        store = SessionStore()
        store.create()
        old_store = SessionStore(max_age=-1)
        old_store.create()
        assert old_store.cleanup_expired() == 1

    def test_singleton_returns_same_instance(self) -> None:
        s1 = SessionStore.get_instance()
        s2 = SessionStore.get_instance()
        assert s1 is s2
