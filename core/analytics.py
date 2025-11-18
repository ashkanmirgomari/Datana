from core.database import load_records
from core.auth import load_users
from core.config_manager import get_autobackup_config
from core.utils import LOG_PATH, BACKUP_DIR
from datetime import datetime, timedelta
import os
import json

class Analytics:
    
    @staticmethod
    def user_activity_report():
        users = load_users()
        records = load_records()
        
        report = {
            "total_users": len(users),
            "total_records": len(records),
            "users_by_role": {},
            "recent_activity": "Coming soon"
        }
        
        for user_data in users.values():
            role = user_data.get('role', 'viewer')
            report["users_by_role"][role] = report["users_by_role"].get(role, 0) + 1
        
        return report
    
    @staticmethod
    def data_quality_report():
        records = load_records()
        
        if not records:
            return {"error": "No records available"}
        
        report = {
            "total_records": len(records),
            "completeness": {},
            "validity": {}
        }
        
        fields_to_check = ['first_name', 'last_name', 'national_id', 'phone', 'address']
        for field in fields_to_check:
            filled_count = sum(1 for record in records if record.get(field))
            percentage = (filled_count / len(records)) * 100
            report["completeness"][field] = f"{percentage:.1f}% ({filled_count}/{len(records)})"
        
        from core.validators import DataValidator
        
        valid_national_ids = 0
        valid_phones = 0
        
        for record in records:
            if record.get('national_id'):
                is_valid, _ = DataValidator.validate_national_id(record['national_id'])
                if is_valid:
                    valid_national_ids += 1
            
            if record.get('phone'):
                is_valid, _ = DataValidator.validate_iranian_phone(record['phone'])
                if is_valid:
                    valid_phones += 1
        
        report["validity"]["national_ids"] = f"{valid_national_ids} valid"
        report["validity"]["phones"] = f"{valid_phones} valid"
        
        return report
    
    @staticmethod
    def system_status_report():
        records = load_records()
        backup_config = get_autobackup_config()
        
        records_size = os.path.getsize(os.path.join(os.path.dirname(__file__), '..', 'data', 'records.enc')) if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'data', 'records.enc')) else 0
        logs_size = os.path.getsize(LOG_PATH) if os.path.exists(LOG_PATH) else 0
        
        backup_size = 0
        if os.path.exists(BACKUP_DIR):
            for file in os.listdir(BACKUP_DIR):
                if file.startswith('backup_') and file.endswith('.enc'):
                    backup_size += os.path.getsize(os.path.join(BACKUP_DIR, file))
        
        report = {
            "storage_usage": {
                "records": f"{len(records)} records ({records_size / 1024:.1f} KB)",
                "backups": f"{backup_size / 1024:.1f} KB",
                "logs": f"{logs_size / 1024:.1f} KB"
            },
            "autobackup": {
                "status": "Enabled" if backup_config.get('enabled') else "Disabled",
                "mode": backup_config.get('mode', 'daily'),
                "last_backup": backup_config.get('last_backup', 'Never')
            }
        }
        
        return report
    
    @staticmethod
    def security_report():
        log_entries = []
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, 'r', encoding='utf-8') as f:
                    log_entries = f.readlines()[-100:] 
            except:
                log_entries = []
        
        failed_logins = 0
        security_events = 0
        
        for line in log_entries:
            if 'LOGIN_FAIL' in line:
                failed_logins += 1
            if 'SECURITY_WARNING' in line or 'AUTOBACKUP' in line or 'USERADD' in line or 'USERDEL' in line:
                security_events += 1
        
        report = {
            "recent_activity": {
                "failed_logins": failed_logins,
                "security_events": security_events,
                "total_log_entries": len(log_entries)
            },
            "recommendations": []
        }
        

        if failed_logins > 5:
            report["recommendations"].append("High number of failed login attempts detected")
        
        if security_events > 10:
            report["recommendations"].append("Multiple security events detected - review logs")
        
        return report