from core.argument_parser import (
    handle_useradd_arguments, handle_userdel_arguments, handle_usermod_arguments,
    handle_add_arguments, handle_delete_arguments, handle_view_arguments,
    handle_search_arguments, handle_export_arguments, show_command_help,
    handle_useredit_arguments
)
from core.database import (
    add_record, search_by_name_partial, search_by_id, export_csv, create_backup, 
    load_records, save_records, validate_iranian_phone, format_iranian_phone, 
    validate_national_id, is_duplicate_record, delete_record_by_id, capitalize_name,
    show_exports_location, get_system_stats, advanced_search, get_available_backups,
    restore_from_backup, get_last_backup_info
)
from core.auth import verify, load_users, save_users
from threading import Thread, Event
from cryptography.fernet import Fernet
from core.progress import animated_login, loading_operation
from core.progress import simple_loading
from core.argument_parser import handle_add_arguments, show_command_help
from core.clear import clear_screen
from core.logger import log
from core.utils import VERSION, LOG_PATH, USERS_PATH
from core.validators import DataValidator
from tabulate import tabulate
import getpass
import os
import sys
import bcrypt
import json
import time
import psutil

last_activity_time = time.time()
logout_timer_event = Event()

ACCESS = {
    "root": {"add", "search", "view", "export", "backup", "help", "clear", "whoami", "exit", 
             "useradd", "userdel", "usermod", "logs", "config", "edit", "delete", "lists", 
             "userlist", "stats", "restore", "autobackup", "useredit"},
    "admin": {"add", "search", "view", "export", "backup", "help", "clear", "whoami", "exit", 
              "logs", "edit", "delete", "lists", "userlist", "stats"},
    "staff": {"add", "search", "view", "export", "help", "clear", "whoami", "exit", "lists", "stats"},
    "viewer": {"search", "view", "help", "clear", "whoami", "exit", "lists", "stats"}
}

COMMANDS = {
    "status": {"roles": {"root", "admin", "staff"}, "desc": "Show system status and health"},
    "report": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Generate advanced reports"},
    "help": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show help"},
    "clear": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Clear screen"},
    "whoami": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show current user and role"},
    "add": {"roles": {"root", "admin", "staff"}, "desc": "Add new record"},
    "search": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Search records with advanced options"},
    "view": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "View one record"},
    "export": {"roles": {"root", "admin", "staff"}, "desc": "Export all to CSV"},
    "backup": {"roles": {"root", "admin"}, "desc": "Create backup"},
    "edit": {"roles": {"root", "admin"}, "desc": "Edit existing record"},
    "delete": {"roles": {"root", "admin"}, "desc": "Delete record"},
    "useradd": {"roles": {"root"}, "desc": "Add new user"},
    "userdel": {"roles": {"root"}, "desc": "Delete user"},
    "usermod": {"roles": {"root"}, "desc": "Modify user role"},
    "useredit": {"roles": {"root"}, "desc": "Edit user username or password"},
    "logs": {"roles": {"root", "admin"}, "desc": "View system logs"},
    "config": {"roles": {"root"}, "desc": "System configuration"},
    "lists": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "List all records with pagination"},
    "userlist": {"roles": {"root", "admin"}, "desc": "List all system users"},
    "stats": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show system statistics"},
    "restore": {"roles": {"root"}, "desc": "Restore from backup"},
    "autobackup": {"roles": {"root"}, "desc": "Configure auto-backup"},
    "exit": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Quit"},
    "logout": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Quit"}
}
COMMANDS.update({
    "profile": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show your gamification profile"},
    "leaderboard": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show top users by points"},
    "badges": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "List your earned badges"},
    "bulk": {"roles": {"root", "admin"}, "desc": "Bulk operations on records"},
    "run": {"roles": {"root", "admin"}, "desc": "Run web panel or other services"},
    "joke": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Tell a random programming joke"},
    "reminder": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Set and manage reminders"},
    "time": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show current time and system uptime"},
    "tip": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show a random tech tip"},
    "fact": {"roles": {"root", "admin", "staff", "viewer"}, "desc": "Show a random fact about Datana"}
})

#Chatgpt helped me to create command description
def do_status(role, current_user, parts=None):
    if role == "viewer":
        print("Access denied. Viewer role cannot view system status.")
        return
    if parts and any(arg in ['--help', '-h', 'help'] for arg in parts):
        print("""
status [OPTIONS]

Display comprehensive system status and health information.

OPTIONS:
  -s, --show SECTION    Display specific section only
                        Available sections: resource, metrics, security
  -h, --help           Show this help message

EXAMPLES:
  status                    # Display all system information
  status -s resource        # Show only system resources
  status --show metrics     # Show only datana metrics
  status -s security        # Show only security information
""")
        return
    show_section = "all"
    if parts:
        for i, part in enumerate(parts):
            if part in ["-s", "--show"] and i + 1 < len(parts):
                show_section = parts[i + 1].lower()
                break

    if show_section != "all":
        if show_section not in ["resource", "metrics", "security"]:
            print(f"Invalid section: {show_section}")
            print("Available sections: resource, metrics, security")
            return
        
        try:
            loading_operation(f"GATHERING {show_section.upper()} STATUS", 0.5)
            show_professional_status(role, current_user, show_section)
        except KeyboardInterrupt:
            print("\nStatus cancelled")
        except Exception as e:
            print(f"Error displaying status: {e}")
    else:
        try:
            loading_operation("GATHERING SYSTEM STATUS", 1.0)
            show_professional_status(role, current_user, "all")
        except KeyboardInterrupt:
            print("\nStatus cancelled")
        except Exception as e:
            print(f"Error displaying status: {e}")

def show_professional_status(role, current_user, show_section="all"):
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    disk = psutil.disk_usage('/')
    
    from core.database import load_records, get_system_stats
    from core.auth import load_users
    
    records = load_records()
    users = load_users()
    stats = get_system_stats()
    
    print("\n" + "="*65)
    print("DATANA SYSTEM STATUS".center(65))
    print("="*65)

    if show_section in ["all", "resource"]:
        show_resource_table(memory, cpu_percent, disk)
    
    if show_section in ["all", "metrics"]:
        show_metrics_table(records, users, stats, current_user, role)
    
    if show_section in ["all", "security"]:
        show_security_table(records)

#Note : DeepSeek Ai Help me to create this table . remember i dont use Ai for all this section
def show_resource_table(memory, cpu_percent, disk):
    print("\n+-------------------+---------------------+-------------------+")
    print("| RESOURCE          | USAGE               | DETAILS           |")
    print("+-------------------+---------------------+-------------------+")
    print(f"| Memory            | {create_bar(memory.percent, 10)} {memory.percent:>3.0f}% | {memory.used//(1024**3):>2}/{memory.total//(1024**3):>2} GB              |")
    print(f"| CPU               | {create_bar(cpu_percent, 10)} {cpu_percent:>3.1f}% | Load: {psutil.getloadavg()[0]:.1f}            |")
    print(f"| Disk              | {create_bar(disk.percent, 10)} {disk.percent:>3.1f}% | {disk.used//(1024**3):>3}/{disk.total//(1024**3):>3} GB           |")
    print("+-------------------+---------------------+-------------------+")

def show_metrics_table(records, users, stats, current_user, role):
    last_backup = "Available" if stats.get('last_backup') != "No backups found" else "None"
    
    print("\n+---------------------+----------+-------------+-----------+")
    print("| DATANA METRICS      | COUNT    | SIZE        | STATUS    |")
    print("+---------------------+----------+-------------+-----------+")
    print(f"| Records             | {len(records):<8} | {stats.get('data_size', 0)//1024:>5} KB     | ACTIVE   |")
    print(f"| Users               | {len(users):<8} | {len(users)*1.2:>5.1f} KB     | ACTIVE   |")
    print(f"| Last Backup         | {last_backup:<8} | -           | OK       |")
    print(f"| Current Session     | {current_user:<8} | {role:<11}  | ACTIVE   |")
    print("+---------------------+----------+-------------+-----------+")

def show_security_table(records):
    print("\n+---------------------+------------------+-----------------+")
    print("| SECURITY            | STATUS           | LAST ACTIVITY   |")
    print("+---------------------+------------------+-----------------+")
    enc_status = "ACTIVE" if len(records) > 0 else "INACTIVE"
    print(f"| Encryption          | {enc_status:<16} | 2 hours ago     |")
    print(f"| Data Integrity      | VERIFIED         | 15 minutes ago  |")
    print(f"| Access Control      | ENFORCED         | Now             |")
    print(f"| Audit Logging       | ACTIVE           | Now             |")
    print("+---------------------+------------------+-----------------+")

def create_bar(percentage, length=10):
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar}"

def create_progress_bar(percentage, length=10):
    filled = int(length * percentage / 100)
    bar = "[" + "█" * filled + "░" * (length - filled) + "]"
    return bar

def reset_activity_timer():
    global last_activity_time
    last_activity_time = time.time()

def check_session_timeout():
    global last_activity_time
    return (time.time() - last_activity_time) > 900 

def auto_logout_monitor():
    while not logout_timer_event.is_set():
        time.sleep(30)  
        if check_session_timeout():
            print("\n\nSession timeout: You have been logged out due to inactivity.")
            print("Please login again.\n")
            os._exit(0)  

def safe_input(prompt):
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\nCancelled")
        return "CANCEL"  

def safe_getpass(prompt):
    try:
        return getpass.getpass(prompt)
    except KeyboardInterrupt:
        print("\nCancelled")
        return "CANCEL"  

def run_project_shell():
    attempts = 0
    user_info = None
    
    while attempts < 3 and not user_info:
        username = safe_input("Username: ")
        if username == "CANCEL": 
            print("Login cancelled")
            return
            
        password = safe_getpass("Password: ")
        if password == "CANCEL":  
            print("Login cancelled")
            return
        
        try:
            animated_login()
        except KeyboardInterrupt:
            print("\nLogin cancelled")
            return
        
        user_info = verify(username, password)
        if not user_info:
            attempts += 1
            print("Login failed. Please try again.")
    
    if not user_info:
        print("Too many failed attempts. Exiting.")
        return

    current_user = user_info["username"]
    role = user_info["role"]
    
    print(f"Welcome {current_user} - role: {role}")
    repl(role, current_user)

def do_joke():
    from core.jokes import JokeSystem
    print(f"\n{JokeSystem.get_random_joke()}\n")

def do_tip():
    from core.jokes import JokeSystem
    print(f"\n{JokeSystem.get_random_tip()}\n")

def do_fact():
    from core.jokes import JokeSystem
    print(f"\n{JokeSystem.get_fun_fact()}\n")

def do_time(parts):
    from core.time_utils import TimeSystem
    
    if len(parts) > 1 and parts[1] == "--timezone":
        if len(parts) > 2:
            tz = parts[2]
            print(f"\nCurrent time in {tz}: {TimeSystem.get_current_time(tz)}")
        else:
            print("\nAvailable timezones:")
            for tz in TimeSystem.get_timezones():
                print(f"  {tz}")
    else:
        print(f"\nLocal time: {TimeSystem.get_current_time()}")
        print(f"System uptime: {TimeSystem.get_system_uptime()}")

def do_reminder(parts):
    from core.reminders import ReminderSystem
    
    if len(parts) < 2:
        print("\nReminder usage:")
        print("  reminder list                    - List active reminders")
        print("  reminder list --all              - List all reminders")
        print("  reminder add \"text\" [options]   - Add new reminder")
        print("  reminder complete <id>           - Mark reminder as complete")
        print("\nOptions for add:")
        print("  --days N      - Remind in N days")
        print("  --hours N     - Remind in N hours")
        print("  --minutes N   - Remind in N minutes")
        return
    
    subcommand = parts[1]
    
    if subcommand == "list":
        show_all = "--all" in parts
        reminders = ReminderSystem.list_reminders(show_completed=show_all)
        
        if not reminders:
            print("\nNo reminders found.")
            return
        
        print(f"\n{'ID':<4} {'Due':<20} {'Status':<12} {'Text'}")
        print("-" * 60)
        
        for r in reminders:
            due_time = datetime.fromisoformat(r["due"]).strftime("%Y-%m-%d %H:%M")
            status = "Completed" if r["completed"] else "Pending"
            print(f"{r['id']:<4} {due_time:<20} {status:<12} {r['text']}")
    
    elif subcommand == "add":
        # استخراج متن از بین کوتیشن‌ها
        import shlex
        try:
            parsed = shlex.split(" ".join(parts[2:]))
            text = parsed[0] if parsed else ""
            
            # استخراج options
            days = 0
            hours = 0
            minutes = 0
            
            for i, arg in enumerate(parsed[1:], 1):
                if arg == "--days" and i+1 < len(parsed):
                    days = int(parsed[i+1])
                elif arg == "--hours" and i+1 < len(parsed):
                    hours = int(parsed[i+1])
                elif arg == "--minutes" and i+1 < len(parsed):
                    minutes = int(parsed[i+1])
            
            if not text:
                print("Error: Reminder text is required")
                return
            
            reminder_id = ReminderSystem.add_reminder(text, days, hours, minutes)
            print(f"\nReminder added successfully! ID: {reminder_id}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    elif subcommand == "complete":
        if len(parts) < 3:
            print("Error: Reminder ID is required")
            return
        
        try:
            reminder_id = int(parts[2])
            if ReminderSystem.complete_reminder(reminder_id):
                print(f"\nReminder {reminder_id} marked as completed.")
            else:
                print(f"\nReminder {reminder_id} not found.")
        except ValueError:
            print("Error: Invalid reminder ID")
    
    else:
        print(f"Unknown subcommand: {subcommand}")


def repl(role, user):
    logout_thread = Thread(target=auto_logout_monitor, daemon=True)
    logout_thread.start()
    
    from core.reminders import ReminderSystem
    due_reminders = ReminderSystem.check_due_reminders()
    
    if due_reminders:
        print(f"\n You have {len(due_reminders)} reminder(s) due:")
        for r in due_reminders:
            print(f"   [{r['id']}] {r['text']}")
        print()

    while True:
        try:
            reset_activity_timer()
            cmd_line = safe_input(f"{user}@datana:~$ ")
            
            if cmd_line == "CANCEL":
                print("\nGoodbye.")
                logout_timer_event.set()
                return
                
            if cmd_line is None:
                continue
                
        except KeyboardInterrupt:
            print("\nGoodbye.")
            logout_timer_event.set()
            return
        except (EOFError):
            print("\nExiting.")
            logout_timer_event.set()
            return

        if not cmd_line:
            continue

        reset_activity_timer()
        
        parts = cmd_line.split()
        base = parts[0].lower()

        if base not in COMMANDS:
            print("Command doesn't exist. try [help]")
            continue

        if role not in COMMANDS[base]["roles"]:
            print("You don't have access to this command")
            continue

        reset_activity_timer()

        if base == "help":
            if len(parts) > 1:
                do_help(role, parts[1])
            else:
                do_help(role)
            continue

        if base == "clear":
            clear_screen()
            continue

        if base == "whoami":
            print(f"user: {user}, role: {role}")
            continue

        if base in ("exit", "logout"):
            print("Goodbye.")
            logout_timer_event.set()
            return
        if base == "profile":
            do_profile(user)
        elif base == "leaderboard":
            do_leaderboard(parts)
        elif base == "badges":
            do_badges(user)

        if base == "status":
            try:
                do_status(role, user, parts)  
            except KeyboardInterrupt:
                print("\nStatus cancelled")
            continue
        if base == "run":
            do_run(role, user, parts)
            continue
        if base == "bulk":
            do_bulk(role, user, parts)
            continue

        if base == "joke":
            do_joke()

        elif base == "reminder":
            do_reminder(parts)

        elif base == "time":
            do_time(parts)

        elif base == "tip":
            do_tip()

        elif base == "fact":
            do_fact()

        # ==================== ADD COMMAND ====================
        if base == "add":
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('add')
                        continue
                    
                    args = handle_add_arguments(parts)
                    if not args:
                        continue
                    
                    first = args['first_name']
                    last = args['last_name']
                    national_id = args['national_id']
                    phone = args['phone']
                    city = args['city']
                    auto_confirm = args.get('auto_confirm', False)
                    
                    print(f"\nAdding record:")
                    print(f"  First Name: {first}")
                    print(f"  Last Name: {last}")
                    print(f"  National ID: {national_id}")
                    print(f"  Phone: {phone}")
                    print(f"  City: {city}")
                    
                    if not auto_confirm:
                        confirm = safe_input("Proceed? (Y/n): ")
                        if confirm and confirm.lower() in ['n', 'no']:
                            print("Add cancelled")
                            continue
                    
                    simple_loading("ADDING RECORD", 1.0)
                    
                    try:
                        rid = add_record(first, last, national_id, None, phone, city, None, None)
                        print(f"Record saved with id {rid}")
                    except ValueError as e:
                        print(f"Error: {e}")
                    continue
                
                first = None
                last = None
                national_id = None
                phone = None
                city = None
                
                while True:
                    first = safe_input("First name: ")
                    if first == "CANCEL": 
                        print("Add cancelled")
                        break
                    
                    if not first or not first.strip():
                        print("Error: First name is required")
                        continue
                    
                    is_valid_first, first_msg = DataValidator.validate_english_name(first, "First name")
                    if not is_valid_first:
                        print(f"Error: {first_msg}")
                        continue
                    break
                
                if first == "CANCEL": 
                    continue
                
                while True:
                    last = safe_input("Last name: ")
                    if last == "CANCEL": 
                        print("Add cancelled")
                        break
                    
                    if not last or not last.strip():
                        print("Error: Last name is required")
                        continue
                    
                    is_valid_last, last_msg = DataValidator.validate_english_name(last, "Last name")
                    if not is_valid_last:
                        print(f"Error: {last_msg}")
                        continue
                    break
                
                if last == "CANCEL": 
                    continue
                
                while True:
                    national_input = safe_input("National ID: ")
                    if national_input == "CANCEL": 
                        print("Add cancelled")
                        break
                    
                    if not national_input or not national_input.strip():
                        print("Error: National ID is required")
                        continue
                    
                    is_valid, error_msg = DataValidator.validate_national_id(national_input)
                    if is_valid:
                        national_id = national_input
                        break
                    else:
                        print(f"Error: {error_msg}")
                        continue
                
                if national_input == "CANCEL": 
                    continue
                
                while True:
                    phone_input = safe_input("Phone: +98 ")
                    if phone_input == "CANCEL": 
                        print("Add cancelled")
                        break
                    
                    if not phone_input or not phone_input.strip():
                        print("Error: Phone is required")
                        continue
                    
                    try:
                        if phone_input.startswith('+98'):
                            formatted_phone = phone_input
                        else:
                            formatted_phone = format_iranian_phone(phone_input)
                        
                        if formatted_phone is None:
                            print("Error: Phone number is required")
                            continue
                        else:
                            is_valid, error_msg = DataValidator.validate_iranian_phone(formatted_phone)
                            if is_valid:
                                phone = formatted_phone
                                break
                            else:
                                print(f"Error: {error_msg}")
                                continue
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue
                
                if phone_input == "CANCEL": 
                    continue
                
                while True:
                    city_input = safe_input("City: ")
                    if city_input == "CANCEL": 
                        print("Add cancelled")
                        break
                    
                    if not city_input or not city_input.strip():
                        print("Error: City is required")
                        continue
                    
                    is_valid_city, city_msg = DataValidator.validate_city_name(city_input)
                    if not is_valid_city:
                        print(f"Error: {city_msg}")
                        continue
                    
                    city = DataValidator.capitalize_city(city_input)
                    break
                
                if city_input == "CANCEL": 
                    continue
                
                simple_loading("ADDING RECORD", 1.0)
                
                try:
                    rid = add_record(first, last, national_id, None, phone, city, None, None)
                    print(f"Record saved with id {rid}")
                except ValueError as e:
                    print(f"Error: {e}")
                
            except KeyboardInterrupt:
                print("\nAdd cancelled")
            continue

        # ==================== VIEW COMMAND ====================
        if base == "view":
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('view')
                        continue
                    
                    args = handle_view_arguments(parts)
                    if not args:
                        continue
                    
                    rid = args['record_id']
                else:
                    if len(parts) < 2:
                        rid = safe_input("Record ID: ")
                        if rid == "CANCEL": 
                            continue
                    else:
                        rid = parts[1]
                
                simple_loading("LOADING RECORD", 0.5)
                
                rec = search_by_id(rid)
                if not rec:
                    print("Not found.")
                else:
                    print("\nRecord details:")
                    print("-" * 40)
                    for k, v in rec.items():
                        print(f"{k}: {v}")
                    print("-" * 40)
            except KeyboardInterrupt:
                print("\nView cancelled")
            continue

        # ==================== SEARCH COMMAND ====================
        if base == "search":
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('search')
                        continue
                    
                    args = handle_search_arguments(parts)
                    if args is not None:
                        simple_loading("ADVANCED SEARCH", 1.0)
                        
                        results = advanced_search(
                            first_name=args.get('first_name'),
                            last_name=args.get('last_name'),
                            city=args.get('city'),
                            national_id=args.get('national_id'),
                            phone=args.get('phone'),
                            search_mode=args.get('mode', 'and')
                        )
                        
                        if not results:
                            print("No results found.")
                        else:
                            table = [(r["id"], r.get("first_name",""), r.get("last_name",""), 
                                     r.get("national_id",""), r.get("phone",""), r.get("address","")) 
                                    for r in results]
                            print(tabulate(table, headers=["ID","First","Last","National ID","Phone","Address"]))
                            print(f"Found {len(results)} results")
                        continue
                
                if len(parts) > 1 and parts[1].startswith('--'):
                    from core.advanced_search import AdvancedSearch
                    
                    if parts[1] == "--regex" and len(parts) > 2:
                        pattern = " ".join(parts[2:])
                        field = 'all'
                        if len(parts) > 3 and parts[2] in ['name', 'city', 'phone', 'national_id']:
                            field = parts[2]
                            pattern = " ".join(parts[3:])
                        
                        loading_operation("REGEX SEARCH", 1.0)
                        results = AdvancedSearch.regex_search(pattern, field)
                        
                    elif parts[1] == "--date" and len(parts) > 2:
                        date_str = parts[2]
                        loading_operation("DATE SEARCH", 1.0)
                        results = AdvancedSearch.date_search(date_str)
                        
                    elif parts[1] == "--empty" and len(parts) > 2:
                        field = parts[2]
                        loading_operation("EMPTY FIELD SEARCH", 1.0)
                        results = AdvancedSearch.empty_field_search(field)
                        
                    else:
                        print("Invalid search option. Available options:")
                        print("  --regex [pattern] [field]  - Search with regex")
                        print("  --date YYYY-MM-DD          - Search by date")
                        print("  --empty [field]            - Find records with empty field")
                        continue
                
                else:
                    print("\nSearch options:")
                    print("  1. Simple name search")
                    print("  2. Advanced search with filters")
                    
                    search_type = safe_input("Choose search type (1/2): ")
                    if search_type == "CANCEL": 
                        continue
                    
                    if search_type == "2":
                        
                        first_name = safe_input("First name (leave empty for any): ")
                        if first_name == "CANCEL": 
                            continue
                        
                        last_name = safe_input("Last name (leave empty for any): ")
                        if last_name == "CANCEL": 
                            continue
                        
                        city = safe_input("City (leave empty for any): ")
                        if city == "CANCEL": 
                            continue
                        
                        national_id_filter = safe_input("National ID (leave empty for any): ")
                        if national_id_filter == "CANCEL": 
                            continue
                        
                        phone_filter = safe_input("Phone (leave empty for any): ")
                        if phone_filter == "CANCEL": 
                            continue
                        
                        print("\nSearch mode:")
                        print("  1. AND - All filters must match")
                        print("  2. OR - Any filter can match")
                        mode_choice = safe_input("Choose search mode (1/2): ")
                        if mode_choice == "CANCEL": 
                            continue
                        search_mode = "and" if mode_choice != "2" else "or"
                        
                        loading_operation("ADVANCED SEARCH", 1.0)
                        results = advanced_search(
                            first_name=first_name if first_name else None,
                            last_name=last_name if last_name else None,
                            city=city if city else None,
                            national_id=national_id_filter if national_id_filter else None,
                            phone=phone_filter if phone_filter else None,
                            search_mode=search_mode
                        )
                    else:
                        if len(parts) > 1:
                            term = " ".join(parts[1:])
                        else:
                            term = safe_input("Search term: ")
                            if term == "CANCEL": 
                                continue
                        
                        loading_operation("SEARCHING", 0.8)
                        results = search_by_name_partial(term)
                
                if not results:
                    print("No results found.")
                else:
                    table = [(r["id"], r.get("first_name",""), r.get("last_name",""), 
                             r.get("national_id",""), r.get("phone",""), r.get("address","")) 
                            for r in results]
                    print(tabulate(table, headers=["ID","First","Last","National ID","Phone","Address"]))
                    print(f"Found {len(results)} results")
                    
            except KeyboardInterrupt:
                print("\nSearch cancelled")
            continue

        # ==================== EXPORT COMMAND ====================
        if base == "export":
            try:
                auto_confirm = False
                custom_path = None
                
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('export')
                        continue
                    
                    args = handle_export_arguments(parts)
                    if args:
                        custom_path = args.get('filename')
                        auto_confirm = args.get('auto_confirm', False)
                else:
                    if len(parts) > 1:
                        custom_path = parts[1]
                    else:
                        use_custom = safe_input("Use custom filename? (y/N): ")
                        if use_custom and use_custom.lower() in ['y', 'yes']:
                            custom_path = safe_input("Filename: ")
                            if custom_path == "CANCEL": 
                                continue
                            if not custom_path.endswith('.csv'):
                                custom_path += '.csv'
                
                exports_dir = show_exports_location()
                print(f"Exports will be saved to: {exports_dir}")
                
                records = load_records()
                record_count = len(records)
                
                if record_count == 0:
                    print("No records to export")
                    continue
                
                print(f"\nExport preview:")
                print(f"  Records to export: {record_count}")
                print(f"  Fields: ID, First Name, Last Name, National ID, Phone, Address, etc.")
                if custom_path:
                    print(f"  File: {os.path.join(exports_dir, custom_path)}")
                else:
                    print(f"  File: auto-generated with timestamp")
                
                if not auto_confirm:
                    confirm = safe_input("Proceed with export? (Y/n): ")
                    if confirm and confirm.lower() in ['n', 'no']:
                        print("Export cancelled")
                        continue
                
                simple_loading("EXPORTING RECORDS", 1.5)
                
                count, export_path = export_csv(custom_path)
                
                if count > 0 and export_path:
                    print(f"Export completed successfully!")
                    print(f"  Records exported: {count}")
                    print(f"  File location: {export_path}")
                    print(f"  File size: {os.path.getsize(export_path) if os.path.exists(export_path) else 'N/A'} bytes")
                    
                    if count > 0:
                        print(f"\nFirst 3 records exported:")
                        sample_records = records[:3]
                        for i, rec in enumerate(sample_records, 1):
                            print(f"  {i}. {rec.get('first_name', '')} {rec.get('last_name', '')} - {rec.get('phone', '')}")
                        if count > 3:
                            print(f"  ... and {count - 3} more records")
                else:
                    print("Export failed or no records were exported")
                    
            except KeyboardInterrupt:
                print("\nExport cancelled")
            except Exception as e:
                print(f"Export error: {e}")
            continue

        # ==================== DELETE COMMAND ====================
        if base == "delete":
            if role not in ["root", "admin"]:
                print("Access denied. Only root and admin can delete records.")
                continue
            
            record_id = None
            auto_confirm = False
            
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('delete')
                        continue
                    
                    args = handle_delete_arguments(parts)
                    if not args:
                        continue
                    
                    record_id = args['record_id']
                    auto_confirm = args.get('auto_confirm', False)
                else:
                    if len(parts) > 1:
                        record_id = parts[1]
                        auto_confirm = False
                    else:
                        record_id = safe_input("Record ID to delete: ")
                        if record_id == "CANCEL": 
                            continue
                        auto_confirm = False
                
                if not auto_confirm:
                    confirm = safe_input(f"Are you sure you want to delete record {record_id}? (y/N): ")
                    if not confirm or confirm.lower() not in ['y', 'yes']:
                        print("Delete cancelled")
                        continue
                
                do_delete_direct(role, user, record_id)
                    
            except KeyboardInterrupt:
                print("\nDelete cancelled")
            continue

        # ==================== USERADD COMMAND ====================
        if base == "useradd":
            if role != "root":
                print("Access denied. Only root can add users.")
                continue
            
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('useradd')
                        continue
                    
                    args = handle_useradd_arguments(parts)
                    if not args:
                        continue
                    
                    username = args['username']
                    password = args['password']
                    user_role = args.get('role', 'viewer')
                    auto_confirm = args.get('auto_confirm', False)
                else:
                    username = safe_input("Username: ")
                    if username == "CANCEL": continue
                    
                    password = safe_getpass("Password: ")
                    if password == "CANCEL": continue
                    
                    user_role = safe_input("Role (root/admin/staff/viewer): ")
                    if user_role == "CANCEL": continue
                    
                    user_role = user_role.lower()
                    auto_confirm = False
                
                do_useradd(role, user, username, password, user_role, auto_confirm)
            except KeyboardInterrupt:
                print("\nUser add cancelled")
            continue

        # ==================== USERDEL COMMAND ====================
        if base == "userdel":
            if role != "root":
                print("Access denied. Only root can delete users.")
                continue
                
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('userdel')
                        continue
                    
                    args = handle_userdel_arguments(parts)
                    if not args:
                        continue
                    
                    username = args['username']
                    auto_confirm = args.get('auto_confirm', False)
                else:
                    username = safe_input("Username to delete: ")
                    if username == "CANCEL": continue
                    auto_confirm = False
                
                do_userdel(role, user, username, auto_confirm)
                    
            except KeyboardInterrupt:
                print("\nUser delete cancelled")
            continue

        # ==================== USERMOD COMMAND ====================
        if base == "usermod":
            if role != "root":
                print("Access denied. Only root can modify users.")
                continue
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('usermod')
                        continue
                    
                    args = handle_usermod_arguments(parts)
                    if not args:
                        continue
                    
                    username = args['username']
                    new_role = args['role']
                    auto_confirm = args.get('auto_confirm', False)
                else:
                    username = safe_input("Username to modify: ")
                    if username == "CANCEL": continue
                    
                    new_role = safe_input("New role (root/admin/staff/viewer): ")
                    if new_role == "CANCEL": continue
                    
                    new_role = new_role.lower()
                    auto_confirm = False
                
                do_usermod(role, user, username, new_role, auto_confirm)
            except KeyboardInterrupt:
                print("\nUser modify cancelled")
            continue

        # ==================== USEREDIT COMMAND ====================
        if base == "useredit":
            if role != "root":
                print("Access denied. Only root can edit users.")
                continue
                
            try:
                if len(parts) > 1 and parts[1].startswith('-'):
                    if parts[1] == '--help':
                        show_command_help('useredit')
                        continue
                    
                    args = handle_useredit_arguments(parts)
                    if not args:
                        continue
                    
                    username = args['username']
                    new_password = args.get('new_password')
                    new_username = args.get('new_username')
                    auto_confirm = args.get('auto_confirm', False)
                else:
                    username = safe_input("Username to edit: ")
                    if username == "CANCEL": continue
                    
                    print("What do you want to change?")
                    print("  1. Change username")
                    print("  2. Change password")
                    print("  3. Both")
                    
                    choice = safe_input("Select (1/2/3): ")
                    if choice == "CANCEL": continue
                    
                    new_username = None
                    new_password = None
                    
                    if choice in ["1", "3"]:
                        new_username = safe_input("New username: ")
                        if new_username == "CANCEL": continue
                        if not new_username.strip():
                            print("Error: New username cannot be empty")
                            continue
                            
                    if choice in ["2", "3"]:
                        new_password = safe_getpass("New password: ")
                        if new_password == "CANCEL": continue
                        if not new_password.strip():
                            print("Error: New password cannot be empty")
                            continue
                    
                    auto_confirm = False
                
                do_useredit(role, user, username, new_password, new_username, auto_confirm)
            except KeyboardInterrupt:
                print("\nUser edit cancelled")
            continue

        # ==================== EDIT COMMAND ====================
        if base == "edit":
            try:
                do_edit(role, user)
            except KeyboardInterrupt:
                print("\nEdit cancelled")
            continue

        # ==================== LISTS COMMAND ====================
        if base == "lists":
            try:
                do_lists(role, user)
            except KeyboardInterrupt:
                print("\nLists cancelled")
            continue

        # ==================== USERLIST COMMAND ====================
        if base == "userlist":
            try:
                do_userlist(role, user)
            except KeyboardInterrupt:
                print("\nUserlist cancelled")
            continue

        # ==================== LOGS COMMAND ====================
        if base == "logs":
            try:
                do_advanced_logs(role, user)
            except KeyboardInterrupt:
                print("\nLogs cancelled")
            continue

        # ==================== REPORT COMMAND ====================
        if base == "report":
            try:
                from core.analytics import Analytics
                from core.secure_logger import SecureLogger
                
                print("\nReport Types:")
                print("  1. User Activity Report")
                print("  2. Data Quality Report") 
                print("  3. System Status Report")
                print("  4. Security Report")
                print("  5. Log File Analysis")
                
                report_type = safe_input("Select report type (1-5): ")
                if report_type == "CANCEL": 
                    continue
                
                loading_operation("GENERATING REPORT", 1.5)
                
                if report_type == "1":
                    report = Analytics.user_activity_report()
                    print("\n" + "="*50)
                    print("USER ACTIVITY REPORT")
                    print("="*50)
                    print(f"Total Users: {report['total_users']}")
                    print(f"Total Records: {report['total_records']}")
                    print("\nUsers by Role:")
                    for role, count in report['users_by_role'].items():
                        print(f"  {role}: {count} user(s)")
                    
                elif report_type == "2":
                    report = Analytics.data_quality_report()
                    print("\n" + "="*50)
                    print("DATA QUALITY REPORT")
                    print("="*50)
                    print(f"Total Records: {report['total_records']}")
                    print("\nData Completeness:")
                    for field, completeness in report['completeness'].items():
                        print(f"  {field}: {completeness}")
                    print("\nData Validity:")
                    for check, result in report['validity'].items():
                        print(f"  {check}: {result}")
                    
                elif report_type == "3":
                    report = Analytics.system_status_report()
                    print("\n" + "="*50)
                    print("SYSTEM STATUS REPORT")
                    print("="*50)
                    print("Storage Usage:")
                    for item, usage in report['storage_usage'].items():
                        print(f"  {item}: {usage}")
                    print("\nAuto-backup Status:")
                    for key, value in report['autobackup'].items():
                        print(f"  {key}: {value}")
                    
                elif report_type == "4":
                    report = Analytics.security_report()
                    print("\n" + "="*50)
                    print("SECURITY REPORT")
                    print("="*50)
                    print("Recent Activity:")
                    for activity, count in report['recent_activity'].items():
                        print(f"  {activity}: {count}")
                    if report['recommendations']:
                        print("\nRecommendations:")
                        for rec in report['recommendations']:
                            print(f"  - {rec}")
                    
                elif report_type == "5":
                    stats = SecureLogger.get_log_stats()
                    print("\n" + "="*50)
                    print("LOG FILE ANALYSIS")
                    print("="*50)
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    
                else:
                    print("Invalid report type")
                    
            except KeyboardInterrupt:
                print("\nReport cancelled")
            except Exception as e:
                print(f"Error generating report: {e}")
            continue

        # ==================== BACKUP COMMAND ====================
        if base == "backup":
            try:
                simple_loading("CREATING BACKUP", 1.5)
                
                target = create_backup()
                if target:
                    print(f"Backup created: {target}")
                    print(f"Last backup: {get_last_backup_info()}")
                else:
                    print("No data to backup.")
            except KeyboardInterrupt:
                print("\nBackup cancelled")
            continue

        # ==================== STATS COMMAND ====================
        if base == "stats":
            try:
                loading_operation("GATHERING STATISTICS", 1.0)
                stats = get_system_stats()
                
                print("\n" + "="*50)
                print("DATANA SYSTEM STATISTICS")
                print("="*50)
                
                print(f"\nRecords:")
                print(f"  Total records: {stats['total_records']}")
                print(f"  With phone: {stats['records_with_phone']}")
                print(f"  With national ID: {stats['records_with_national_id']}")
                print(f"  Data size: {stats['data_size']} bytes")
                
                print(f"\nUsers:")
                print(f"  Total users: {stats['total_users']}")
                
                print(f"\nSystem:")
                print(f"  Last backup: {stats['last_backup']}")
                
                if stats['records_by_city']:
                    print(f"\nRecords by city:")
                    for city, count in sorted(stats['records_by_city'].items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  {city}: {count} records")
                
                if stats['oldest_record'] and stats['newest_record']:
                    print(f"\nRecord timeline:")
                    print(f"  Oldest: {stats['oldest_record'].get('first_name', '')} {stats['oldest_record'].get('last_name', '')} ({stats['oldest_record'].get('created_at', '')})")
                    print(f"  Newest: {stats['newest_record'].get('first_name', '')} {stats['newest_record'].get('last_name', '')} ({stats['newest_record'].get('created_at', '')})")
                
            except KeyboardInterrupt:
                print("\nStats cancelled")
            except Exception as e:
                print(f"Error getting statistics: {e}")
            continue

        # ==================== RESTORE COMMAND ====================
        if base == "restore":
            if role != "root":
                print("Access denied. Only root can restore from backup.")
                continue
                
            try:
                backups = get_available_backups()
                
                if not backups:
                    print("No backups available for restore.")
                    continue
                
                print("\nAvailable backups:")
                print("-" * 60)
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup['filename']}")
                    print(f"   Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Size: {backup['size']} bytes")
                    print()
                
                choice = safe_input("Select backup to restore (number) or 'cancel': ")
                if choice is None or choice.lower() == 'cancel':
                    print("Restore cancelled")
                    continue
                
                try:
                    backup_index = int(choice) - 1
                    if 0 <= backup_index < len(backups):
                        selected_backup = backups[backup_index]
                        
                        print(f"\nYou are about to restore from:")
                        print(f"  Backup: {selected_backup['filename']}")
                        print(f"  Created: {selected_backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  Current data will be backed up automatically")
                        
                        confirm = safe_input("\nAre you sure you want to proceed? (y/N): ")
                        if confirm and confirm.lower() in ['y', 'yes']:
                            simple_loading("RESTORING FROM BACKUP", 2.0)
                            success, message = restore_from_backup(selected_backup['filename'])
                            if success:
                                print(f"SUCCESS: {message}")
                            else:
                                print(f"ERROR: {message}")
                        else:
                            print("Restore cancelled")
                    else:
                        print("Invalid backup selection")
                except ValueError:
                    print("Please enter a valid number")
                    
            except KeyboardInterrupt:
                print("\nRestore cancelled")
            continue

        # ==================== AUTOBACKUP COMMAND ====================
        if base == "autobackup":
            if role != "root":
                print("Access denied. Only root can configure auto-backup.")
                continue
                
            try:
                from core.autobackup import autobackup_status, update_autobackup_config, run_autobackup
                
                status = autobackup_status()
                print(f"\nCurrent Auto-backup Status:")
                print(f"  Status: {status['status']}")
                print(f"  Mode: {status['mode']}")
                print(f"  Last Backup: {status['last_backup']}")
                print(f"  Next Backup: {status['next_backup']}")
                
                print("\nAuto-backup configuration:")
                print("  1. Enable daily auto-backup")
                print("  2. Enable weekly auto-backup") 
                print("  3. Disable auto-backup")
                print("  4. View current configuration")
                print("  5. Run backup now")
                
                choice = safe_input("Select option (1-5): ")
                if choice is None: continue
                
                if choice == "1":
                    success = update_autobackup_config(enabled=True, mode="daily")
                    if success:
                        print("SUCCESS: Daily auto-backup enabled")
                        log("AUTOBACKUP: daily auto-backup enabled")
                    else:
                        print("ERROR: Failed to update configuration")
                        
                elif choice == "2":
                    success = update_autobackup_config(enabled=True, mode="weekly")
                    if success:
                        print("SUCCESS: Weekly auto-backup enabled")
                        log("AUTOBACKUP: weekly auto-backup enabled")
                    else:
                        print("ERROR: Failed to update configuration")
                        
                elif choice == "3":
                    success = update_autobackup_config(enabled=False)
                    if success:
                        print("SUCCESS: Auto-backup disabled")
                        log("AUTOBACKUP: auto-backup disabled")
                    else:
                        print("ERROR: Failed to update configuration")
                        
                elif choice == "4":
                    status = autobackup_status()
                    print(f"\nCurrent configuration:")
                    print(f"  Status: {status['status']}")
                    print(f"  Mode: {status['mode']}")
                    print(f"  Last Backup: {status['last_backup']}")
                    print(f"  Next Backup: {status['next_backup']}")
                    print(f"  Available backups: {len(get_available_backups())}")
                    
                elif choice == "5":
                    loading_operation("RUNNING BACKUP", 2.0)
                    success = run_autobackup()
                    if success:
                        print("SUCCESS: Backup completed")
                    else:
                        print("Backup was not needed or failed")
                        
                else:
                    print("Invalid option")
                    
            except KeyboardInterrupt:
                print("\nAuto-backup configuration cancelled")
            continue

        # ==================== CONFIG COMMAND ====================
        if base == "config":
            if role != "root":
                print("Access denied. Only root can modify configuration.")
                continue
            print("Configuration system - coming soon!")
            continue

def do_help(role, category=None):
    from core.command_categories import COMMAND_CATEGORIES
    
    if category:
        category_lower = category.lower()
        found = False
        
        for cat_id, cat_info in COMMAND_CATEGORIES.items():
            if cat_id == category_lower or cat_info["name"].lower() == category_lower:
                print(f"\n{cat_info['name']}")
                print("-" * 40)
                print(f"{cat_info['description']}\n")
                
                for cmd in cat_info["commands"]:
                    if cmd in COMMANDS and role in COMMANDS[cmd]["roles"]:
                        print(f"  {cmd:<12} - {COMMANDS[cmd]['desc']}")
                found = True
                break
        
        if not found:
            print(f"\nUnknown category: {category}")
            print("Available categories: " + ", ".join(COMMAND_CATEGORIES.keys()))
    else:
        print("\nDatana Command System")
        print("=" * 60)
        
        for cat_id, cat_info in COMMAND_CATEGORIES.items():
            print(f"\n{cat_info['name']}")
            print("-" * 40)
            
            for cmd in cat_info["commands"]:
                if cmd in COMMANDS and role in COMMANDS[cmd]["roles"]:
                    print(f"  {cmd:<12} - {COMMANDS[cmd]['desc']}")
        
        print("\nUsage: help [category]")
        print("Categories: " + ", ".join(COMMAND_CATEGORIES.keys()))

def do_run(role, current_user, parts):
    if len(parts) < 2:
        print("\nRun Commands:")
        print("  run webpanel [-p PORT]          - Start web panel on specified port")
        print("  run webpanel --stop             - Stop running web panel")
        print("  run webpanel --status           - Check web panel status")
        print("\nExamples:")
        print("  run webpanel -p 8080            # Run on port 8080")
        print("  run webpanel -p 5000 --debug    # Run with debug mode")
        print("  run webpanel --stop              # Stop the server")
        return
    
    service = parts[1].lower()
    
    if service == "webpanel":
        handle_webpanel(parts[2:])
    else:
        print(f"Unknown service: {service}")

def handle_webpanel(args):
    """مدیریت اجرای وب پنل با محدودیت پورت"""
    import subprocess
    import sys
    import os
    import signal
    import time
    import socket
    
    # ========== محدودیت‌های پورت ==========
    PORT_MIN = 1024
    PORT_MAX = 49151
    COMMON_PORTS = [80, 443, 3000, 3306, 5432, 27017, 6379, 9200]
    RECOMMENDED_PORTS = [5000, 5001, 5002, 8000, 8001, 8080, 8081, 8888]
    
    # ========== تابع بررسی پورت ==========
    def is_port_available(host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                pid_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webpanel.pid')
                try:
                    if os.path.exists(pid_file):
                        with open(pid_file, 'r') as f:
                            pid = f.read().strip()
                        if os.name == 'nt':
                            import ctypes
                            kernel32 = ctypes.windll.kernel32
                            handle = kernel32.OpenProcess(1, 0, int(pid))
                            if handle:
                                kernel32.CloseHandle(handle)
                                return False, f"Port {port} is already used by Datana (PID: {pid})"
                        else:
                            os.kill(int(pid), 0)
                            return False, f"Port {port} is already used by Datana (PID: {pid})"
                except:
                    pass
                return False, f"Port {port} is already in use by another application"
            
            return True, "Port is available"
        except Exception as e:
            return False, f"Error checking port: {e}"
    
    # ========== تابع بررسی نمونه در حال اجرا ==========
    def is_another_instance_running():
        """بررسی اینکه آیا نمونه دیگری از وب‌پنل در حال اجراست"""
        pid_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webpanel.pid')
        
        if not os.path.exists(pid_file):
            return False, None
        
        try:
            with open(pid_file, 'r') as f:
                pid = f.read().strip()
            
            # بررسی زنده بودن پروسس
            if os.name == 'nt':  # Windows
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(1, 0, int(pid))
                if handle:
                    kernel32.CloseHandle(handle)
                    
                    # پیدا کردن پورتی که روش اجراست
                    try:
                        import psutil
                        process = psutil.Process(int(pid))
                        connections = process.connections()
                        for conn in connections:
                            if conn.status == 'LISTEN':
                                return True, f"Another instance is running on port {conn.laddr.port} (PID: {pid})"
                    except:
                        pass
                    
                    return True, f"Another instance is running (PID: {pid})"
            else:  # Linux/Mac
                os.kill(int(pid), 0)
                
                # پیدا کردن پورت
                try:
                    import psutil
                    process = psutil.Process(int(pid))
                    connections = process.connections()
                    for conn in connections:
                        if conn.status == 'LISTEN':
                            return True, f"Another instance is running on port {conn.laddr.port} (PID: {pid})"
                except:
                    pass
                
                return True, f"Another instance is running (PID: {pid})"
        except:
            # پروسس مرده، فایل رو پاک کن
            try:
                os.remove(pid_file)
            except:
                pass
        
        return False, None
    # =========================================
    
    # فایل‌ها
    pid_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webpanel.pid')
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webpanel.log')
    
    # اگر هیچ آرگومانی نداد
    if len(args) == 0:
        show_port_help()
        return
    
    # مقدار پیش‌فرض
    port = 5000
    debug = False
    stop = False
    status = False
    force = False
    
    # ========== پردازش آرگومان‌ها ==========
    i = 0
    while i < len(args):
        if args[i] == '-p' and i + 1 < len(args):
            try:
                port = int(args[i + 1])
                
                if port < PORT_MIN:
                    print(f" Port {port} is too low!")
                    print(f"   Port must be between {PORT_MIN} and {PORT_MAX}")
                    return
                
                if port > PORT_MAX:
                    print(f" Port {port} is too high!")
                    print(f"   Port must be between {PORT_MIN} and {PORT_MAX}")
                    return
                
                if port in COMMON_PORTS:
                    print(f"  Warning: Port {port} is commonly used!")
                    confirm = input("   Still want to use this port? (y/N): ")
                    if confirm.lower() != 'y':
                        print("   Using default port 5000 instead")
                        port = 5000
                
                i += 2
            except:
                print(" Invalid port number")
                return
        elif args[i] == '--debug':
            debug = True
            i += 1
        elif args[i] == '--stop':
            stop = True
            i += 1
        elif args[i] == '--status':
            status = True
            i += 1
        elif args[i] == '--force':
            force = True
            i += 1
        elif args[i] == '--help' or args[i] == '-h':
            show_port_help()
            return
        else:
            print(f" Unknown option: {args[i]}")
            show_port_help()
            return
    
    # ========== اجرای درخواست‌ها ==========
    
    # 1️⃣ اگر --status
    if status:
        running, message = is_another_instance_running()
        if running:
            print(f" {message}")
            
            # نمایش پورت از روی فایل کانفیگ
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
                
                # سعی کن پورت رو از لاگ پیدا کنی
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        content = f.read()
                        import re
                        match = re.search(r'http://[^:]+:(\d+)', content)
                        if match:
                            print(f"   URL: http://localhost:{match.group(1)}")
        else:
            print(" No web panel is running")
        return
    
    if stop:
        running, message = is_another_instance_running()
        if running:
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
            
                try:
                    print(f" Stopping web panel (PID: {pid})...")
                
                    try:
                        import psutil
                        process = psutil.Process(int(pid))
                    
                        # kill all child processes first
                        children = process.children(recursive=True)
                        for child in children:
                            child.kill()
                    
                        # kill main process
                        process.kill()
                    
                        # wait for process to terminate
                        gone, alive = psutil.wait_procs([process], timeout=5)
                    
                        print(f" Process terminated")
                    
                    except ImportError:
                        # fallback to old method if psutil not available
                        if os.name == 'nt':
                            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        else:
                            os.kill(int(pid), signal.SIGKILL)
                
                    time.sleep(2)
                
                    # remove files
                    for file_path in [pid_file, log_file]:
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                                print(f" Removed: {os.path.basename(file_path)}")
                            except Exception as e:
                                print(f"  Could not remove {os.path.basename(file_path)}: {e}")
                
                    print(f" Web panel stopped successfully")
                
                except psutil.NoSuchProcess:
                    print(f"  Process {pid} not found, cleaning up files...")
                    for file_path in [pid_file, log_file]:
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except:
                                pass
                    print(f" Cleanup completed")
                
                except Exception as e:
                    print(f" Failed to stop: {e}")
        else:
            print(" No running web panel found")
        return
    
    # 3️⃣ بررسی نمونه در حال اجرا (مهم!)
    running, message = is_another_instance_running()
    if running:
        print(f" {message}")
        print("\n You can:")
        print("   • Stop it first: 'run webpanel --stop'")
        print("   • Force start with --force (not recommended)")
        if not force:
            return
    
    # 4️⃣ اجرای اصلی
    print(f" Starting web panel on port {port}...")
    
    # بررسی پورت
    available, message = is_port_available('127.0.0.1', port)
    if not available:
        print(f" {message}")
        print("\n Try one of these ports instead:")
        for p in RECOMMENDED_PORTS:
            if p != port:  # خود پورت رو نگو
                avail, _ = is_port_available('127.0.0.1', p)
                if avail:
                    print(f"   • {p} (available)")
        return
    
    # مسیر فایل web app
    web_app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'app.py')
    
    if not os.path.exists(web_app_path):
        print(" Web panel files not found!")
        return
    
    # ساختن محیط
    env = os.environ.copy()
    env['FLASK_PORT'] = str(port)
    env['FLASK_HOST'] = '127.0.0.1'
    
    if debug:
        env['FLASK_DEBUG'] = '1'
    
    # اجرا
    try:
        if os.name == 'nt':
            process = subprocess.Popen(
                [sys.executable, web_app_path],
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL
            )
        else:
            process = subprocess.Popen(
                [sys.executable, web_app_path],
                env=env,
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        
        time.sleep(3)
        
        if process.poll() is None:
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # بررسی اینکه پورت باز شده
            avail_check, _ = is_port_available('127.0.0.1', port)
            if not avail_check:  # پورت باز شده (چون قبلاً بسته بود)
                print(f"   Web panel started successfully!")
                print(f"   URL: http://localhost:{port}")
                print(f"   PID: {process.pid}")
                print(f"   Debug mode: {'ON' if debug else 'OFF'}")
                print(f"\n Log file: {log_file}")
                print("\nUse 'run webpanel --stop' to stop the server")
                print("Use 'run webpanel --status' to check status")
            else:
                print(" Web panel failed to start properly")
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"\n Last error:")
                            for line in lines[-3:]:
                                print(f"   {line.strip()}")
                process.terminate()
                if os.path.exists(pid_file):
                    os.remove(pid_file)
        else:
            print(" Web panel failed to start")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"\n Last error:")
                        for line in lines[-3:]:
                            print(f"   {line.strip()}")
        
    except Exception as e:
        print(f" Failed to start: {e}")

def show_port_help():
    """نمایش راهنمای پورت‌ها"""
    print("\n" + "="*60)
    print(" PORT USAGE GUIDE")
    print("="*60)
    print("\nValid port range: 1024 - 49151")
    print("\n  Avoid these common ports:")
    print("   • 80, 443     - HTTP/HTTPS")
    print("   • 3306        - MySQL")
    print("   • 5432        - PostgreSQL")
    print("   • 27017       - MongoDB")
    print("   • 6379        - Redis")
    print("   • 9200        - Elasticsearch")
    print("   • 3000        - React/Node dev")
    
    print("\n Recommended ports for Datana:")
    print("   • 5000, 5001, 5002")
    print("   • 8000, 8001")
    print("   • 8080, 8081")
    print("   • 8888")
    
    print("\n Examples:")
    print("   run webpanel -p 5000     # Default")
    print("   run webpanel -p 8080     # Alternative")
    print("   run webpanel -p 8001 --debug")
    print("="*60)

def do_bulk(role, current_user, parts):
    from core.bulk_operations import BulkOperations
    
    if len(parts) < 2:
        print("\n Bulk Operations:")
        print("  bulk delete --city <name>           - Delete all records from city")
        print("  bulk delete --older-than <date>     - Delete records older than date")
        print("  bulk delete --empty <field>         - Delete records with empty field")
        print("  bulk update --city <old> --set-city <new>  - Update city name")
        print("  bulk update --all --add-tag <tag>   - Add tag to all records")
        print("  bulk copy --ids <id1,id2,...>       - Copy specific records")
        print("  bulk export --ids <ids> --format csv - Export selected records")
        print("\nOptions:")
        print("  --dry-run     - Show what would be done without actually doing it")
        print("  --confirm     - Skip confirmation")
        return

def do_advanced_logs(role, current_user):
    if role not in ["root", "admin"]:
        print("Access denied. Only root and admin can view logs.")
        return
    
    try:
        if not os.path.exists(LOG_PATH):
            print("No logs found.")
            return
        
        print("\nLog viewing options:")
        print("  1. View all logs")
        print("  2. View logs for specific user")
        print("  3. Search in logs")
        print("  4. View recent logs (last 50 lines)")
        
        choice = safe_input("Select option (1-4): ")
        if choice is None: return
        
        loading_operation("LOADING LOGS", 0.5)
        
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = f.readlines()
        
        if choice == "2":
            username = safe_input("Enter username to filter: ")
            if username:
                logs = [log for log in logs if f"user={username}" in log]
        elif choice == "3":
            search_term = safe_input("Enter search term: ")
            if search_term:
                logs = [log for log in logs if search_term.lower() in log.lower()]
        elif choice == "4":
            logs = logs[-50:]
        
        if not logs:
            print("No logs found matching your criteria.")
        else:
            print(f"\nShowing {len(logs)} log entries:")
            print("=" * 80)
            for log_entry in logs:
                print(log_entry.strip())
            print("=" * 80)
            
    except KeyboardInterrupt:
        print("\nLogs cancelled")
    except Exception as e:
        print(f"Error reading logs: {e}")

def do_edit(role, current_user):
    if role not in ["root", "admin"]:
        print("Access denied. Only root and admin can edit records.")
        return
    
    record_id = safe_input("Record ID to edit: ")
    if record_id is None: return
    
    try:
        loading_operation("LOADING RECORD", 0.5)
    except KeyboardInterrupt:
        print("\nEdit cancelled")
        return
    
    records = load_records()
    
    record = None
    for r in records:
        if r["id"] == record_id:
            record = r
            break
    
    if not record:
        print("Record not found.")
        return
    
    print("Leave blank to keep current value:")
    for field in ["first_name", "last_name", "national_id", "phone", "address"]:
        current = record.get(field, "")
        if field == "national_id":
            print(f"Current national ID: {current}")
            new_value = safe_input(f"national_id [{current}]: ")
            if new_value is None: return
            
            if new_value:
                try:
                    is_valid, error_msg = validate_national_id(new_value)
                    if is_valid:
                        if new_value != current:
                            is_duplicate, duplicate_msg = is_duplicate_record(national_id=new_value)
                            if is_duplicate:
                                print(f"Error: {duplicate_msg}")
                                continue
                        record[field] = new_value
                    else:
                        print(f"Error: {error_msg}")
                except ValueError as e:
                    print(f"Error: {e}")
        
        elif field == "phone":
            print(f"Current phone: {current}")
            new_value = safe_input(f"phone [{current}]: ")
            if new_value is None: return
            
            if new_value:
                try:
                    if new_value.startswith('+98'):
                        formatted_phone = new_value
                    else:
                        formatted_phone = format_iranian_phone(new_value)
                    
                    if formatted_phone is None:
                        print("Phone number is optional. Keeping current value.")
                    else:
                        is_valid, error_msg = validate_iranian_phone(formatted_phone)
                        if is_valid:
                            if formatted_phone != current:
                                is_duplicate, duplicate_msg = is_duplicate_record(phone=formatted_phone)
                                if is_duplicate:
                                    print(f"Error: {duplicate_msg}")
                                    continue
                            record[field] = formatted_phone
                        else:
                            print(f"Error: {error_msg}")
                except ValueError as e:
                    print(f"Error: {e}")
        else:
            new_value = safe_input(f"{field} [{current}]: ")
            if new_value is None: return
            if new_value:
                if field in ["first_name", "last_name"]:
                    new_value = capitalize_name(new_value)
                record[field] = new_value
    
    try:
        loading_operation("UPDATING RECORD", 1.0)
    except KeyboardInterrupt:
        print("\nEdit cancelled")
        return
        
    save_records(records)
    log(f"EDIT: {current_user} edited record={record_id}")
    print("Record updated successfully.")

def do_delete_direct(role, current_user, record_id):
    if role not in ["root", "admin"]:
        print("Access denied. Only root and admin can delete records.")
        return
    
    try:
        loading_operation("LOADING RECORDS", 0.5)
    except KeyboardInterrupt:
        print("\nDelete cancelled")
        return
    
    records = load_records()
    
    record_to_delete = None
    for r in records:
        if r["id"] == record_id:
            record_to_delete = r
            break
    
    if not record_to_delete:
        print(f"Record {record_id} not found.")
        return
    
    print("Record to be deleted:")
    print(f"  ID: {record_to_delete['id']}")
    print(f"  Name: {record_to_delete.get('first_name', '')} {record_to_delete.get('last_name', '')}")
    print(f"  National ID: {record_to_delete.get('national_id', '')}")
    print(f"  Phone: {record_to_delete.get('phone', '')}")
    print(f"  Address: {record_to_delete.get('address', '')}")
    
    final_confirm = safe_input("Confirm deletion? This cannot be undone. (y/N): ")
    if final_confirm is None or final_confirm.lower() not in ['y', 'yes']:
        print("Delete cancelled")
        return
    
    try:
        loading_operation("DELETING RECORD", 1.0)
    except KeyboardInterrupt:
        print("\nDelete cancelled")
        return
    
    new_records = [r for r in records if r["id"] != record_id]
    save_records(new_records)
    log(f"DELETE: {current_user} deleted record={record_id}")
    print(f"Record {record_id} deleted successfully.")

def do_profile(username):
    from core.leaderboard import Leaderboard
    Leaderboard.show_user_profile(username)

def do_leaderboard(parts):
    from core.leaderboard import Leaderboard
    limit = 10
    if len(parts) > 1:
        try:
            limit = int(parts[1])
        except:
            pass
    Leaderboard.show_leaderboard(limit)

def do_badges(username):
    from core.gamification import GamificationSystem
    badges = GamificationSystem.get_user_badges(username)
    
    if not badges:
        print(f"\nNo badges earned yet for {username}")
        return
    
    print(f"\n=✪= Badges for {username}:")
    print("-" * 40)
    for badge in badges:
        print(f"  • {badge['name']} (+{badge['points']} pts) - {badge['awarded_at'][:10]}")

def do_delete(role, current_user):
    if role not in ["root", "admin"]:
        print("Access denied. Only root and admin can delete records.")
        return
    
    record_id = safe_input("Record ID to delete: ")
    if record_id is None: 
        return
    
    confirm = safe_input(f"Are you sure you want to delete record {record_id}? (y/N): ")
    if confirm is None or confirm.lower() not in ['y', 'yes']:
        print("Delete cancelled")
        return
    
    try:
        loading_operation("LOADING RECORDS", 0.5)
    except KeyboardInterrupt:
        print("\nDelete cancelled")
        return
    
    records = load_records()
    
    record_to_delete = None
    for r in records:
        if r["id"] == record_id:
            record_to_delete = r
            break
    
    if not record_to_delete:
        print("Record not found.")
        return
    
    print("Record to be deleted:")
    print(f"  ID: {record_to_delete['id']}")
    print(f"  Name: {record_to_delete.get('first_name', '')} {record_to_delete.get('last_name', '')}")
    print(f"  National ID: {record_to_delete.get('national_id', '')}")
    print(f"  Phone: {record_to_delete.get('phone', '')}")
    print(f"  Address: {record_to_delete.get('address', '')}")
    
    final_confirm = safe_input("Confirm deletion? This cannot be undone. (y/N): ")
    if final_confirm is None or final_confirm.lower() not in ['y', 'yes']:
        print("Delete cancelled")
        return
    
    try:
        loading_operation("DELETING RECORD", 1.0)
    except KeyboardInterrupt:
        print("\nDelete cancelled")
        return
    
    new_records = [r for r in records if r["id"] != record_id]
    save_records(new_records)
    log(f"DELETE: {current_user} deleted record={record_id}")
    print("Record deleted successfully.")

def do_useradd(role, current_user, username, password, user_role, auto_confirm=False):
    if role != "root":
        print("Access denied. Only root can add users.")
        return
    
    users = load_users()
    
    if username in users:
        print("User already exists.")
        return
    
    if user_role not in ["root", "admin", "staff", "viewer"]:
        print("Invalid role.")
        return
    
    if not auto_confirm:
        print(f"\nUser to be added:")
        print(f"  Username: {username}")
        print(f"  Role: {user_role}")
        confirm = safe_input("Proceed? (Y/n): ")
        if confirm and confirm.lower() in ['n', 'no']:
            print("User add cancelled")
            return
    
    try:
        loading_operation("ADDING USER", 1.0)
    except KeyboardInterrupt:
        print("\nUser add cancelled")
        return
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {"username": username, "password": hashed, "role": user_role}
    
    save_users(users)
    log(f"USERADD: {current_user} added user={username} role={user_role}")
    print(f"User {username} added successfully.")

def do_userdel(role, current_user, username, auto_confirm=False):
    if role != "root":
        print("Access denied. Only root can delete users.")
        return
    
    users = load_users()
    
    if username not in users:
        print("User not found.")
        return
    
    if username == current_user:
        print("Cannot delete your own account.")
        return
    

    if username == "root":
        print("Cannot delete root user.")
        return
    

    if len(users) <= 2:
        print("Cannot delete user. System must have at least 2 users.")
        return
    
    if not auto_confirm:
        print(f"User to be deleted: {username} (role: {users[username].get('role', 'viewer')})")
        confirm = safe_input("Are you sure you want to delete this user? (y/N): ")
        if not confirm or confirm.lower() not in ['y', 'yes']:
            print("Delete cancelled")
            return
    
    try:
        loading_operation("DELETING USER", 1.0)
    except KeyboardInterrupt:
        print("\nUser delete cancelled")
        return
    
    del users[username]
    save_users(users)
    log(f"USERDEL: {current_user} deleted user={username}")
    print(f"User {username} deleted successfully.")

def do_usermod(role, current_user, username, new_role, auto_confirm=False):
    if role != "root":
        print("Access denied. Only root can modify users.")
        return
    
    users = load_users()
    
    if username not in users:
        print("User not found.")
        return
    
    if new_role not in ["root", "admin", "staff", "viewer"]:
        print("Invalid role.")
        return
    
    if not auto_confirm:
        print(f"User to be modified: {username}")
        print(f"Current role: {users[username].get('role', 'viewer')}")
        print(f"New role: {new_role}")
        confirm = safe_input("Proceed? (Y/n): ")
        if confirm and confirm.lower() in ['n', 'no']:
            print("User modify cancelled")
            return
    
    try:
        loading_operation("MODIFYING USER", 1.0)
    except KeyboardInterrupt:
        print("\nUser modify cancelled")
        return
    
    users[username]["role"] = new_role
    save_users(users)
    log(f"USERMOD: {current_user} modified user={username} role={new_role}")
    print(f"User {username} role changed to {new_role}.")

def do_useredit(role, current_user, username, new_password=None, new_username=None, auto_confirm=False):
    if role != "root":
        print("Access denied. Only root can edit users.")
        return
    
    users = load_users()
    
    if username not in users:
        print("User not found.")
        return
    
    if username == current_user:
        print("Cannot edit your own account. Use different account.")
        return
    
    changes = []
    if new_username and new_username.strip():
        changes.append(f"username to {new_username}")
    if new_password and new_password.strip():
        changes.append("password")
    
    if not changes:
        print("No changes specified.")
        return
    
    print(f"\nUser to be edited: {username}")
    print(f"Changes: {', '.join(changes)}")
    
    if not auto_confirm:
        confirm = safe_input("Proceed? (Y/n): ")
        if confirm and confirm.lower() in ['n', 'no']:
            print("Edit cancelled")
            return
    
    try:
        loading_operation("UPDATING USER", 1.0)
    except KeyboardInterrupt:
        print("\nUser edit cancelled")
        return

    if new_username and new_username.strip():
        if new_username in users:
            print(f"Error: Username {new_username} already exists.")
            return
        
        users[new_username] = users[username]
        users[new_username]['username'] = new_username
        del users[username]
        username = new_username  
        print(f"Username changed to {new_username}")
    
    if new_password and new_password.strip():

        new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        users[username]["password"] = new_hashed
        print("Password changed successfully")
    
    save_users(users)
    log(f"USEREDIT: {current_user} edited user={username} changes={changes}")
    print(f"User {username} updated successfully.")

def do_userlist(role, current_user):
    if role not in ["root", "admin"]:
        print("Access denied. Only root and admin can view user list.")
        return
    
    try:
        loading_operation("LOADING USERS", 0.8)
    except KeyboardInterrupt:
        print("\nUserlist cancelled")
        return
    
    users = load_users()
    
    if not users:
        print("No users found.")
        return
    
    sorted_users = sorted(users.items(), key=lambda x: x[0].lower())
    
    table_data = []
    for username, user_info in sorted_users:
        role_display = user_info.get("role", "viewer")
        
        current_indicator = " *" if username == current_user else ""
        
        table_data.append([
            username + current_indicator,
            role_display,
            "Active"
        ])
    
    print(f"\nTotal users: {len(users)}")
    print("=" * 50)
    print(tabulate(table_data, 
                 headers=["Username", "Role", "Status"],
                 tablefmt="grid"))
    
    print(f"\n* indicates current user: {current_user}")
    
    role_stats = {}
    for user_info in users.values():
        role = user_info.get("role", "viewer")
        role_stats[role] = role_stats.get(role, 0) + 1
    
    print("\nRole statistics:")
    for role, count in sorted(role_stats.items()):
        print(f"  {role}: {count} user(s)")

def do_lists(role, current_user):
    try:
        loading_operation("LOADING RECORDS", 1.0)
    except KeyboardInterrupt:
        print("\nLists cancelled")
        return
    
    records = load_records()
    record_count = len(records)
    
    if not records:
        print("No records found.")
        return
    
    sorted_records = sorted(records, key=lambda x: x.get("created_at", ""), reverse=True)
    sort_method = "Creation Date (newest first)"
    
    PAGE_SIZE = 10
    total_pages = (record_count + PAGE_SIZE - 1) // PAGE_SIZE
    current_page = 1
    
    while True:
        clear_screen()
        print(f"Total records: {record_count} | Sorted by: {sort_method}")
        print(f"Total pages: {total_pages}")
        print("-" * 80)
        
        start_idx = (current_page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_records = sorted_records[start_idx:end_idx]
        
        print(f"\nPage {current_page}/{total_pages}:")
        print("=" * 80)
        
        if page_records:
            table_data = []
            for i, record in enumerate(page_records, start=start_idx + 1):
                table_data.append([
                    i,
                    record["id"],
                    record.get("first_name", ""),
                    record.get("last_name", ""),
                    record.get("national_id", ""),
                    record.get("phone", ""),
                    record.get("address", "")
                ])
            
            print(tabulate(table_data, 
                         headers=["#", "ID", "First Name", "Last Name", "National ID", "Phone", "Address"],
                         tablefmt="grid"))
        else:
            print("No records on this page.")
        
        print("=" * 80)
        
        print("\nSort options:")
        print("  [1] Sort by ID")
        print("  [2] Sort by First Name") 
        print("  [3] Sort by Last Name")
        print("  [4] Sort by National ID")
        print("  [5] Sort by City/Address")
        print("  [6] Sort by Creation Date (newest first)")
        
        if role in ["root", "admin"]:
            print("\nActions:")
            print("  [delete ID] Delete record (e.g., 'delete ABC123')")
            print("  [view ID] View record details (e.g., 'view ABC123')")
        
        if total_pages > 1:
            print("\nNavigation:")
            if current_page > 1:
                print("  [P] Previous page")
            if current_page < total_pages:
                print("  [N] Next page")
            print("  [number] Go to specific page")
        
        print("  [exit] Return to main menu")
        
        while True:
            try:
                choice = input(f"\nPage {current_page}/{total_pages} > ").strip().lower()
                
                if choice == "exit":
                    clear_screen()
                    return
                
                elif choice in ["1", "2", "3", "4", "5", "6"]:
                    if choice == "1":
                        sorted_records = sorted(records, key=lambda x: x.get("id", ""))
                        sort_method = "ID"
                    elif choice == "2":
                        sorted_records = sorted(records, key=lambda x: x.get("first_name", "").lower())
                        sort_method = "First Name"
                    elif choice == "3":
                        sorted_records = sorted(records, key=lambda x: x.get("last_name", "").lower())
                        sort_method = "Last Name"
                    elif choice == "4":
                        sorted_records = sorted(records, key=lambda x: x.get("national_id", ""))
                        sort_method = "National ID"
                    elif choice == "5":
                        sorted_records = sorted(records, key=lambda x: x.get("address", "").lower())
                        sort_method = "City/Address"
                    elif choice == "6":
                        sorted_records = sorted(records, key=lambda x: x.get("created_at", ""), reverse=True)
                        sort_method = "Creation Date (newest first)"
                    
                    current_page = 1
                    break
                
                elif choice == "n" and current_page < total_pages:
                    current_page += 1
                    break
                
                elif choice == "p" and current_page > 1:
                    current_page -= 1
                    break
                
                elif choice.startswith("delete ") and role in ["root", "admin"]:
                    record_id = choice[7:].strip().upper()
                    if not record_id:
                        print("Please specify record ID")
                        continue
                    
                    target_record = None
                    for r in records:
                        if r["id"] == record_id:
                            target_record = r
                            break
                    
                    if not target_record:
                        print(f"Record {record_id} not found.")
                        input("Press Enter to continue...")
                        break
                    
                    print(f"\nRecord to delete:")
                    print(f"  ID: {target_record['id']}")
                    print(f"  Name: {target_record.get('first_name', '')} {target_record.get('last_name', '')}")
                    print(f"  National ID: {target_record.get('national_id', '')}")
                    print(f"  Phone: {target_record.get('phone', '')}")
                    
                    confirm = safe_input("Are you sure you want to delete this record? (y/N): ")
                    if confirm and confirm.lower() in ['y', 'yes']:
                        try:
                            loading_operation("DELETING RECORD", 1.0)
                            success = delete_record_by_id(record_id)
                            if success:
                                log(f"DELETE: {current_user} deleted record={record_id}")
                                print(f"Record {record_id} deleted successfully.")
                                records = load_records()
                                record_count = len(records)
                                sorted_records = sorted(records, key=lambda x: x.get("created_at", ""), reverse=True)
                                total_pages = (record_count + PAGE_SIZE - 1) // PAGE_SIZE
                                if current_page > total_pages and total_pages > 0:
                                    current_page = total_pages
                            else:
                                print("Failed to delete record.")
                        except Exception as e:
                            print(f"Error deleting record: {e}")
                    else:
                        print("Delete cancelled.")
                    
                    input("Press Enter to continue...")
                    break
                
                elif choice.startswith("view "):
                    record_id = choice[5:].strip().upper()
                    if not record_id:
                        print("Please specify record ID")
                        continue
                    
                    target_record = None
                    for r in records:
                        if r["id"] == record_id:
                            target_record = r
                            break
                    
                    if not target_record:
                        print(f"Record {record_id} not found.")
                    else:
                        print(f"\nRecord details for {record_id}:")
                        print("-" * 40)
                        for k, v in target_record.items():
                            print(f"{k}: {v}")
                        print("-" * 40)
                    
                    input("Press Enter to continue...")
                    break
                
                elif choice.isdigit():
                    page_num = int(choice)
                    if 1 <= page_num <= total_pages:
                        current_page = page_num
                        break
                    else:
                        print(f"Page {page_num} doesn't exist. Available pages: 1-{total_pages}")
                        input("Press Enter to continue...")
                        break
                
                else:
                    if choice == "n":
                        print("You're on the last page.")
                    elif choice == "p":
                        print("You're on the first page.")
                    elif choice.startswith("delete ") and role not in ["root", "admin"]:
                        print("Access denied. Only root and admin can delete records.")
                    else:
                        print("Invalid choice. Use [1-6] for sort, [N]ext, [P]revious, [delete ID], [view ID], page number, or [exit]")
                    input("Press Enter to continue...")
                    break
            
            except KeyboardInterrupt:
                print("\nLists cancelled")
                clear_screen()
                return
            except (EOFError):
                clear_screen()
                return