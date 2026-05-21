"""Utility: load and cache game config JSON files."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).parent.parent / "config"
_cache: dict[str, Any] = {}


def load_config(name: str, use_cache: bool = True) -> Any:
    """Load a JSON config file from config/{name}.json.

    Args:
        name: Filename without extension (e.g. "expeditions").
        use_cache: Return cached version if available.

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        FileNotFoundError: If config file does not exist.
        json.JSONDecodeError: If file contains invalid JSON.
    """
    if use_cache and name in _cache:
        return _cache[name]

    config_path = _CONFIG_DIR / f"{name}.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Config not found: config/{name}.json")

    with open(config_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if use_cache:
        _cache[name] = data

    return data


def reload_config(name: str | None = None) -> None:
    """Clear cached config(s) to force reload from disk.

    Args:
        name: Specific config to reload, or None to clear all.
    """
    if name:
        _cache.pop(name, None)
    else:
        _cache.clear()
