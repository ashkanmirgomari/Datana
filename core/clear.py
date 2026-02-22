# core/clear.py
import os
from core.utils import INFO

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    # reprint banner/info after clearing
    print(INFO)
