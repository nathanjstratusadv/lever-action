# AGENTS.md

## Project: Lever Action
**Native Windows AI chat web app — Aim. Shoot. Reload.**

## Tech Stack
- **Python** — All code follows PEP 8, uses `StrEnum` for choices
- **Bottle** — Lightweight web framework for routing and serving (hosted by pywebview)
- **pywebview** — Native window wrapper (WebView2 on Windows) for desktop deployment
- **PyInstaller** — Bundles Python app to standalone executable
- **MSIX/MakeAppx** — Windows Store packaging format
- **Dandy** — AI integration (Bot, Prompt, Intel)
- **markdown** + **pygments** — Markdown to HTML conversion with syntax highlighting
- **JavaScript** (vanilla, module pattern) — Client-side UI logic
- **CSS** — Styling (no frameworks)
- **pytest** + **pytest-cov** + **webtest** — Testing and coverage
- **ruff** — Formatting and linting (configured in `pyproject.toml`)
- **uv** — Package management
- **just** — Task runner

## Architecture

The project follows clean architecture principles with clear separation of concerns:

```
lever_action/
├── main.py                    # Entry point, Bottle app, routes, pywebview launcher
├── src/lever_action/          # Source package
│   ├── services/               # Business logic (chat_service)
│   ├── storage/                 # Data persistence (history, sessions)
│   ├── templates/               # Bottle templates
│   └── static/                  # CSS and JS
└── tests/                      # Mirrored test structure
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `src/lever_action/services/chat_service.py` | `ChatService` (modes), `BotManager` (bot lifecycle) |
| `src/lever_action/storage/history.py` | `HistoryStorage` (thread-safe singleton), `ChatEntry` |
| `src/lever_action/storage/sessions.py` | `SessionStore` (in-memory session management) |

### Design Principles Applied

- **KISS**: Simple, focused modules with single responsibilities
- **DRY**: Shared utilities reduce duplication
- **SRP**: Each module/class does one thing well
- **OCP**: Services are injectable
- **DIP**: Routes depend on abstractions (services), not concrete implementations

## Coding Conventions

### Python
- Type hints on all function signatures
- f-strings for string formatting
- No inline comments unless explaining non-obvious logic
- Follow PEP 8 and ruff rules (configured in `pyproject.toml`)
- Use `from __future__ import annotations` in all modules
- Use `StrEnum` for choice enums (`ChatMode`, `GuidelineMode`)

### Bottle
- Routes in `main.py` handle HTTP requests/responses only — no business logic
- `ChatService`, `HistoryStorage` contain all business logic
- `markdown_to_html()` and `get_pygments_css()` live in `main.py` as module-level functions
- Bottle dev server (`app.run()`) runs in a background thread; pywebview hosts the window
- All routes use `HTTPResponse` with JSON body for API endpoints

### Dandy
- **Fire & Forget** mode: each `process()` call creates a **new** `Bot()` instance
- **Aim & Ask** mode: `BotManager` maintains a persistent `Bot()` instance
- Switching from fire-and-forget to aim-and-ask seeds the new bot with the last exchange
- `ChatResult` dataclass wraps `response_intel.text` and `mode`
- Settings live in `dandy_settings.py` at project root

### JavaScript
- Vanilla JS using the Revealing Module pattern — `LeverUI` object exposes API
- All async calls use `fetch()` with proper error handling
- DOM manipulation is minimal and focused on message rendering
- `escapeHtml()` used for user input to prevent XSS
- Initialized via `LeverUI.init()` on `DOMContentLoaded`

### Environment & Config
- `development.env` — Local env vars (API keys, hosts), loaded via `python-dotenv`
- `dandy_settings.py` — Reads from env vars, provides `LLM_CONFIGS` dict
- Never commit `.env` files — they're in `.gitignore`

### File Structure
```
lever_action/
├── main.py                     # Entry point, Bottle app, routes, pywebview launcher
├── dandy_settings.py            # Dandy LLM config
├── lever_action.spec            # PyInstaller packaging spec
├── AppxManifest.xml             # MSIX manifest for Windows Store
├── pyproject.toml               # uv dependencies, pytest, ruff config
├── justfile                     # Task runner
├── .gitignore                   # Python, .env, IDE, build artifacts
├── src/lever_action/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── chat_service.py      # ChatService, BotManager, ChatMode, GuidelineMode
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── history.py           # HistoryStorage (thread-safe singleton), ChatEntry
│   │   ├── sessions.py           # SessionStore (in-memory session management)
│   │   └── settings.py          # SettingsStorage (persistent settings)
│   ├── templates/
│   │   └── index.tpl             # Main HTML page
│   └── static/
│       ├── css/
│       │   └── style.css         # Application styles
│       └── js/
│           └── app.js             # Client-side UI logic (module pattern)
└── tests/
    ├── __init__.py
    ├── test_app.py               # Integration tests (webtest)
    ├── test_services/
    │   ├── __init__.py
    │   └── test_chat_service.py
    └── test_storage/
        ├── __init__.py
        ├── test_chat_entry.py
        ├── test_history.py
        ├── test_sessions.py
        └── test_settings.py
```

### Task Runner (just)
**ALWAYS use `just` commands instead of running tools directly.** This ensures consistent cleanup, environment loading, and build behavior.
- `just run` — Run the application (development)
- `just test` — Run all tests with verbose output
- `just test-coverage` — Run tests with coverage report (storage, services)
- `just fmt` — Format and lint with ruff
- `just lint` — Lint only (check without fixing)
- `just clean` — Clear pytest and ruff caches
- `just prod` — Run with pywebview (production window)
- `just package` — Build standalone executable with PyInstaller
- `just exe` — Run the built executable from `dist/lever_action/lever_action.exe`
- `just msix` — Create MSIX package for Windows Store (requires `just package` first)

### Testing
- Use pytest, configured in `pyproject.toml` under `[tool.pytest.ini_options]`
- Use `webtest` for integration tests against the Bottle app
- Mock Dandy calls — never hit the API in tests
- Place tests in `tests/` mirroring source structure (`test_services/`, `test_storage/`)
- `test_app.py` covers route-level integration with mocked service layer
- Target: 100% coverage on services and storage
- `main.py` routes are tested via webtest; `ChatService` unit tested in isolation
- Use `app.config["skip_auth"] = True` in tests for auth control

## Task Completion Checklist

**Every task must follow this sequence. IN ORDER. Do not skip any step. Do not skip `just package`.**

### Step 1: Run Tests
```
just test
```
All 79 tests must pass. If any fail, fix them before proceeding.

### Step 2: Lint
```
just fmt
```
Format and lint with ruff. All checks must pass.

### Step 3: BUILD THE EXECUTABLE
```
just package
```
**THIS STEP IS MANDATORY. IT IS NEVER OPTIONAL. IT MUST ALWAYS RUN.**

After running `just package`, verify the build succeeds. Look for:
```
6867 INFO: Building EXE completed successfully.
```

**CRITICAL**: If you do not run `just package`, the executable in `dist/lever_action/` will be stale/outdated. Users who download or run the old executable will not see your changes. You MUST rebuild the executable after every code change.

### Step 4: Verify (optional but recommended)
Run the executable to spot-check:
```
just exe
```

## Rules

- **ALWAYS use `just` commands** — never run pytest, ruff, or python directly. The justfile handles cleanup, environment loading, and build behavior.
- **ALWAYS run `just package`** after completing any code change — the executable must be rebuilt. This is non-negotiable.
- **NEVER skip `just package`** — the old executable will not have your changes.
- **NEVER mark a task complete until `just package` succeeds** — if the build fails, fix it.
- **DO NOT run `just test` or `just fmt` as a substitute for `just package`** — they are not interchangeable.

## What NOT To Do
- Don't carry conversation history between submits in fire-and-forget mode — each submit is fresh
- Don't block the request thread on API calls — always use the thread pool executor
- Don't hardcode API keys — use `dandy_settings.py` or env vars
- Don't put business logic in Bottle routes — keep it in `services/` or `storage/`
- Don't create new modules without good reason — follow YAGNI
- Don't add features outside the plan without discussion
- Don't use inline imports where lazy imports suffice (e.g., `markdown_to_html()` handles its own imports)