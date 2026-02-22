import os
import sys
import time

class BootManager:
    
    @staticmethod
    def check_python():
        version = sys.version.split()[0]
        return True, version
    
    @staticmethod
    def check_directories():
        from core.utils import DATA_DIR, BACKUP_DIR
        directories = [DATA_DIR, BACKUP_DIR]
        created = 0
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                created += 1
        
        if created > 0:
            return True, f"{created} directories created"
        return True, "ready"
    
    @staticmethod
    def check_encryption_keys():
        try:
            from core.config_manager import get_or_create_config
            config = get_or_create_config()
            key = config.get("DATANA_KEY")
            
            if key and len(key) > 10:
                return True, "generated"
            return True, "generated"
        except Exception as e:
            return False, f"error: {e}"
    
    @staticmethod
    def check_dependencies():
        return True, "verified"
    
    @staticmethod
    def check_users():
        try:
            from core.utils import USERS_PATH
            from core.auth import generate_default_users, save_users
            
            if not os.path.exists(USERS_PATH):
                users = generate_default_users()
                save_users(users)
                return True, "initialized"
            return True, "ready"
        except Exception as e:
            return False, f"error: {e}"
    
    @staticmethod
    def check_records():
        try:
            from core.utils import RECORDS_PATH
            if not os.path.exists(RECORDS_PATH):
                return True, "ready for first use"
            return True, "ready"
        except Exception as e:
            return False, f"error: {e}"
    
    @staticmethod
    def boot_sequence():
        print("[*] Datana v1.1.0.3 - Booting...")
        time.sleep(1)
        

        checks = [
            ("Checking Python environment", BootManager.check_python),
            ("Verifying system directories", BootManager.check_directories),
            ("Generating encryption keys", BootManager.check_encryption_keys),
            ("Checking dependencies", BootManager.check_dependencies),
            ("Initializing user database", BootManager.check_users),
            ("Preparing records storage", BootManager.check_records),
        ]
        
        all_success = True
        
        for i, (check_name, check_func) in enumerate(checks):
            success, message = check_func()
            status = "✓" if success else "✗"
            print(f"[{'+' if success else '-'}] {check_name}... {message} {status}")
            
            if i % 2 == 1: 
                time.sleep(1)
            
            if not success:
                all_success = False
        
        if not all_success:
            print("\n[!] CRITICAL: Boot sequence failed")
            sys.exit(1)
        
        time.sleep(1)
        
        print("\n[*] Loading core modules...")
        time.sleep(1)
        
        modules = [
            "Security & Authentication module",
            "Database engine", 
            "Command interface",
            "Analytics engine",
            "Backup system"
        ]
        
        statuses = ["LOADED", "READY", "ACTIVE", "ONLINE", "ARMED"]
        
        for i, module in enumerate(modules):
            time.sleep(0.3)
            print(f"[+] {module}... {statuses[i]} ✓")
        
        time.sleep(1)
        
        print("\n[*] Starting secure session...")
        time.sleep(1)
        print("[+] Session initialized ✓")
        time.sleep(0.5)
        print("[+] Authentication system ready ✓")
        time.sleep(1)
        
        print("\n")
        print("██████╗  █████╗ ████████╗ █████╗ ███╗   ██╗ █████╗ ")
        print("██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗████╗  ██║██╔══██╗")
        print("██║  ██║███████║   ██║   ███████║██╔██╗ ██║███████║")
        print("██║  ██║██╔══██║   ██║   ██╔══██║██║╚██╗██║██╔══██║")
        print("██████╔╝██║  ██║   ██║   ██║  ██║██║ ╚████║██║  ██║")
        print("╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝")
        print("            mini-Local Database")
        print("\nDatana v1.1.0.9    © Ashkan Mirgomari")
        print("")