# core/stats.py
from core.database import load_records

def summary():
    recs = load_records()
    return {
        "total": len(recs)
    }
