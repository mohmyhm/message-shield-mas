"""Configuration loading utilities."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def load_runtime_policy(path: str | Path = "configs/runtime_policy.yaml") -> dict[str, Any]:
    return load_yaml(path)


def load_attack_config(path: str | Path = "configs/attacks.yaml") -> dict[str, Any]:
    return load_yaml(path)


def load_task_config(path: str | Path = "configs/tasks.yaml") -> dict[str, Any]:
    return load_yaml(path)
