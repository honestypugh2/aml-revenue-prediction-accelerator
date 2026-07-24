"""Layered configuration loading (base YAML -> env YAML -> env vars)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import Settings


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into ``base`` and return the result."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config file {path} must contain a mapping at the top level")
    return loaded


def load_settings(
    environment: str | None = None,
    configs_dir: str | Path = "configs",
) -> Settings:
    """Load :class:`Settings` for the requested environment.

    Precedence (lowest to highest): base YAML, environment YAML, environment
    variables / ``.env``. Environment variables always win so that secrets and
    cloud identifiers never need to live in files.
    """
    configs_path = Path(configs_dir)

    # Determine environment from explicit arg or env var, defaulting to dev.
    import os

    env = environment or os.environ.get("RPA_ENVIRONMENT", "dev")

    base = _read_yaml(configs_path / "base" / "config.yaml")
    env_specific = _read_yaml(configs_path / env / "config.yaml")
    merged = _deep_merge(base, env_specific)
    merged.setdefault("environment", env)

    # Settings() applies environment variables on top of the file-provided data.
    return Settings(**merged)
