# core/database.py
import os, json, uuid, re
from cryptography.fernet import Fernet
from core.utils import RECORDS_PATH, BACKUP_DIR, timestamp
from core.logger import log
from core.config_manager import get_encryption_key
from core.validators import DataValidator

def ensure_data_dir():
    d = os.path.dirname(RECORDS_PATH)
    os.makedirs(d, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def get_exports_dir():
    if os.name == 'nt':  # Windows
        base_dir = os.path.join(os.path.expanduser("~"), "Datana")
    else:  # Linux/Mac
        base_dir = os.path.join(os.path.expanduser("~"), "Datana")
    
    exports_dir = os.path.join(base_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    return exports_dir

def load_records():
    key = get_encryption_key()
    ensure_data_dir()
    
    if not os.path.exists(RECORDS_PATH):
        return []
        
    try:
        with open(RECORDS_PATH, "rb") as f:
            token = f.read()
        fernet = Fernet(key)
        data = fernet.decrypt(token)
        return json.loads(data.decode())
    except Exception as e:
        print(f"Error loading records: {e}")
        return []

def save_records(records):

    key = get_encryption_key()
    ensure_data_dir()
    
    try:
        fernet = Fernet(key)
        data = json.dumps(records, ensure_ascii=False).encode()
        token = fernet.encrypt(data)
        with open(RECORDS_PATH, "wb") as fh:
            fh.write(token)
    except Exception as e:
        print(f"Error saving records: {e}")

def validate_iranian_phone(phone):
    if not phone:
        return True, ""  # Phone is optional
    
    # Clean input
    phone = phone.strip()
    
    # Cannot start with 0
    if phone.startswith('0'):
        return False, "Phone number cannot start with 0"
    
    # Check format +989123456789
    pattern = r'^\+98\d{10}$'
    if not re.match(pattern, phone):
        return False, "Invalid phone format. Correct format: +989123456789"
    
    return True, ""

def validate_national_id(national_id):
    if not national_id:
        return True, ""  # National ID is optional
    
    # Clean input
    national_id = national_id.strip()
    
    # 1. Check 10 digits
    if len(national_id) != 10 or not national_id.isdigit():
        return False, "National ID must be 10 digits"
    
    # 2. Check all digits not same
    if len(set(national_id)) == 1:
        return False, "National ID cannot have all identical digits"
    
    # 3. Calculate check digit
    check_digit = int(national_id[9])
    total = 0
    
    for i in range(9):
        total += int(national_id[i]) * (10 - i)
    
    remainder = total % 11
    
    # Calculate correct check digit
    if remainder < 2:
        calculated_check = remainder
    else:
        calculated_check = 11 - remainder
    
    # Compare check digit
    if calculated_check != check_digit:
        return False, "Invalid national ID"
    
    return True, "Valid national ID"

def format_iranian_phone(phone_part):
    if not phone_part:
        return None
    
    phone_part = phone_part.strip()
    
    # If user entered full number
    if phone_part.startswith('+98'):
        is_valid, error_msg = validate_iranian_phone(phone_part)
        if not is_valid:
            raise ValueError(error_msg)
        return phone_part
    
    # If only 9 digits entered
    if len(phone_part) == 10 and phone_part.isdigit():
        return f"+98{phone_part}"
    
    # If less than 10 digits
    if phone_part.isdigit() and len(phone_part) < 10:
        return None
    
    # Invalid characters
    raise ValueError("Invalid phone number. Enter 10 digits after +98")

def capitalize_name(name):
    if not name:
        return name
    return name[0].upper() + name[1:].lower()

def is_duplicate_record(phone=None, national_id=None):
    records = load_records()
    
    for record in records:
        if phone and record.get('phone') and record['phone'] == phone:
            return True, f"Record with phone {phone} already exists (ID: {record['id']})"
        
        if national_id and record.get('national_id') and record['national_id'] == national_id:
            return True, f"Record with national ID {national_id} already exists (ID: {record['id']})"
    
    return False, ""

def add_record(first, last, national_id=None, dob=None, phone=None, address=None, tags=None, notes=None):
    
    is_valid_first, first_msg = DataValidator.validate_english_name(first, "First name")
    if not is_valid_first:
        raise ValueError(f"First name validation error: {first_msg}")
    
    is_valid_last, last_msg = DataValidator.validate_english_name(last, "Last name")
    if not is_valid_last:
        raise ValueError(f"Last name validation error: {last_msg}")
    
    if national_id:
        is_valid_national, national_msg = DataValidator.validate_national_id(national_id)
        if not is_valid_national:
            raise ValueError(f"National ID validation error: {national_msg}")
    
    if phone:
        is_valid_phone, phone_msg = DataValidator.validate_iranian_phone(phone)
        if not is_valid_phone:
            raise ValueError(f"Phone validation error: {phone_msg}")
    
    if address:
        is_valid_city, city_msg = DataValidator.validate_city_name(address)
        if not is_valid_city:
            raise ValueError(f"City validation error: {city_msg}")
    
    first = DataValidator.capitalize_name(first)
    last = DataValidator.capitalize_name(last)
    if address:
        address = DataValidator.capitalize_city(address)
    
    is_duplicate, duplicate_msg = is_duplicate_record(phone=phone, national_id=national_id)
    if is_duplicate:
        raise ValueError(f"Duplicate record: {duplicate_msg}")
    
    recs = load_records()
    rid = str(uuid.uuid4())[:8].upper()
    
    item = {
        "id": rid,
        "first_name": first,
        "last_name": last,
        "national_id": national_id,
        "dob": dob,
        "phone": phone,
        "address": address,
        "tags": tags,
        "notes": notes,
        "created_at": timestamp(),
        "security_score": DataValidator.generate_security_score({
            'first_name': first,
            'last_name': last,
            'national_id': national_id,
            'phone': phone,
            'address': address
        })
    }
    
    anomalies = DataValidator.detect_anomaly(item)
    if anomalies:
        print(f"Security warning: {', '.join(anomalies)}")
        log(f"SECURITY_WARNING: Anomalies detected in record {rid} - {anomalies}")
    
    recs.append(item)
    save_records(recs)
    log(f"ADD: id={rid} first={first} last={last} national_id={national_id} phone={phone} security_score={item['security_score']}")
    return rid 


def search_by_id(rid):
    recs = load_records()
    for r in recs:
        if r["id"] == rid:
            return r
    return None

def search_by_name_partial(term):
    recs = load_records()
    term_low = term.lower()
    result = []
    
    for r in recs:
        first_match = r.get("first_name","") and term_low in r["first_name"].lower()
        last_match = r.get("last_name","") and term_low in r["last_name"].lower()
        
        if first_match or last_match:
            result.append(r)
            
    return result

def search_by_national_id(national_id):
    recs = load_records()
    for r in recs:
        if r.get("national_id") == national_id:
            return r
    return None

def search_by_phone(phone):
    recs = load_records()
    for r in recs:
        if r.get("phone") == phone:
            return r
    return None

def advanced_search(first_name=None, last_name=None, city=None, national_id=None, phone=None, search_mode="and"):
    records = load_records()
    
    if not any([first_name, last_name, city, national_id, phone]):
        return records
    
    results = []
    
    for record in records:
        matches = []
        
        if first_name and first_name.strip():
            first_name_match = False
            if record.get('first_name') and first_name.lower() in record['first_name'].lower():
                first_name_match = True
            matches.append(first_name_match)
        
        if last_name and last_name.strip():
            last_name_match = False
            if record.get('last_name') and last_name.lower() in record['last_name'].lower():
                last_name_match = True
            matches.append(last_name_match)
        
        if city and city.strip():
            city_match = False
            if record.get('address') and city.lower() in record['address'].lower():
                city_match = True
            matches.append(city_match)
        
        if national_id and national_id.strip():
            national_id_match = False
            if record.get('national_id') and record['national_id'] == national_id:
                national_id_match = True
            matches.append(national_id_match)
        
        if phone and phone.strip():
            phone_match = False
            if record.get('phone') and record['phone'] == phone:
                phone_match = True
            matches.append(phone_match)
        
        if search_mode == "and":
            if matches and all(matches):
                results.append(record)
        else:
            if matches and any(matches):
                results.append(record)
    
    return results

def delete_record_by_id(record_id):
    records = load_records()
    
    for i, record in enumerate(records):
        if record["id"] == record_id:
            del records[i]
            save_records(records)
            return True
    
    return False

def export_csv(path=None):
    import csv
    import time
    
    recs = load_records()
    
    if not recs:
        print("No records to export")
        return 0, None
    
    # Get system-standard exports directory
    exports_dir = get_exports_dir()
    
    # Generate automatic filename with timestamp
    if not path:
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(exports_dir, f"export_{timestamp_str}.csv")
    else:
        # If custom path provided, ensure it's in exports directory
        if not os.path.isabs(path):
            path = os.path.join(exports_dir, path)
    
    keys = ["id", "first_name", "last_name", "national_id", "dob", "phone", "address", "tags", "notes", "created_at"]
    
    try:
        # Check if file exists and create backup
        if os.path.exists(path):
            backup_path = path + ".backup"
            import shutil
            shutil.copy(path, backup_path)
            print(f"Backup created: {backup_path}")
        
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in recs:
                writer.writerow({k: r.get(k, "") for k in keys})
                
        log(f"EXPORT: path={path} count={len(recs)}")
        return len(recs), path
        
    except Exception as e:
        print(f"Export failed: {e}")
        return 0, None

def create_backup():
    import shutil
    import time
    
    ensure_data_dir()
    recs = load_records()
    
    if not recs:
        print("No data to backup")
        return None
        
    try:
        t = time.strftime("%Y%m%d_%H%M%S")
        target = os.path.join(BACKUP_DIR, f"backup_{t}.enc")
        
        if os.path.exists(RECORDS_PATH):
            shutil.copy(RECORDS_PATH, target)
            log(f"BACKUP: created {target}")
            
            # Clean up old backups
            cleanup_old_backups()
            
            return target
        else:
            print("No records file found for backup")
            return None
            
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def get_system_stats():
    records = load_records()
    from core.auth import load_users
    
    stats = {
        "total_records": len(records),
        "total_users": len(load_users()),
        "data_size": os.path.getsize(RECORDS_PATH) if os.path.exists(RECORDS_PATH) else 0,
        "last_backup": get_last_backup_info(),
        "records_by_city": {},
        "records_with_phone": 0,
        "records_with_national_id": 0,
        "oldest_record": None,
        "newest_record": None
    }
    
    for record in records:
        city = record.get('address', 'Unknown')
        stats["records_by_city"][city] = stats["records_by_city"].get(city, 0) + 1
        
        if record.get('phone'):
            stats["records_with_phone"] += 1
        if record.get('national_id'):
            stats["records_with_national_id"] += 1
        
        if stats["oldest_record"] is None or record.get('created_at', '') < stats["oldest_record"].get('created_at', ''):
            stats["oldest_record"] = record
        if stats["newest_record"] is None or record.get('created_at', '') > stats["newest_record"].get('created_at', ''):
            stats["newest_record"] = record
    
    return stats

def get_last_backup_info():
    if not os.path.exists(BACKUP_DIR):
        return "No backups found"
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_') and f.endswith('.enc')]
    if not backups:
        return "No backups found"
    
    latest_backup = sorted(backups)[-1]
    backup_path = os.path.join(BACKUP_DIR, latest_backup)
    backup_time = os.path.getctime(backup_path)
    
    from datetime import datetime
    return f"{latest_backup} ({datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d %H:%M:%S')})"

def get_available_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.startswith('backup_') and f.endswith('.enc'):
            backup_path = os.path.join(BACKUP_DIR, f)
            backup_time = os.path.getctime(backup_path)
            backup_size = os.path.getsize(backup_path)
            
            from datetime import datetime
            backups.append({
                'filename': f,
                'path': backup_path,
                'created': datetime.fromtimestamp(backup_time),
                'size': backup_size
            })
    
    return sorted(backups, key=lambda x: x['created'], reverse=True)

def restore_from_backup(backup_filename):
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        return False, "Backup file not found"
    
    try:
        current_backup = create_backup()
        if current_backup:
            print(f"Current data backed up to: {current_backup}")
        
        import shutil
        shutil.copy(backup_path, RECORDS_PATH)
        log(f"RESTORE: restored from {backup_filename}")
        return True, "Restore completed successfully"
    except Exception as e:
        return False, f"Restore failed: {e}"

def cleanup_old_backups(max_backups=10):
    backups = get_available_backups()
    
    if len(backups) <= max_backups:
        return
    
    backups_to_keep = backups[:max_backups]
    backups_to_delete = backups[max_backups:]
    
    for backup in backups_to_delete:
        try:
            os.remove(backup['path'])
            log(f"BACKUP_CLEANUP: removed {backup['filename']}")
        except Exception as e:
            print(f"Error deleting backup {backup['filename']}: {e}")

def get_records_count():
    recs = load_records()
    return len(recs)

def delete_all_records():
    try:
        if os.path.exists(RECORDS_PATH):
            os.remove(RECORDS_PATH)
            print("All records deleted")
            log("DELETE_ALL: all records removed")
        else:
            print("No records file found")
    except Exception as e:
        print(f"Delete failed: {e}")

def get_recent_records(limit=5):
    recs = load_records()
    return recs[-limit:] if recs else []

def show_exports_location():
    exports_dir = get_exports_dir()
    return exports_dir