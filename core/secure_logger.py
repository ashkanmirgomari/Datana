# core/secure_logger.py
import os
import hashlib
import hmac
from core.utils import LOG_PATH, timestamp
from core.config_manager import get_encryption_key

class SecureLogger:
    
    @staticmethod
    def ensure_secure_log():
        log_dir = os.path.dirname(LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)
        
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, 'w', encoding='utf-8') as f:
                f.write(f"[{timestamp()}] SECURE_LOG: Log system initialized\n")
    
    @staticmethod
    def calculate_log_hash():

        if not os.path.exists(LOG_PATH):
            return None
        
        try:
            with open(LOG_PATH, 'rb') as f:
                content = f.read()
            
            #HMAC Encryption
            key = get_encryption_key()
            log_hash = hmac.new(key, content, hashlib.sha256).hexdigest()
            return log_hash
        except Exception:
            return None
    
    @staticmethod
    def secure_log(event):
        try:
            SecureLogger.ensure_secure_log()
            
            current_hash = SecureLogger.calculate_log_hash()
            
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp()}] {event}\n")
            
            new_hash = SecureLogger.calculate_log_hash()
            
            if current_hash and current_hash != new_hash:
                with open(LOG_PATH, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp()}] SECURITY_ALERT: Log file integrity compromised\n")
            
        except Exception as e:

            pass
    
    @staticmethod
    def verify_log_integrity():
        if not os.path.exists(LOG_PATH):
            return True, "Log file doesn't exist"
        
        try:
            current_hash = SecureLogger.calculate_log_hash()
            
            with open(LOG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines and 'SECURITY_ALERT' in lines[-1]:
                    return False, "Log integrity compromised - security alert detected"
            
            return True, "Log integrity verified"
            
        except Exception as e:
            return False, f"Integrity check failed: {e}"
    
    @staticmethod
    def get_log_stats():
        if not os.path.exists(LOG_PATH):
            return {"size": 0, "lines": 0, "integrity": "No log file"}
        
        try:
            size = os.path.getsize(LOG_PATH)
            with open(LOG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            integrity_status, integrity_msg = SecureLogger.verify_log_integrity()
            
            return {
                "size": f"{size / 1024:.1f} KB",
                "lines": len(lines),
                "integrity": integrity_msg,
                "last_entry": lines[-1].strip() if lines else "No entries"
            }
        except Exception:
            return {"size": "Unknown", "lines": 0, "integrity": "Error reading log"}