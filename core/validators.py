import re
import random

class DataValidator:
    
    PERSIAN_NAME_PATTERN = r'^[\u0600-\u06FF\s]+$'
    ENGLISH_NAME_PATTERN = r'^[a-zA-Z\s]+$'
    CITY_PATTERN = r'^[\u0600-\u06FFa-zA-Z\s\-\.]+$'
    NATIONAL_ID_PATTERN = r'^\d{10}$'
    PHONE_PATTERN = r'^\+98\d{10}$'
    
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
        if not city or not city.strip():
            return False, "City is required"
        
        city = city.strip()
        if len(city) < 2:
            return False, "City name must be at least 2 characters"
        if len(city) > 30:
            return False, "City name cannot exceed 30 characters"
        if not re.match(DataValidator.CITY_PATTERN, city):
            return False, "City name can only contain letters and hyphens"
    
        if city.lower() in DataValidator.SUSPICIOUS_CITIES:
            return False, "City name contains suspicious value"
    
        if len(city.split()) > 1:
            return False, "Please enter only city name (not full address)"
    
        return True, "Valid city name"

    @staticmethod
    def capitalize_city(city):
        if not city:
            return city
        return city[0].upper() + city[1:].lower()
    
    @staticmethod
    def capitalize_name(name):
        if not name:
            return name
        return name[0].upper() + name[1:].lower()
    
    @staticmethod
    def validate_persian_name(name, field_name="Name"):
        if not name or not name.strip():
            return False, f"{field_name} cannot be empty"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters"
        if len(name) > 50:
            return False, f"{field_name} cannot exceed 50 characters"
        

        if not re.match(DataValidator.PERSIAN_NAME_PATTERN, name):
            return False, f"{field_name} can only contain Persian letters and spaces"
        

        if name.lower() in DataValidator.SUSPICIOUS_NAMES:
            return False, f"{field_name} contains suspicious value"
        

        if len(set(name)) < 2:
            return False, f"{field_name} appears to be invalid"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_english_name(name, field_name="Name"):
        if not name or not name.strip():
            return False, f"{field_name} cannot be empty"
        
        name = name.strip()
        

        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters"
        if len(name) > 50:
            return False, f"{field_name} cannot exceed 50 characters"
        

        if not re.match(DataValidator.ENGLISH_NAME_PATTERN, name):
            return False, f"{field_name} can only contain English letters and spaces"
        

        if name.lower() in DataValidator.SUSPICIOUS_NAMES:
            return False, f"{field_name} contains suspicious value"
        

        if len(set(name)) < 2:
            return False, f"{field_name} appears to be invalid"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_city(city):
        if not city or not city.strip():
            return True, ""  
        city = city.strip()
        

        if len(city) < 2:
            return False, "City name must be at least 2 characters"
        if len(city) > 50:
            return False, "City name cannot exceed 50 characters"
        

        if not re.match(DataValidator.CITY_PATTERN, city):
            return False, "City name can only contain letters, spaces, and hyphens"
        
 
        if city.lower() in DataValidator.SUSPICIOUS_CITIES:
            return False, "City name contains suspicious value"
        
        return True, "Valid city"
    
    @staticmethod
    def validate_national_id(national_id):
        if not national_id or not national_id.strip():
            return False, "National ID is required"
        
        national_id = national_id.strip()
        if not re.match(DataValidator.NATIONAL_ID_PATTERN, national_id):
            return False, "National ID must be exactly 10 digits"
        
        if len(set(national_id)) == 1:
            return False, "National ID cannot have all identical digits"
        
        check_digit = int(national_id[9])
        total = 0
        
        for i in range(9):
            total += int(national_id[i]) * (10 - i)
        
        remainder = total % 11
        
        if remainder < 2:
            calculated_check = remainder
        else:
            calculated_check = 11 - remainder
        
        if calculated_check != check_digit:
            return False, "Invalid national ID"
        
        test_ids = {'1111111111', '1234567890', '0000000000', '9999999999'}
        if national_id in test_ids:
            return False, "Suspicious national ID detected"
        
        return True, "Valid national ID"
    
    @staticmethod
    def validate_iranian_phone(phone):
        if not phone or not phone.strip():
            return False, "Phone is required"
        
        phone = phone.strip()
        if not re.match(DataValidator.PHONE_PATTERN, phone):
            return False, "Invalid phone format. Correct format: +989123456789"
        

        valid_prefixes = {
            '910', '911', '912', '913', '914', '915', '916', '917', '918', '919',  
            '930', '933', '935', '936', '937', '938', '939', 
            '920', '921', '922', '923', 
            '901', '902', '903', '904', '905', '941' 
        }
    
        

        suspicious_numbers = {
            '+989111111111', '+989999999999', '+989000000000',
            '+989123456789', '+989987654321'
        }
        if phone in suspicious_numbers:
            return False, "Suspicious phone number detected"
        
        return True, "Valid phone number"
    
    @staticmethod
    def detect_anomaly(record):
        anomalies = []
        

        if record.get('first_name') and record['first_name'].isdigit():
            anomalies.append("First name contains only numbers")
        
        if record.get('last_name') and record['last_name'].isdigit():
            anomalies.append("Last name contains only numbers")
        

        if record.get('address') and record['address'].isdigit():
            anomalies.append("City contains only numbers")
        

        if record.get('first_name') and len(record['first_name']) < 2:
            anomalies.append("First name is too short")
        
        if record.get('last_name') and len(record['last_name']) < 2:
            anomalies.append("Last name is too short")
        
        return anomalies
    
    @staticmethod
    def generate_security_score(record):
        score = 100
        

        anomalies = DataValidator.detect_anomaly(record)
        score -= len(anomalies) * 20
        

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
        

        if record.get('national_id'):
            is_valid, _ = DataValidator.validate_national_id(record['national_id'])
            if is_valid:
                score += 10
        
        if record.get('phone'):
            is_valid, _ = DataValidator.validate_iranian_phone(record['phone'])
            if is_valid:
                score += 10
        
        return max(0, score)  