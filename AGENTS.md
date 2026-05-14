# AGENTS.md

## Project: Lever Action
**Native Windows AI chat web app — Aim. Shoot. Reload.**

## Tech Stack
- **Bottle** — web framework (hosted in pywebview window)
- **pywebview** — native wrapper (WebView2 on Windows)
- **Dandy** — AI integration (Bot, Prompt, Intel)
- **PyInstaller** — standalone executable builds
- **pytest** + **webtest** + **pytest-cov** — testing
- **ruff** — formatting and linting
- **uv** — package management
- **just** — task runner

## Architecture

```
main.py                     # Entry, Bottle app, routes, pywebview launcher
dandy_settings.py            # LLM config (reads settings.json + env vars)
src/lever_action/
├── services/chat_service.py # ChatService (modes, guidelines, target)
├── storage/history.py       # HistoryStorage (per-user JSON, singleton)
├── storage/sessions.py      # SessionStore (in-memory, token-based)
├── storage/settings.py      # SettingsStorage (persistent JSON, singleton)
├── templates/index.tpl      # Main HTML page
└── static/                  # CSS (style.css) and JS (app.js)
tests/                       # Mirrors source: test_app.py, test_services/, test_storage/
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `ChatService` | Chat modes, guidelines, target context, Dandy Bot lifecycle |
| `HistoryStorage` | Per-user JSON history storage (singleton) |
| `SessionStore` | In-memory session tokens with expiry (singleton) |
| `SettingsStorage` | Persistent settings JSON with version migration (singleton) |

### Sessions
Per-session `ChatService` + `HistoryStorage` instances are created on first request. Session tokens are stored as `httponly` cookies with 30-day expiry. Background thread cleans expired sessions every 60s. Use `app.config["skip_auth"] = True` in tests.

### API Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main page |
| `/chat` | POST | Process prompt, return response + HTML |
| `/mode` | GET/POST | Get/set chat mode (`fire_and_forget`, `aim_and_ask`) |
| `/guideline` | GET/POST | Get/set guideline (`normal`, `concise`) |
| `/target` | GET/POST | Get/set target context (prepended to every prompt) |
| `/history` | GET | Return all history entries with HTML |
| `/settings` | GET/POST | Get/set LLM config (host, port, api_key, model) |
| `/logout` | POST | Revoke session, redirect to `/` |
| `/static/*` | GET | Static files (CSS, JS) |
| `/static/css/pygments.css` | GET | Generated Pygments CSS |

## Coding Conventions

### Python
- Type hints on all function signatures
- `from __future__ import annotations` in every module
- `StrEnum` for choice enums (`ChatMode`, `GuidelineMode`)
- f-strings for formatting; no inline comments unless non-obvious
- PEP 8 + ruff rules (see `pyproject.toml`)

### Bottle
- Routes handle HTTP only — no business logic
- `markdown_to_html()` and `get_pygments_css()` are module-level in `main.py`
- API endpoints return `HTTPResponse` with JSON body
- Bottle runs in a background thread; pywebview hosts the window

### Dandy
- **Fire & Forget**: each `process()` creates a new `Bot()` instance
- **Aim & Ask**: persistent `Bot()` instance maintained by `ChatService`
- Switching fire-and-forget → aim-and-ask seeds the bot with last exchange
- Settings loaded from `~/.config/lever_action/settings.json` or bundled `settings.json`

### JavaScript
- Global functions, no module wrapper
- `fetch()` for all async calls; `escapeHtml()` for user input
- Initialized via `DOMContentLoaded` listener in `app.js`
- `lastResponseText` tracks last response for clipboard copy

## Hot Keys

| Shortcut | Action |
|----------|--------|
| `Enter` | Send prompt |
| `Shift + Enter` | New line in prompt |
| `Ctrl + Enter` | Toggle mode (Fire & Forget / Aim & Ask) |
| `Ctrl + Shift + Enter` | Toggle guideline (Steady / Quick) |
| `Ctrl + Alt + Enter` | Open target modal |
| `Ctrl + Shift + C` | Copy last response to clipboard |
| `Ctrl + ,` | Open settings |
| `Ctrl + R` | Reset chat |
| `Escape` | Close modals |
| `Ctrl + Up/Down` | Scroll messages (while typing) |
| `Arrow Up/Down` | Navigate prompt history (when typing) / Scroll messages (when focused) |
| `Page Up/Down` | Scroll messages by page (when focused) |

## Chat Modes & Guidelines

| Mode | Behavior |
|------|----------|
| `fire_and_forget` | Fresh Bot each call. Last exchange cached for aim-and-ask seed. |
| `aim_and_ask` | Persistent Bot with conversation history. |

| Guideline | Behavior |
|-----------|----------|
| `normal` | Standard responses with code formatting guidelines. |
| `concise` | Short, direct answers + code formatting guidelines. |

Target context (optional) is prepended as `[Context: {target}]` to every prompt.

## Task Runner (just)
**ALWAYS use `just` commands** — never run pytest, ruff, or python directly.

| Command | Purpose |
|---------|---------|
| `just run` | Run the application (development) |
| `just test` | Run all 89 tests (verbose) |
| `just test-coverage` | Tests with coverage report (services, storage) |
| `just fmt` | Format and lint with ruff |
| `just lint` | Lint only (no fixes) |
| `just clean` | Clear pytest and ruff caches |
| `just prod` | Run with pywebview (production window) |
| `just package` | Build executable with PyInstaller |
| `just exe` | Run built executable |
| `just msix` | Create MSIX package (requires `just package` first) |
| `just msi` | Create Inno Setup MSI installer (requires `just package` first) |
| `just release` | Package, tag, build installer, push to GitHub |

## Task Completion Checklist

1. **`just test`** — All 89 tests must pass
2. **`just fmt`** — ruff format + check must pass
3. **`just package`** — Build executable (MANDATORY — old exe won't have your changes)
4. **`just exe`** — Optional: verify the built executable

## Rules
- **NEVER skip `just package`** — the executable must be rebuilt after every code change
- **NEVER run tools directly** — always use `just` commands
- **DO NOT commit `.env` files** — they're in `.gitignore`

## What NOT To Do
- Don't carry conversation history in fire-and-forget mode
- Don't block the request thread on API calls
- Don't hardcode API keys — use settings or env vars
- Don't put business logic in Bottle routes
- Don't create new modules without good reason (YAGNI)
- Don't use inline imports where lazy imports suffice
