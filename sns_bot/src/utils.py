import json
import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger("sns-bot")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_yaml(filename: str) -> dict:
    path = CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_settings() -> dict:
    return load_yaml("settings.yaml")


def load_templates() -> dict:
    return load_yaml("templates_x.yaml")


def load_blocked_keywords() -> list[str]:
    data = load_yaml("blocked_keywords.yaml")
    return data.get("blocked_keywords", [])


def load_json(filename: str) -> list:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: list):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_dry_run() -> bool:
    env_override = os.environ.get("DRY_RUN")
    if env_override is not None:
        return env_override.lower() in ("true", "1", "yes")
    settings = load_settings()
    return settings.get("general", {}).get("dry_run", True)
