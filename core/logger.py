# core/logger.py
import os
from core.utils import LOG_PATH, timestamp

def ensure_log():
    d = os.path.dirname(LOG_PATH)
    os.makedirs(d, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "w", encoding="utf-8").close()

def log(event):
    try:
        ensure_log()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp()}] {event}\n")
    except Exception:
        pass
