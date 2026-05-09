from __future__ import annotations

import json
from pathlib import Path

BASE_PATH = Path(__file__).parent.resolve()

_SETTINGS_PATH = BASE_PATH / "settings.json"


def _load_llm_settings() -> dict:
    if _SETTINGS_PATH.exists():
        try:
            with open(_SETTINGS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_llm_configs() -> dict[str, dict[str, str | int | None]]:
    settings = _load_llm_settings()
    return {
        "DEFAULT": {
            "HOST": settings.get("host", "api.openai.com"),
            "PORT": int(settings.get("port", 443)),
            "API_KEY": settings.get("api_key"),
            "MODEL": settings.get("model", "gpt-4o-mini"),
        },
    }


LLM_CONFIGS = get_llm_configs()
