from __future__ import annotations

import json
import logging
import os
import re
import sys
import threading
import time
from pathlib import Path

from bottle import TEMPLATE_PATH, Bottle, HTTPResponse, request, static_file, template
from dotenv import load_dotenv

from lever_action.services.chat_service import ChatMode, ChatService, GuidelineMode
from lever_action.storage.history import HistoryStorage
from lever_action.storage.sessions import SessionStore
from lever_action.storage.settings import SettingsStorage

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    log_dir = get_resource_path() / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "lever_action.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(formatter)
    root.addHandler(stderr_handler)


MAX_REQUEST_SIZE = 1024 * 1024
SESSION_MAX_AGE = 2592000
CLEANUP_INTERVAL = 60

_ENV_SERVICES = "lever_action.session_services"


def get_resource_path() -> Path:
    base = Path(sys.executable).parent
    if getattr(sys, "frozen", False):
        if not (base / "templates").exists():
            return base / "_internal"
        return base
    return Path(__file__).parent / "src" / "lever_action"


def get_pygments_css() -> str:
    from pygments.formatters import HtmlFormatter  # ty: ignore

    formatter = HtmlFormatter(style="monokai", nobackground=True)
    return formatter.get_style_defs()


def markdown_to_html(text: str) -> str:
    import html as html_module

    import markdown
    from pygments import highlight
    from pygments.formatters import HtmlFormatter  # ty: ignore
    from pygments.lexers import TextLexer, get_lexer_by_name  # ty: ignore

    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "nl2br"],
    )

    body = md.reset().convert(text)

    code_blocks: list[tuple[str, str]] = []
    pattern = r'<pre>\s*<code(?: class="language-([\w-]+)")?>(.*?)</code>\s*</pre>'

    def capture_code(m: re.Match) -> str:
        lang = m.group(1)
        code = html_module.unescape(m.group(2))
        placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"

        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()

        formatter = HtmlFormatter(style="monokai", nobackground=True)
        highlighted = highlight(code, lexer, formatter)
        code_blocks.append((placeholder, highlighted))
        return placeholder

    body = re.sub(pattern, capture_code, body, flags=re.DOTALL)
    body = _escape_inline_html(body)

    for placeholder, highlighted in code_blocks:
        body = body.replace(placeholder, highlighted, 1)

    return body


def _escape_inline_html(html: str) -> str:
    import html as html_module

    parts: list[str] = []
    i = 0
    while i < len(html):
        if (
            html[i] == "<"
            and i + 1 < len(html)
            and not html[i + 1].isspace()
            and html[i + 1] != ">"
        ):
            tag_start = i
            tag_end = html.find(">", i)
            if tag_end != -1:
                tag = html[tag_start : tag_end + 1]
                if not _is_safe_markdown_tag(tag):
                    parts.append(html_module.escape(tag))
                else:
                    parts.append(tag)
                i = tag_end + 1
                continue
        parts.append(html[i])
        i += 1
    return "".join(parts)


def _is_safe_markdown_tag(tag: str) -> bool:
    safe_tags = frozenset(
        {
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "br",
            "code",
            "em",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "hr",
            "i",
            "img",
            "li",
            "ol",
            "p",
            "pre",
            "s",
            "span",
            "strong",
            "strike",
            "sub",
            "sup",
            "ul",
            "kbd",
        }
    )
    import re as re_module

    match = re_module.match(r"</?(\w+)", tag, re_module.IGNORECASE)
    if match:
        return match.group(1).lower() in safe_tags
    return False


TEMPLATE_PATH.insert(0, str(get_resource_path() / "templates"))

app = Bottle()

logger.info("Template path: %s", TEMPLATE_PATH)
logger.info("Resource path: %s", get_resource_path())
session_store = SessionStore.get_instance()


@app.error(500)
def handle_500(error: Exception) -> HTTPResponse:
    logger.exception("Unhandled 500 error: %s", error)
    return HTTPResponse(
        body=json.dumps({"error": "internal server error"}),
        status=500,
        content_type="application/json",
    )


@app.error(404)
def handle_404(error: Exception) -> HTTPResponse:
    logger.warning("404: %s", request.path)
    return HTTPResponse(
        body=json.dumps({"error": "not found"}),
        status=404,
        content_type="application/json",
    )


settings_storage = SettingsStorage.get_instance()


@app.route("/settings")
def settings_get() -> HTTPResponse:
    return HTTPResponse(
        body=json.dumps(settings_storage.get_all()),
        status=200,
        content_type="application/json",
    )


@app.route("/settings", method="POST")
def settings_set() -> HTTPResponse:
    body = request.json
    if not body:
        return HTTPResponse(
            body=json.dumps({"error": "invalid json"}),
            status=400,
            content_type="application/json",
        )
    settings_storage.save(body)
    settings_storage.reload()
    import importlib

    import dandy_settings

    importlib.reload(dandy_settings)
    return HTTPResponse(
        body=json.dumps({"ok": True}),
        status=200,
        content_type="application/json",
    )


_per_session_services: dict[str, tuple[ChatService, HistoryStorage]] = {}


def _get_session_token() -> str | None:
    return request.cookies.get("lever_action_session")


def _get_services() -> tuple[ChatService, HistoryStorage]:
    services = request.environ.get(_ENV_SERVICES)
    if services is None:
        raise HTTPResponse(
            body=json.dumps({"error": "unauthorized"}),
            status=401,
            content_type="application/json",
        )
    return services


def _cleanup_session(token: str) -> None:
    _per_session_services.pop(token, None)


def _session_cleanup_loop() -> None:
    while True:
        time.sleep(CLEANUP_INTERVAL)
        expired_tokens = [
            token
            for token, info in session_store._sessions.items()
            if time.time() > info.expires_at
        ]
        for token in expired_tokens:
            session_store.revoke(token)
            _cleanup_session(token)
        if expired_tokens:
            logger.info("Cleaned up %d expired sessions", len(expired_tokens))


@app.hook("before_request")
def load_env() -> None:
    if not getattr(load_env, "_loaded", False):
        env_path = get_resource_path() / "development.env"
        if env_path.exists():
            load_dotenv(env_path)
        load_env._loaded = True  # ty: ignore


@app.hook("before_request")
def check_request_size() -> None:
    content_length = request.content_length
    if content_length is not None and content_length > MAX_REQUEST_SIZE:
        raise HTTPResponse(
            body=json.dumps({"error": "request too large"}),
            status=413,
            content_type="application/json",
        )


@app.hook("before_request")
def ensure_session() -> None:
    if request.path.startswith("/static/"):
        return
    token = _get_session_token()
    if (
        token
        and token in _per_session_services
        and (app.config.get("skip_auth", False) or session_store.verify(token))
    ):
        request.environ[_ENV_SERVICES] = _per_session_services[token]
        return
    if app.config.get("skip_auth", False):
        return
    if token:
        session_store.revoke(token)
        _cleanup_session(token)
    token = session_store.create()
    _per_session_services[token] = (
        ChatService(),
        HistoryStorage(user_id=token),
    )
    request.environ[_ENV_SERVICES] = _per_session_services[token]
    resp = HTTPResponse(status=302)
    resp.set_header("Location", "/")
    resp.set_cookie(
        "lever_action_session",
        token,
        path="/",
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="Lax",
    )
    raise resp


@app.route("/logout", method="POST")
def logout() -> HTTPResponse:
    token = _get_session_token()
    if token:
        session_store.revoke(token)
        _cleanup_session(token)
    resp = HTTPResponse(status=302)
    resp.set_header("Location", "/")
    resp.delete_cookie("lever_action_session", path="/")
    raise resp


@app.route("/static/<filepath:path>")
def serve_static(filepath: str) -> HTTPResponse:
    return static_file(filepath, root=str(get_resource_path() / "static"))


@app.route("/static/css/pygments.css")
def pygments_css() -> HTTPResponse:
    return HTTPResponse(
        body=get_pygments_css(),
        status=200,
        content_type="text/css",
    )


@app.route("/")
def index() -> str:
    return template("index")


@app.route("/chat", method="POST")
def chat() -> HTTPResponse:
    chat_service, history_storage = _get_services()

    body = request.json
    if not body:
        return HTTPResponse(
            body=json.dumps({"error": "invalid json"}),
            status=400,
            content_type="application/json",
        )

    prompt = str(body.get("prompt", "")).strip()
    if not prompt:
        return HTTPResponse(
            body=json.dumps({"error": "prompt is required"}),
            status=400,
            content_type="application/json",
        )

    try:
        current_mode = chat_service.mode.value
        response_intel = chat_service.process(prompt)
        response_text = response_intel.text
        entry = history_storage.add_entry(prompt, response_text)
        return HTTPResponse(
            body=json.dumps(
                {
                    "prompt": prompt,
                    "response": response_text,
                    "response_html": markdown_to_html(response_text),
                    "timestamp": entry.timestamp,
                    "mode": current_mode,
                }
            ),
            status=200,
            content_type="application/json",
        )
    except Exception:
        logger.exception("Chat processing failed")
        logger.debug("Request body: %s", body)
        return HTTPResponse(
            body=json.dumps({"error": "internal server error"}),
            status=500,
            content_type="application/json",
        )


@app.route("/mode")
def mode_get() -> HTTPResponse:
    chat_service = _get_services()[0]
    return HTTPResponse(
        body=json.dumps({"mode": chat_service.mode.value}),
        status=200,
        content_type="application/json",
    )


@app.route("/mode", method="POST")
def mode_set() -> HTTPResponse:
    chat_service = _get_services()[0]

    body = request.json
    if not body:
        return HTTPResponse(
            body=json.dumps({"error": "invalid json"}),
            status=400,
            content_type="application/json",
        )

    mode_value = body.get("mode")
    try:
        mode = ChatMode(mode_value)
    except (ValueError, TypeError):
        return HTTPResponse(
            body=json.dumps({"error": "invalid mode"}),
            status=400,
            content_type="application/json",
        )

    chat_service.set_mode(mode)
    return HTTPResponse(
        body=json.dumps({"mode": mode.value}),
        status=200,
        content_type="application/json",
    )


@app.route("/guideline")
def guideline_get() -> HTTPResponse:
    chat_service = _get_services()[0]
    return HTTPResponse(
        body=json.dumps({"guideline": chat_service.guideline_mode.value}),
        status=200,
        content_type="application/json",
    )


@app.route("/guideline", method="POST")
def guideline_set() -> HTTPResponse:
    chat_service = _get_services()[0]

    body = request.json
    if not body:
        return HTTPResponse(
            body=json.dumps({"error": "invalid json"}),
            status=400,
            content_type="application/json",
        )

    guideline_value = body.get("guideline")
    try:
        guideline = GuidelineMode(guideline_value)
    except (ValueError, TypeError):
        return HTTPResponse(
            body=json.dumps({"error": "invalid guideline"}),
            status=400,
            content_type="application/json",
        )

    chat_service.set_guideline_mode(guideline)
    return HTTPResponse(
        body=json.dumps({"guideline": guideline.value}),
        status=200,
        content_type="application/json",
    )


@app.route("/target")
def target_get() -> HTTPResponse:
    chat_service = _get_services()[0]
    return HTTPResponse(
        body=json.dumps({"target": chat_service.target}),
        status=200,
        content_type="application/json",
    )


@app.route("/target", method="POST")
def target_set() -> HTTPResponse:
    chat_service = _get_services()[0]

    body = request.json
    if not body:
        return HTTPResponse(
            body=json.dumps({"error": "invalid json"}),
            status=400,
            content_type="application/json",
        )

    target_value = str(body.get("target", ""))
    chat_service.set_target(target_value)
    return HTTPResponse(
        body=json.dumps({"target": chat_service.target}),
        status=200,
        content_type="application/json",
    )


@app.route("/history")
def history_list() -> HTTPResponse:
    history_storage = _get_services()[1]
    entries = history_storage.get_all()
    data = [
        {
            "prompt": e.prompt,
            "response": e.response,
            "response_html": markdown_to_html(e.response),
            "timestamp": e.timestamp,
        }
        for e in reversed(entries)
    ]
    return HTTPResponse(
        body=json.dumps(data), status=200, content_type="application/json"
    )


def main() -> None:
    _setup_logging()
    logger.info("Lever Action starting...")

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        host = sys.argv[2]

    cleanup_thread = threading.Thread(target=_session_cleanup_loop, daemon=True)
    cleanup_thread.start()

    server_thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, quiet=True),
        daemon=True,
    )
    server_thread.start()

    os.environ["PYTHONNET_RUNTIME"] = "netfx"
    import webview

    url = f"http://{host}:{port}"
    logger.info("Starting Lever Action at %s", url)

    try:
        webview.create_window(
            "Lever Action",
            url,
            width=960,
            height=720,
            min_size=(640, 480),
            resizable=True,
            zoomable=True,
        )
        webview.start(debug=False, gui="edgechromium")
    except Exception:
        logger.exception("Failed to start webview")
        raise


if __name__ == "__main__":
    main()
