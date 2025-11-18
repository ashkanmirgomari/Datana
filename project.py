import os
import sys
import subprocess
import importlib


def initialize_system():
    from core.boot import BootManager
    BootManager.boot_sequence()
    return "System initialized successfully"


def get_system_info():
    import psutil
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    return {
        "memory_used": f"{memory.used // (1024**3)} GB",
        "memory_total": f"{memory.total // (1024**3)} GB", 
        "cpu_usage": f"{cpu_percent}%"
    }


def validate_user_input(data_type, value):
    from core.validators import DataValidator
    
    if data_type == "name":
        return DataValidator.validate_english_name(value, "Test name")
    elif data_type == "phone":
        return DataValidator.validate_iranian_phone(value)
    elif data_type == "national_id":
        return DataValidator.validate_national_id(value)
    else:
        return False, "Unknown data type"


def check_and_install_dependencies():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        return True
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing = []
        for package in requirements:
            package_name = package.split('==')[0].split('>=')[0].split('<=')[0]
            try:
                importlib.import_module(package_name)
            except ImportError:
                missing.append(package_name)
        
        if missing:
            print(f"[*] Installing missing packages: {', '.join(missing)}")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', requirements_file
                ], capture_output=True, text=True, check=True)
                print("[+] Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[-] Installation failed: {e.stderr}")
                return False
        
        return True
    except Exception as e:
        print(f"[-] Dependency check failed: {e}")
        return False


def main():
    if not check_and_install_dependencies():
        print("[!] CRITICAL: Failed to install dependencies")
        print("[!] Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    from core.boot import BootManager
    from core.commands import run_project_shell
    
    BootManager.boot_sequence()
    run_project_shell()


if __name__ == "__main__":
    main()