# core/config_manager.py
import os
import json
from cryptography.fernet import Fernet
from core.utils import DATA_DIR

CONFIG_FILE = os.path.join(DATA_DIR, "datana_config.json")

def get_or_create_config():
    """دریافت یا ساخت config خودکار"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # اگر config قدیمی هست، فیلد autobackup رو اضافه کن
            if "autobackup" not in config:
                config["autobackup"] = {
                    "enabled": False,
                    "mode": "daily",
                    "last_backup": None
                }
                # ذخیره config آپدیت شده
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                    
            return config
        except:
            # اگر فایل config خراب بود، از اول می‌سازیم
            pass
    
    # ساخت config جدید
    new_key = Fernet.generate_key().decode()
    config = {
        "DATANA_KEY": new_key,
        "version": "1.0.0",
        "auto_generated": True,
        "autobackup": {
            "enabled": False,
            "mode": "daily",
            "last_backup": None
        }
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Could not save config: {e}")
    
    return config

def get_encryption_key():
    """دریافت کلید رمزگذاری از config"""
    config = get_or_create_config()
    return config["DATANA_KEY"].encode()

def show_key_info():
    """نمایش اطلاعات کلید برای کاربر"""
    config = get_or_create_config()
    return config["DATANA_KEY"]

def update_autobackup_config(enabled=None, mode=None):
    """آپدیت تنظیمات autobackup"""
    config = get_or_create_config()
    
    if enabled is not None:
        config["autobackup"]["enabled"] = enabled
    if mode is not None:
        config["autobackup"]["mode"] = mode
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def get_autobackup_config():
    """دریافت تنظیمات autobackup"""
    config = get_or_create_config()
    return config["autobackup"]

def set_last_backup_time():
    """ذخیره زمان آخرین بک‌آپ"""
    from datetime import datetime
    config = get_or_create_config()
    config["autobackup"]["last_backup"] = datetime.now().isoformat()
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error updating last backup time: {e}")
        return False