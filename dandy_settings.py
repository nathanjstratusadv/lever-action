from __future__ import annotations

import json
import os
from pathlib import Path

BASE_PATH = Path(__file__).parent.resolve()

_SETTINGS: dict | None = None


def _load_settings() -> dict:
    global _SETTINGS
    if _SETTINGS is None:
        settings_path = BASE_PATH / "settings.json"
        if settings_path.exists():
            try:
                with open(settings_path, encoding="utf-8") as f:
                    _SETTINGS = json.load(f)
            except (json.JSONDecodeError, OSError):
                _SETTINGS = {}
        else:
            _SETTINGS = {}
    return _SETTINGS


def _get_setting(key: str, env_var: str, default: str) -> str:
    env_val = os.getenv(env_var)
    if env_val:
        return env_val
    settings = _load_settings()
    return settings.get(key, default)


LLM_CONFIGS: dict[str, dict[str, str | int | None]] = {
    "DEFAULT": {
        "HOST": _get_setting(
            "openai_base_url",
            "OPENAI_HOST",
            "https://api.openai.com",
        ),
        "PORT": int(os.getenv("OPENAI_PORT", "443")),
        "API_KEY": os.getenv("OPENAI_API_KEY")
        or _load_settings().get("openai_api_key"),
        "MODEL": _get_setting(
            "openai_model",
            "OPENAI_MODEL",
            "gpt-4o-mini",
        ),
    }
}
