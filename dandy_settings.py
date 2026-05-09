from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_PATH = Path(__file__).parent.resolve()


def _get_config_settings_path() -> Path:
    return Path.home() / ".config" / "lever_action" / "settings.json"


def _get_bundled_settings_path() -> Path | None:
    exe_dir = Path(sys.executable).parent
    if getattr(sys, "frozen", False):
        base = (
            exe_dir / "_internal" if not (exe_dir / "templates").exists() else exe_dir
        )
    else:
        base = BASE_PATH
    path = base / "settings.json"
    return path if path.exists() else None


def _load_llm_settings() -> dict:
    config_path = _get_config_settings_path()
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    bundled = _get_bundled_settings_path()
    if bundled:
        try:
            with open(bundled, encoding="utf-8") as f:
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
