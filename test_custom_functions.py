import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import initialize_system, get_system_info, validate_user_input


def test_initialize_system():
    result = initialize_system()
    assert "initialized" in result.lower()
    assert "success" in result.lower()


def test_get_system_info():
    info = get_system_info()
    
    assert "memory_used" in info
    assert "memory_total" in info 
    assert "cpu_usage" in info
    assert "GB" in info["memory_used"]
    assert "%" in info["cpu_usage"]


def test_validate_user_input_name():
    is_valid, message = validate_user_input("name", "َAshkan")
    assert is_valid == True
    
    is_valid, message = validate_user_input("name", "Ashkan123")
    assert is_valid == False


def test_validate_user_input_phone():
    is_valid, message = validate_user_input("phone", "+989123456789")
    assert isinstance(is_valid, bool)


def test_validate_user_input_national_id():
    is_valid, message = validate_user_input("national_id", "1276297246")
    assert isinstance(is_valid, bool)