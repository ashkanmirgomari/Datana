# core/time_utils.py
from datetime import datetime
import pytz

class TimeSystem:
    @staticmethod
    def get_current_time(timezone=None):
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            except:
                return "Invalid timezone"
        
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_system_uptime():
        import psutil
        import time
        
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return f"{days}d {hours}h {minutes}m"
    
    @staticmethod
    def get_timezones():
        return [
            "Asia/Tehran",
            "UTC", 
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney"
        ]