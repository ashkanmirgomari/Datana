import json, os
from core.utils import DATA_DIR

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

DEFAULT = {
    "timeout": 300,
    "autosave": True
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT, f, indent=2)
        return DEFAULT

def set_config(key, value):
    cfg = load_config()
    cfg[key] = value
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg
