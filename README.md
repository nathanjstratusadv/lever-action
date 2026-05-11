# Lever Action

**Aim. Shoot. Reload.**

Lever Action is a native Windows AI chat app built with the personality of a lever-action rifle — fast, precise, and refreshingly simple.

---

## Features

| Feature | Description |
|---------|-------------|
| **Fire & Forget** | Every prompt is a fresh shot. No memory, no baggage. |
| **Aim & Ask** | Persistent conversation mode for iterative work. |
| **Steady / Quick** | Toggle between full responses and concise answers. |
| **Target Context** | Pin persistent context that prepends to every prompt. |
| **Chat History** | All exchanges saved to JSON — review past shots anytime. |
| **Markdown + Syntax Highlighting** | Code blocks rendered in Monokai style via Pygments. |
| **Settings Modal** | Configure your LLM host, port, API key, and model in-app. |
| **Keyboard Shortcuts** | `Ctrl+Enter` send, `Ctrl+T` toggle mode, `Ctrl+,` settings, and more. |

---

## Quick Start

```bash
uv sync
just run
```

A native Windows window opens. Configure your API settings on first launch. Done.

---

## Configuration

Settings are managed through the in-app Settings modal and persisted to `~/.config/lever_action/settings.json`:

```json
{
    "host": "api.anthropic.com",
    "port": 443,
    "api_key": "sk-your-key-here",
    "model": "claude-sonnet-4-20250514"
}
```

A bundled `settings.json` ships with the app as a fallback. OpenAI-compatible APIs (OpenAI, Azure, LM Studio, etc.) are all supported.

---

## Task Runner

Everything runs through `just`. Never run tools directly.

| Command | Purpose |
|---------|---------|
| `just run` | Development server |
| `just prod` | Production pywebview window |
| `just test` | Run all 89 tests |
| `just test-coverage` | Tests with coverage report |
| `just fmt` | Format and lint with ruff |
| `just lint` | Lint only |
| `just clean` | Clear caches |
| `just package` | Build standalone executable |
| `just exe` | Run built executable |
| `just msix` | Windows Store package |
| `just msi` | Inno Setup MSI installer |
| `just release` | Full release pipeline |

---

## Packaging

```bash
just package    # Standalone .exe in dist/lever_action/
just msix       # Windows Store package
just msi        # MSI installer
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send prompt |
| `Ctrl + Enter` | Toggle mode |
| `Ctrl + Shift + Enter` | Toggle guideline |
| `Ctrl + Alt + Enter` | Open target modal |
| `Ctrl + ,` | Open settings |
| `Escape` | Close modals |
| `Arrow Up/Down` | Scroll messages |

---

## Tech Stack

Bottle · pywebview · Dandy · PyInstaller · pytest · ruff · uv · just

---

## License

MIT

---

*"With great power comes great responsibility. With Lever Action comes great satisfaction."*
