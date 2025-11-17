# core/validators.py
import re
import random

class DataValidator:
    """اعتبارسنجی حرفه‌ای داده‌های ایرانی"""
    
    # الگوهای اعتبارسنجی
    PERSIAN_NAME_PATTERN = r'^[\u0600-\u06FF\s]+$'
    ENGLISH_NAME_PATTERN = r'^[a-zA-Z\s]+$'
    CITY_PATTERN = r'^[\u0600-\u06FFa-zA-Z\s\-\.]+$'
    NATIONAL_ID_PATTERN = r'^\d{10}$'
    PHONE_PATTERN = r'^\+98\d{10}$'
    
    # لیست اسامی و شهرهای مشکوک
    SUSPICIOUS_NAMES = {
        'test', 'admin', 'root', 'user', 'unknown', 'null', 'undefined',
        '123', '456', '789', '000', '111', '222', '333', '444', '555',
        '666', '777', '888', '999', '0123456789'
    }
    
    SUSPICIOUS_CITIES = {
        'test', 'unknown', 'null', 'undefined', '123', '000', '111'
    }

    @staticmethod
    def validate_city_name(city):
        """اعتبارسنجی نام شهر - اجباری"""
        if not city or not city.strip():
            return False, "City is required"
        
        city = city.strip()
        # بررسی طول
        if len(city) < 2:
            return False, "City name must be at least 2 characters"
        if len(city) > 30:
            return False, "City name cannot exceed 30 characters"
    
        # بررسی الگوی شهر (فقط حروف)
        if not re.match(DataValidator.CITY_PATTERN, city):
            return False, "City name can only contain letters and hyphens"
    
        # بررسی شهرهای مشکوک
        if city.lower() in DataValidator.SUSPICIOUS_CITIES:
            return False, "City name contains suspicious value"
    
        # بررسی اینکه فقط یک کلمه باشه (نه آدرس کامل)
        if len(city.split()) > 1:
            return False, "Please enter only city name (not full address)"
    
        return True, "Valid city name"

    @staticmethod
    def capitalize_city(city):
        """Capitalize first letter of city name"""
        if not city:
            return city
        return city[0].upper() + city[1:].lower()
    
    @staticmethod
    def capitalize_name(name):
        """Capitalize first letter of name"""
        if not name:
            return name
        return name[0].upper() + name[1:].lower()
    
    @staticmethod
    def validate_persian_name(name, field_name="Name"):
        """اعتبارسنجی اسم و فامیل فارسی"""
        if not name or not name.strip():
            return False, f"{field_name} cannot be empty"
        
        name = name.strip()
        
        # بررسی طول
        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters"
        if len(name) > 50:
            return False, f"{field_name} cannot exceed 50 characters"
        
        # بررسی الگوی فارسی
        if not re.match(DataValidator.PERSIAN_NAME_PATTERN, name):
            return False, f"{field_name} can only contain Persian letters and spaces"
        
        # بررسی اسامی مشکوک
        if name.lower() in DataValidator.SUSPICIOUS_NAMES:
            return False, f"{field_name} contains suspicious value"
        
        # بررسی تکرار حروف (مثل 'aaaa')
        if len(set(name)) < 2:
            return False, f"{field_name} appears to be invalid"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_english_name(name, field_name="Name"):
        """اعتبارسنجی اسم و فامیل انگلیسی"""
        if not name or not name.strip():
            return False, f"{field_name} cannot be empty"
        
        name = name.strip()
        
        # بررسی طول
        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters"
        if len(name) > 50:
            return False, f"{field_name} cannot exceed 50 characters"
        
        # بررسی الگوی انگلیسی
        if not re.match(DataValidator.ENGLISH_NAME_PATTERN, name):
            return False, f"{field_name} can only contain English letters and spaces"
        
        # بررسی اسامی مشکوک
        if name.lower() in DataValidator.SUSPICIOUS_NAMES:
            return False, f"{field_name} contains suspicious value"
        
        # بررسی تکرار حروف
        if len(set(name)) < 2:
            return False, f"{field_name} appears to be invalid"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_city(city):
        """اعتبارسنجی نام شهر"""
        if not city or not city.strip():
            return True, ""  # شهر اختیاری هست
        
        city = city.strip()
        
        # بررسی طول
        if len(city) < 2:
            return False, "City name must be at least 2 characters"
        if len(city) > 50:
            return False, "City name cannot exceed 50 characters"
        
        # بررسی الگوی شهر
        if not re.match(DataValidator.CITY_PATTERN, city):
            return False, "City name can only contain letters, spaces, and hyphens"
        
        # بررسی شهرهای مشکوک
        if city.lower() in DataValidator.SUSPICIOUS_CITIES:
            return False, "City name contains suspicious value"
        
        return True, "Valid city"
    
    @staticmethod
    def validate_national_id(national_id):
        """اعتبارسنجی پیشرفته کد ملی ایرانی - اجباری"""
        if not national_id or not national_id.strip():
            return False, "National ID is required"
        
        national_id = national_id.strip()
        # بررسی الگوی عددی
        if not re.match(DataValidator.NATIONAL_ID_PATTERN, national_id):
            return False, "National ID must be exactly 10 digits"
        
        # بررسی اینکه همه ارقام یکسان نباشند
        if len(set(national_id)) == 1:
            return False, "National ID cannot have all identical digits"
        
        # الگوریتم اعتبارسنجی کد ملی
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
        
        # بررسی کدهای ملی تستی معروف
        test_ids = {'1111111111', '1234567890', '0000000000', '9999999999'}
        if national_id in test_ids:
            return False, "Suspicious national ID detected"
        
        return True, "Valid national ID"
    
    @staticmethod
    def validate_iranian_phone(phone):
        """اعتبارسنجی پیشرفته شماره تلفن ایرانی - اجباری"""
        if not phone or not phone.strip():
            return False, "Phone is required"
        
        phone = phone.strip()
        # بررسی الگوی تلفن
        if not re.match(DataValidator.PHONE_PATTERN, phone):
            return False, "Invalid phone format. Correct format: +989123456789"
        
        # بررسی پیش‌شماره‌های معتبر ایران
        valid_prefixes = {
            '910', '911', '912', '913', '914', '915', '916', '917', '918', '919',  # همراه اول
            '930', '933', '935', '936', '937', '938', '939',  # ایرانسل
            '920', '921', '922', '923',  # رایتل
            '901', '902', '903', '904', '905', '941'  # سایر اپراتورها
        }
        
        prefix = phone[3:6]  # 3 رقم بعد از +98
        if prefix not in valid_prefixes:
            return False, "Invalid mobile operator prefix"
        
        # بررسی شماره‌های تستی مشکوک
        suspicious_numbers = {
            '+989111111111', '+989999999999', '+989000000000',
            '+989123456789', '+989987654321'
        }
        if phone in suspicious_numbers:
            return False, "Suspicious phone number detected"
        
        return True, "Valid phone number"
    
    @staticmethod
    def detect_anomaly(record):
        """تشخیص ناهنجاری در رکورد"""
        anomalies = []
        
        # بررسی نام‌های عددی
        if record.get('first_name') and record['first_name'].isdigit():
            anomalies.append("First name contains only numbers")
        
        if record.get('last_name') and record['last_name'].isdigit():
            anomalies.append("Last name contains only numbers")
        
        # بررسی شهر عددی
        if record.get('address') and record['address'].isdigit():
            anomalies.append("City contains only numbers")
        
        # بررسی طول غیرعادی
        if record.get('first_name') and len(record['first_name']) < 2:
            anomalies.append("First name is too short")
        
        if record.get('last_name') and len(record['last_name']) < 2:
            anomalies.append("Last name is too short")
        
        return anomalies
    
    @staticmethod
    def generate_security_score(record):
        """محاسبه امتیاز امنیتی رکورد"""
        score = 100
        
        # کسر امتیاز برای ناهنجاری‌ها
        anomalies = DataValidator.detect_anomaly(record)
        score -= len(anomalies) * 20
        
        # کسر برای فیلدهای خالی
        if not record.get('first_name'):
            score -= 10
        if not record.get('last_name'):
            score -= 10
        if not record.get('national_id'):
            score -= 15
        if not record.get('phone'):
            score -= 15
        if not record.get('address'):
            score -= 5
        
        # امتیاز برای داده‌های معتبر
        if record.get('national_id'):
            is_valid, _ = DataValidator.validate_national_id(record['national_id'])
            if is_valid:
                score += 10
        
        if record.get('phone'):
            is_valid, _ = DataValidator.validate_iranian_phone(record['phone'])
            if is_valid:
                score += 10
        
        return max(0, score)  # حداقل صفر