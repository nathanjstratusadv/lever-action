# Lever Action

### Aim. Shoot. Reload.

**Lever Action** is a native Windows AI chat web app with the personality of a lever-action rifle — and about as much patience for small talk.

Every message you fire off is a fresh shot. No lingering context. No "remember when we talked about..." nonsense. Just you, your prompt, and whatever the AI decides to spit back at you.

> *"I don't know what your problem is, but I'll solve it in one round."*

---

## How It Works (In 3 Steps, Obviously)

| Step | What You Do | What Happens |
|------|-------------|--------------|
| **Aim** | Type your prompt into the input field | The app waits, coiled and ready |
| **Shoot** | Hit send | A brand-new `Bot()` instance processes your prompt and fires back a response |
| **Reload** | Input clears automatically | Chamber another round and do it again |

It's the chat equivalent of a satisfying *click-clack* — clean, precise, repeatable.

---

## Features

### Fire & Forget Mode
The default. Every submit is a clean slate. The AI has amnesia, and that's the point.

### Aim & Ask Mode
Toggle it when you actually want the AI to remember what you said five seconds ago. Switch back whenever you change your mind.

### Concise Mode
For when you want answers shorter than a screenplay. Toggle short, direct responses — no essay writing, no fluff.

### Chat History
All your past shots are saved to JSON. Click to review. No continuing conversations — this isn't therapy.

### Markdown + Syntax Highlighting
Responses render beautifully with full Markdown support. Code blocks get highlighted with Pygments in Monokai style because who reads plain text?

### OpenAI-Compatible
Works with OpenAI, Azure, LM Studio, or anything else that speaks the OpenAI protocol. Bring your own API key, bring your own problems.

### Security Headers
Production deployments get CSP, X-Frame-Options, and other security headers for defense in depth.

---

## Tech Stack

Built with tools that don't take themselves too seriously:

- **Bottle** — Because sometimes you just want a web framework that doesn't need a PhD to configure
- **pywebview** — Native Windows window wrapper (WebView2) for desktop deployment
- **Dandy** — The AI integration layer (Bot, Prompt, Intel)
- **Python-Markdown + Pygments** — For making code look pretty
- **Vanilla JS + CSS** — No frameworks. No dependencies. No excuses.
- **PyInstaller + MSIX** — Packaging for standalone exe and Windows Store
- **uv + just** — Package management and task running that actually works

---

## Quick Start

```bash
# Install dependencies
uv sync

# Point the barrel
just run
```

The app opens a native Windows window. No browser needed.

---

## Configuration

Create a `development.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_HOST=https://api.openai.com
OPENAI_PORT=443
OPENAI_MODEL=gpt-4o-mini
ACCESS_KEY=your-secret-access-key
LEVER_SECRET_KEY=something-not-guessable
LEVER_LOG_LEVEL=INFO
LEVER_DATA_DIR=~/lever_action
```

The app reads these through `dandy_settings.py` and `python-dotenv`. Never commit your `.env` file.

---

## Packaging

### Standalone Executable

```bash
just package
```

Builds a standalone `LeverAction.exe` with PyInstaller. Find it in `dist/LeverAction/`.

### Windows Store (MSIX)

```bash
just package
just msix
```

Creates `lever_action.msix` for Windows Store submission. Requires `just package` first and `MakeAppx.exe` (included with Windows SDK).

---

## Task Runner

Everything runs through `just`. If you're typing `python`, `pytest`, or `ruff` directly, you're doing it wrong.

```bash
just run              # Launch the app (development)
just prod             # Launch with pywebview (production window)
just test             # Run tests
just test-coverage    # Run tests with coverage report
just fmt              # Format and lint with ruff
just lint             # Lint only (no formatting)
just clean            # Clear pytest and ruff caches
just package          # Build standalone executable with PyInstaller
just msix             # Create MSIX package for Windows Store
```

---

## Project Structure

```
lever_action/
├── main.py                     # Entry point, Bottle app, routes, pywebview launcher
├── dandy_settings.py           # LLM configuration
├── lever_action.spec           # PyInstaller packaging spec
├── AppxManifest.xml             # MSIX manifest for Windows Store
├── pyproject.toml               # uv project config, pytest, ruff
├── justfile                     # Task runner recipes
├── src/lever_action/
│   ├── services/                # Business logic
│   │   └── chat_service.py       # ChatService, BotManager, modes
│   ├── storage/                 # Data persistence
│   │   ├── history.py            # HistoryStorage, ChatEntry
│   │   ├── sessions.py           # SessionStore
│   │   └── settings.py           # SettingsStorage
│   ├── templates/               # Bottle templates
│   │   └── index.tpl             # Main HTML page
│   └── static/                  # Static assets
│       ├── css/style.css         # Application styles
│       └── js/app.js             # Client-side UI logic
└── tests/                       # Mirrored test structure
    ├── test_app.py
    ├── test_services/
    │   └── test_chat_service.py
    └── test_storage/
        ├── test_chat_entry.py
        ├── test_history.py
        ├── test_sessions.py
        └── test_settings.py
```

---

## Architecture Notes

Lever Action follows clean architecture with clear separation of concerns:

- **Thin Routes**: `main.py` routes handle HTTP only; business logic lives in services/storage
- **Thread-Safe Storage**: `HistoryStorage` uses double-checked locking singleton
- **Bot Lifecycle**: `BotManager` abstracts `Bot()` instance creation and reuse
- **Native Desktop**: Bottle dev server runs in a background thread; pywebview hosts the native window

---

## License

MIT — Do whatever you want with it. Just don't blame us when the AI gets philosophical.

---

*"With great power comes great responsibility. With Lever Action comes great satisfaction."*