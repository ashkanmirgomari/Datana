import os
from datetime import datetime, timedelta
from core.database import create_backup, get_available_backups
from core.config_manager import get_autobackup_config, set_last_backup_time, update_autobackup_config
from core.logger import log

def should_run_backup():
    config = get_autobackup_config()
    
    if not config["enabled"]:
        return False
    
    last_backup = config.get("last_backup")
    if not last_backup:
        return True
    
    try:
        last_backup_time = datetime.fromisoformat(last_backup)
        now = datetime.now()
        
        if config["mode"] == "daily":
            return (now - last_backup_time) >= timedelta(days=1)
        elif config["mode"] == "weekly":
            return (now - last_backup_time) >= timedelta(days=7)
        else:
            return False
    except Exception:
        return True

def run_autobackup():
    if not should_run_backup():
        return False
    
    try:
        backup_path = create_backup()
        
        if backup_path:
            set_last_backup_time()
            log(f"AUTOBACKUP: automatic backup created - {backup_path}")
            return True
        else:
            log("AUTOBACKUP: automatic backup failed")
            return False
            
    except Exception as e:
        log(f"AUTOBACKUP ERROR: {e}")
        return False

def autobackup_status():
    config = get_autobackup_config()
    status = "Enabled" if config["enabled"] else "Disabled"
    mode = config["mode"].capitalize()
    
    last_backup = config.get("last_backup")
    if last_backup:
        try:
            last_time = datetime.fromisoformat(last_backup).strftime("%Y-%m-%d %H:%M:%S")
        except:
            last_time = "Unknown"
    else:
        last_time = "Never"
    
    return {
        "status": status,
        "mode": mode,
        "last_backup": last_time,
        "next_backup": calculate_next_backup(config)
    }


def calculate_next_backup(config):
    if not config["enabled"]:
        return "N/A"
    
    last_backup = config.get("last_backup")
    if not last_backup:
        return "Soon"
    
    try:
        last_backup_time = datetime.fromisoformat(last_backup)
        now = datetime.now()
        
        if config["mode"] == "daily":
            next_backup = last_backup_time + timedelta(days=1)
        elif config["mode"] == "weekly":
            next_backup = last_backup_time + timedelta(days=7)
        else:
            return "Unknown"
        
        if next_backup <= now:
            return "Due now"
        else:
            return next_backup.strftime("%Y-%m-%d %H:%M")
            
    except Exception:
        return "Unknown"