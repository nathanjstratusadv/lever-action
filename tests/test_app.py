from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from webtest import TestApp

from lever_action.services.chat_service import ChatMode, GuidelineMode
from main import (
    MAX_REQUEST_SIZE,
    _per_session_services,
    markdown_to_html,
    session_store,
)
from main import app as bottle_app


@pytest.fixture(autouse=True)
def reset_state() -> None:
    bottle_app.config["skip_auth"] = True
    session_store._sessions.clear()
    _per_session_services.clear()
    yield
    bottle_app.config["skip_auth"] = False
    session_store._sessions.clear()
    _per_session_services.clear()


@pytest.fixture
def client() -> TestApp:
    return TestApp(bottle_app)


class TestIndex:
    def test_serves_index_page(self, client: TestApp) -> None:
        resp = client.get("/")
        assert resp.status_int == 200
        assert b"Lever Action" in resp.body


class TestChat:
    def test_requires_prompt(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (
            MagicMock(),
            MagicMock(),
        )
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/chat",
            params=json.dumps({"prompt": ""}).encode(),
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400

    def test_unauthorized_without_session(self, client: TestApp) -> None:
        resp = client.post(
            "/chat",
            params=json.dumps({"prompt": "hello"}).encode(),
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 401

    def test_returns_response_and_html(self, client: TestApp) -> None:
        mock_intel = MagicMock()
        mock_intel.text = "This is **bold** response"

        mock_chat_service = MagicMock()
        mock_chat_service.process.return_value = mock_intel
        mock_chat_service.mode = ChatMode.FIRE_AND_FORGET

        mock_history = MagicMock()
        mock_entry = MagicMock()
        mock_entry.timestamp = "2024-01-01T00:00:00+00:00"
        mock_history.add_entry.return_value = mock_entry

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, mock_history)
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/chat",
            params=json.dumps({"prompt": "Hello"}).encode(),
            content_type="application/json",
        )

        assert resp.status_int == 200
        data = resp.json
        assert data["prompt"] == "Hello"
        assert data["response"] == "This is **bold** response"
        assert "<strong>bold</strong>" in data["response_html"]


class TestHistory:
    def test_returns_empty_when_no_entries(self, client: TestApp) -> None:
        mock_history = MagicMock()
        mock_history.get_all.return_value = []

        token = session_store.create()
        _per_session_services[token] = (MagicMock(), mock_history)
        client.set_cookie("lever_action_session", token)

        resp = client.get("/history")
        assert resp.status_int == 200
        assert resp.json == []

    def test_returns_all_entries(self, client: TestApp) -> None:
        from lever_action.storage.history import ChatEntry

        mock_history = MagicMock()
        mock_history.get_all.return_value = [
            ChatEntry(prompt="Q1", response="A1", timestamp="t1"),
            ChatEntry(prompt="Q2", response="A2", timestamp="t2"),
        ]

        token = session_store.create()
        _per_session_services[token] = (MagicMock(), mock_history)
        client.set_cookie("lever_action_session", token)

        resp = client.get("/history")
        assert resp.status_int == 200
        data = resp.json
        assert len(data) == 2
        assert data[0]["prompt"] == "Q2"
        assert data[1]["prompt"] == "Q1"

    def test_entries_include_html(self, client: TestApp) -> None:
        from lever_action.storage.history import ChatEntry

        mock_history = MagicMock()
        mock_history.get_all.return_value = [
            ChatEntry(prompt="Q", response="A", timestamp="t1"),
        ]

        token = session_store.create()
        _per_session_services[token] = (MagicMock(), mock_history)
        client.set_cookie("lever_action_session", token)

        resp = client.get("/history")
        data = resp.json
        assert "response_html" in data[0]


class TestMode:
    def test_get_mode_returns_current(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.mode = ChatMode.FIRE_AND_FORGET

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.get("/mode")
        assert resp.status_int == 200
        assert resp.json["mode"] == "fire_and_forget"

    def test_post_mode_sets_aim_and_ask(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.mode = ChatMode.FIRE_AND_FORGET

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/mode",
            params=json.dumps({"mode": "aim_and_ask"}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["mode"] == "aim_and_ask"
        mock_chat_service.set_mode.assert_called_once_with(ChatMode.AIM_AND_ASK)

    def test_post_mode_sets_fire_and_forget(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.mode = ChatMode.AIM_AND_ASK

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/mode",
            params=json.dumps({"mode": "fire_and_forget"}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["mode"] == "fire_and_forget"
        mock_chat_service.set_mode.assert_called_once_with(ChatMode.FIRE_AND_FORGET)

    def test_post_mode_rejects_invalid(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (MagicMock(), MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/mode",
            params=json.dumps({"mode": "invalid"}).encode(),
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400

    def test_post_mode_rejects_empty_body(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (MagicMock(), MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/mode",
            params=b"",
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400


class TestGuideline:
    def test_get_guideline_returns_current(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.guideline_mode = GuidelineMode.NORMAL

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.get("/guideline")
        assert resp.status_int == 200
        assert resp.json["guideline"] == "normal"

    def test_post_guideline_sets_concise(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.guideline_mode = GuidelineMode.NORMAL

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/guideline",
            params=json.dumps({"guideline": "concise"}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["guideline"] == "concise"
        mock_chat_service.set_guideline_mode.assert_called_once_with(
            GuidelineMode.CONCISE
        )

    def test_post_guideline_sets_normal(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.guideline_mode = GuidelineMode.CONCISE

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/guideline",
            params=json.dumps({"guideline": "normal"}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["guideline"] == "normal"
        mock_chat_service.set_guideline_mode.assert_called_once_with(
            GuidelineMode.NORMAL
        )

    def test_post_guideline_rejects_invalid(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (MagicMock(), MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/guideline",
            params=json.dumps({"guideline": "invalid"}).encode(),
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400


class TestLogin:
    def test_unauthenticated_gets_redirected_to_home(self, client: TestApp) -> None:
        bottle_app.config["skip_auth"] = False
        try:
            resp = client.get("/", expect_errors=True)
            assert resp.status_int == 302
            assert resp.headers["Location"].endswith("/")
        finally:
            bottle_app.config["skip_auth"] = True

    def test_unauthenticated_creates_session_and_redirects(
        self, client: TestApp
    ) -> None:
        bottle_app.config["skip_auth"] = False
        try:
            resp = client.get("/", expect_errors=True)
            assert resp.status_int == 302
            cookies = resp.headers.getall("Set-Cookie")
            session_cookies = [c for c in cookies if "lever_action_session" in c]
            assert len(session_cookies) == 1
            assert "HttpOnly" in session_cookies[0]
            assert "SameSite=lax" in session_cookies[0]
        finally:
            bottle_app.config["skip_auth"] = True

    def test_logout_redirects_to_home(self, client: TestApp) -> None:
        bottle_app.config["skip_auth"] = False
        try:
            resp = client.post("/logout", expect_errors=True)
            assert resp.status_int == 302
            assert resp.location.endswith("/")
        finally:
            bottle_app.config["skip_auth"] = True

    def test_logout_revokes_session(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (MagicMock(), MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post("/logout", expect_errors=True)
        assert resp.status_int == 302

        assert session_store.verify(token) is False
        assert token not in _per_session_services


class TestMarkdownToHtml:
    def test_python_code_block_highlighted(self) -> None:
        md = "```python\ndef foo():\n    pass\n```"
        html = markdown_to_html(md)
        assert 'class="highlight"' in html
        assert 'class="k"' in html

    def test_code_block_no_double_pre(self) -> None:
        md = "```python\nx = 1\n```"
        html = markdown_to_html(md)
        assert "<pre><div" not in html
        assert html.count("<pre>") == html.count("</pre>")

    def test_inline_code_renders(self) -> None:
        md = "Use `foo()` here."
        html = markdown_to_html(md)
        assert "<code>foo()</code>" in html

    def test_unsupported_language_plain_block(self) -> None:
        md = "```haskell\nmain = return ()\n```"
        html = markdown_to_html(md)
        assert 'class="highlight"' in html
        assert "main" in html
        assert "return" in html

    def test_unspecified_language_block(self) -> None:
        md = "```\njust some code\n```"
        html = markdown_to_html(md)
        assert 'class="highlight"' in html
        assert "just some code" in html


class TestRequestSize:
    def test_rejects_oversized_request(self, client: TestApp) -> None:
        large_body = json.dumps({"prompt": "x" * (MAX_REQUEST_SIZE + 1)})
        resp = client.post(
            "/chat",
            params=large_body.encode(),
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 413


class TestTarget:
    def test_get_target_returns_current(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.target = "Python Django"

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.get("/target")
        assert resp.status_int == 200
        assert resp.json["target"] == "Python Django"

    def test_post_target_sets_value(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.target = ""

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/target",
            params=json.dumps({"target": "Python Django"}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["target"] == ""
        mock_chat_service.set_target.assert_called_once_with("Python Django")

    def test_post_target_clears_value(self, client: TestApp) -> None:
        mock_chat_service = MagicMock()
        mock_chat_service.target = "Python Django"

        token = session_store.create()
        _per_session_services[token] = (mock_chat_service, MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/target",
            params=json.dumps({"target": ""}).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        mock_chat_service.set_target.assert_called_once_with("")

    def test_post_target_rejects_empty_body(self, client: TestApp) -> None:
        token = session_store.create()
        _per_session_services[token] = (MagicMock(), MagicMock())
        client.set_cookie("lever_action_session", token)

        resp = client.post(
            "/target",
            params=b"",
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400


class TestSettings:
    def test_get_settings_returns_all(self, client: TestApp) -> None:
        resp = client.get("/settings")
        assert resp.status_int == 200
        assert isinstance(resp.json, dict)

    def test_post_settings_saves_and_reloads(self, client: TestApp) -> None:
        new_settings = {
            "host": "api.anthropic.com",
            "port": 443,
            "api_key": "sk-ant-test",
            "model": "claude-sonnet-4-20250514",
        }
        resp = client.post(
            "/settings",
            params=json.dumps(new_settings).encode(),
            content_type="application/json",
        )
        assert resp.status_int == 200
        assert resp.json["ok"] is True

        get_resp = client.get("/settings")
        assert get_resp.json["host"] == "api.anthropic.com"
        assert get_resp.json["model"] == "claude-sonnet-4-20250514"

    def test_post_settings_rejects_empty_body(self, client: TestApp) -> None:
        resp = client.post(
            "/settings",
            params=b"",
            content_type="application/json",
            expect_errors=True,
        )
        assert resp.status_int == 400
