# core/utils.py
import os
from datetime import datetime

os.system("cls" if os.name == "nt" else "clear")
VERSION = "Datana v1.1.0.3"
COPYRIGHT = "© Ashkan Mirgomari"
BANNER = r"""
██████╗  █████╗ ████████╗ █████╗ ███╗   ██╗ █████╗ 
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗████╗  ██║██╔══██╗
██║  ██║███████║   ██║   ███████║██╔██╗ ██║███████║
██║  ██║██╔══██║   ██║   ██╔══██║██║╚██╗██║██╔══██║
██████╔╝██║  ██║   ██║   ██║  ██║██║ ╚████║██║  ██║
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
            mini-Local Database
"""
INFO = f"{BANNER}\n{VERSION}    {COPYRIGHT}\n"

# data dir (relative to project root)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/.."))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_PATH = os.path.join(DATA_DIR, "users.enc")
RECORDS_PATH = os.path.join(DATA_DIR, "records.enc")
LOG_PATH = os.path.join(DATA_DIR, "logs.txt")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def timestamp():
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")
