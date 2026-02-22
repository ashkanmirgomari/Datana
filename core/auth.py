# core/auth.py
import os, json
import bcrypt
from cryptography.fernet import Fernet
from core.utils import USERS_PATH
from core.logger import log
from core.config_manager import get_encryption_key

def generate_default_users():
    return users

def load_users():    
    if os.path.exists(USERS_PATH):
        try:
            key = get_encryption_key()
            with open(USERS_PATH, "rb") as f:
                token = f.read()
            fernet = Fernet(key)
            data = fernet.decrypt(token)
            users_list = json.loads(data.decode())
            return {u["username"]: u for u in users_list}
        except Exception:
            pass
    
    return generate_default_users()

def generate_default_users():
    import bcrypt
    
    root_hash = bcrypt.hashpw("root".encode(), bcrypt.gensalt()).decode()
    
    users = {
        "root": {
            "username": "root",
            "password": root_hash,
            "role": "root"
        },
    }
    return users

def save_users(users_dict):
    key = get_encryption_key()
    fernet = Fernet(key)
    users_list = list(users_dict.values())
    data = json.dumps(users_list, ensure_ascii=False).encode()
    token = fernet.encrypt(data)
    
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    
    with open(USERS_PATH, "wb") as fh:
        fh.write(token)

def verify(username, password):
    try:
        users = load_users()
    except Exception:
        return None
        
    user = users.get(username)
    if not user:
        log(f"LOGIN_FAIL: user={username}")
        return None
        
    stored_hash = user["password"].encode('utf-8')
    input_password = password.encode('utf-8')
    
    ok = bcrypt.checkpw(input_password, stored_hash)
    
    if ok:
        log(f"LOGIN: user={username}")
        return {"username": username, "role": user.get("role", "viewer")}
    else:
        log(f"LOGIN_FAIL: user={username}")
    return None