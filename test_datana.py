import pytest
import os
import sys
import bcrypt
import json
from cryptography.fernet import Fernet

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import generate_default_users
from core.database import capitalize_name, format_iranian_phone, search_by_name_partial
from core.validators import DataValidator
from core.config_manager import get_or_create_config, get_encryption_key


class TestDatanaAuthentication:
    
    def test_password_verification(self):
        password = "securepassword123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        assert bcrypt.checkpw(password.encode(), hashed)
        assert not bcrypt.checkpw("wrongpassword".encode(), hashed)


class TestDatanaValidation:
    
    def test_english_name_validation(self):
        valid_name = "John"
        is_valid, message = DataValidator.validate_english_name(valid_name, "First name")
        assert is_valid == True
        
        invalid_name = "John123"
        is_valid, message = DataValidator.validate_english_name(invalid_name, "First name")
        assert is_valid == False
        
        invalid_name = "J"
        is_valid, message = DataValidator.validate_english_name(invalid_name, "First name")
        assert is_valid == False


class TestDatanaDatabase:
    
    def setup_method(self):
        self.test_records = [
            {
                "id": "TEST001",
                "first_name": "John",
                "last_name": "Doe",
                "national_id": "1234567890",
                "phone": "+989123456789",
                "address": "Tehran",
                "created_at": "2024-01-15 10:30:00"
            }
        ]
    
    def test_capitalize_name(self):
        assert capitalize_name("john") == "John"
        assert capitalize_name("JOHN") == "John"
        assert capitalize_name("jOhN") == "John"
        assert capitalize_name("") == ""
    
    def test_search_functionality(self):
        results = search_by_name_partial("John")
        assert isinstance(results, list)
        
        results = search_by_name_partial("Joh")
        assert isinstance(results, list)
        
        results = search_by_name_partial("john")
        assert isinstance(results, list)


class TestDatanaEncryption:
    
    def test_config_management(self):
        config = get_or_create_config()
        
        assert "DATANA_KEY" in config
        assert "version" in config
        assert "autobackup" in config
        
        key = get_encryption_key()
        fernet = Fernet(key)
        
        test_data = b"Test secret data"
        encrypted = fernet.encrypt(test_data)
        decrypted = fernet.decrypt(encrypted)
        
        assert decrypted == test_data
    
    def test_data_encryption(self):
        test_data = [{"id": "1", "name": "Test", "secret": "sensitive_data"}]
        
        key = get_encryption_key()
        fernet = Fernet(key)
        
        encrypted = fernet.encrypt(json.dumps(test_data).encode())
        
        encrypted_str = encrypted.decode('latin-1')
        assert "sensitive_data" not in encrypted_str
        assert "Test" not in encrypted_str


class TestDatanaIntegration:
    
    def test_user_workflow(self):
        users = generate_default_users()
        
        test_user = users["root"]
        stored_hash = test_user["password"].encode('utf-8')
        input_password = "root".encode('utf-8')
        
        assert bcrypt.checkpw(input_password, stored_hash)


def test_project_structure():
    required_files = [
        "project.py",
        "README.md", 
        "requirements.txt",
        "test_datana.py",
        "core/__init__.py",
        "core/auth.py",
        "core/database.py",
        "core/commands.py",
        "core/validators.py"
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing required file: {file_path}"


def test_requirements_file():
    assert os.path.exists("requirements.txt")
    
    with open("requirements.txt", "r") as f:
        requirements = f.read()
    
    required_packages = ["cryptography", "bcrypt", "tabulate", "psutil"]
    for package in required_packages:
        assert package in requirements, f"Missing package in requirements: {package}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])