import json
import os
from pathlib import Path

CONFIG_FILE = "config.json"
DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = ""


def config_dir():
    return Path(os.environ.get("PROMPTV_CONFIG_DIR", Path.home() / ".config" / "promptv"))


def data_dir():
    return Path(os.environ.get("PROMPTV_DATA_DIR", Path.home() / ".local" / "share" / "promptv"))


def default_config():
    return {
        "default_endpoint": os.environ.get("PROMPTV_DEFAULT_ENDPOINT", DEFAULT_ENDPOINT),
        "default_model": os.environ.get("PROMPTV_DEFAULT_MODEL", DEFAULT_MODEL),
        "data_dir": str(data_dir()),
    }


def load_config():
    path = config_dir() / CONFIG_FILE
    if not path.exists():
        return default_config()
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    result = default_config()
    result.update(config)
    return result


def save_config(config):
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / CONFIG_FILE
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    return path
