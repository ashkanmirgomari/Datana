import bcrypt
from core.config_manager import get_encryption_key
from cryptography.fernet import Fernet
import json
import os

def reset_root_password(new_password):
    users_path = "data/users.enc"
    
    if not os.path.exists(users_path):
        print("users.enc not found!")
        return
    
    key = get_encryption_key()
    fernet = Fernet(key)
    
    with open(users_path, "rb") as f:
        token = f.read()
    
    data = fernet.decrypt(token)
    users_list = json.loads(data.decode())
    
    # پیدا کردن کاربر root و تغییر پسورد
    for user in users_list:
        if user["username"] == "root":
            new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            user["password"] = new_hashed
            print("Root password updated!")
            break
    
    # ذخیره فایل
    data = json.dumps(users_list, ensure_ascii=False).encode()
    token = fernet.encrypt(data)
    
    with open(users_path, "wb") as f:
        f.write(token)
    
    print("Password reset complete!")

# اجرا
if __name__ == "__main__":
    new_pass = input("Enter new root password: ")
    reset_root_password(new_pass)