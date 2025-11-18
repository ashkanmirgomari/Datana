import re
from core.validators import DataValidator

def parse_arguments(args, command):
    args_str = " ".join(args)
    
    patterns = {
        'useradd': {
            'username': r'-u\s+([^-]\S+)',
            'password': r'-p\s+([^-]\S+)',
            'role': r'-r\s+(root|admin|staff|viewer)'
        },
        'userdel': {
            'username': r'-u\s+([^-]\S+)'
        },
        'usermod': {
            'username': r'-u\s+([^-]\S+)',
            'role': r'-r\s+(root|admin|staff|viewer)'
        },
        'useredit': {
            'username': r'-u\s+([^-]\S+)',
            'new_password': r'-np\s+([^-]\S+)',
            'new_username': r'-nu\s+([^-]\S+)'
        },
        'add': {
            'first_name': r'-n\s+([^-]\S+)',
            'last_name': r'-l\s+([^-]\S+)',
            'national_id': r'-nt\s+(\d{10})',
            'phone': r'-p\s+(\+98\d{10})',
            'city': r'-c\s+([^-]\S+)'
        },
        'delete': {
            'record_id': r'-id\s+(\w+)'
        },
        'view': {
            'record_id': r'-id\s+(\w+)'
        },
        'search': {
            'first_name': r'-fn\s+([^-]\S+)',
            'last_name': r'-ln\s+([^-]\S+)',
            'city': r'-c\s+([^-]\S+)',
            'national_id': r'-nt\s+(\d{10})',
            'phone': r'-p\s+(\+98\d{10})',
            'mode': r'-m\s+(and|or)'
        },
        'export': {
            'filename': r'-f\s+([^-]\S+)'
        }
    }
    
    extracted = {}
    auto_confirm = '-y' in args
    
    if command in patterns:
        for field, pattern in patterns[command].items():
            match = re.search(pattern, args_str)
            if match:
                extracted[field] = match.group(1).strip()
    
    extracted['auto_confirm'] = auto_confirm
    return extracted

def handle_useradd_arguments(parts):
    args = parse_arguments(parts[1:], 'useradd')
    
    required = ['username', 'password']
    for field in required:
        if field not in args:
            print(f"Error: Missing required argument -{field[0]}")
            return None
    
    if 'role' not in args:
        args['role'] = 'viewer'
    
    if args['role'] not in ['root', 'admin', 'staff', 'viewer']:
        print("Error: Invalid role. Must be: root, admin, staff, viewer")
        return None
    
    return args

def handle_userdel_arguments(parts):
    args = parse_arguments(parts[1:], 'userdel')
    
    if 'username' not in args:
        print("Error: Missing required argument -u")
        return None
    
    return args

def handle_usermod_arguments(parts):
    args = parse_arguments(parts[1:], 'usermod')
    
    required = ['username', 'role']
    for field in required:
        if field not in args:
            print(f"Error: Missing required argument -{field[0]}")
            return None
    
    if args['role'] not in ['root', 'admin', 'staff', 'viewer']:
        print("Error: Invalid role. Must be: root, admin, staff, viewer")
        return None
    
    return args

def handle_useredit_arguments(parts):
    args = parse_arguments(parts[1:], 'useredit')
    
    if 'username' not in args:
        print("Error: Missing required argument -u")
        return None
    
    if 'new_password' not in args and 'new_username' not in args:
        print("Error: Either -np (new password) or -nu (new username) is required")
        return None
    
    return args

def handle_add_arguments(parts):
    args = parse_arguments(parts[1:], 'add')
    
    required = ['first_name', 'last_name', 'national_id', 'phone', 'city']
    for field in required:
        if field not in args:
            print(f"Error: Missing required argument -{field[0]}")
            return None
    

    try:

        is_valid_first, first_msg = DataValidator.validate_english_name(args['first_name'], "First name")
        if not is_valid_first:
            print(f"Error: {first_msg}")
            return None

        is_valid_last, last_msg = DataValidator.validate_english_name(args['last_name'], "Last name")
        if not is_valid_last:
            print(f"Error: {last_msg}")
            return None

        is_valid_national, national_msg = DataValidator.validate_national_id(args['national_id'])
        if not is_valid_national:
            print(f"Error: {national_msg}")
            return None
        
        is_valid_phone, phone_msg = DataValidator.validate_iranian_phone(args['phone'])
        if not is_valid_phone:
            print(f"Error: {phone_msg}")
            return None

        is_valid_city, city_msg = DataValidator.validate_city_name(args['city'])
        if not is_valid_city:
            print(f"Error: {city_msg}")
            return None

        first_name = DataValidator.capitalize_name(args['first_name'])
        last_name = DataValidator.capitalize_name(args['last_name'])
        city = DataValidator.capitalize_city(args['city'])
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'national_id': args['national_id'],
            'phone': args['phone'],
            'city': city,
            'auto_confirm': args.get('auto_confirm', False)
        }
        
    except Exception as e:
        print(f"Validation error: {e}")
        return None

def handle_status_arguments(parts):
    args = parse_arguments(parts[1:], 'status')
    return args

def handle_delete_arguments(parts):
    args = parse_arguments(parts[1:], 'delete')
    
    if 'record_id' not in args:
        print("Error: Missing required argument -id")
        return None
    
    return args

def handle_view_arguments(parts):
    args = parse_arguments(parts[1:], 'view')
    
    if 'record_id' not in args:
        print("Error: Missing required argument -id")
        return None
    
    return args

def handle_search_arguments(parts):
    args = parse_arguments(parts[1:], 'search')
    
    return args

def handle_export_arguments(parts):
    args = parse_arguments(parts[1:], 'export')
    return args

def show_command_help(command):
    helps = {
        'useradd': """
useradd -u USERNAME -p PASSWORD [-r ROLE] [-y]
  -u  Username (required)
  -p  Password (required) 
  -r  Role (root|admin|staff|viewer, default: viewer)
  -y  Auto confirm
Example: useradd -u john -p secret123 -r admin -y
""",
        'userdel': """
userdel -u USERNAME [-y]
  -u  Username to delete (required)
  -y  Auto confirm
Example: userdel -u john -y
""",
        'usermod': """
usermod -u USERNAME -r ROLE [-y]
  -u  Username to modify (required)
  -r  New role (root|admin|staff|viewer, required)
  -y  Auto confirm  
Example: usermod -u john -r admin -y
""",
        'useredit': """
useredit -u USERNAME [-np NEW_PASSWORD] [-nu NEW_USERNAME] [-y]
  -u  Username to edit (required)
  -np New password 
  -nu New username
  -y  Auto confirm

At least one of -np or -nu is required.

EXAMPLES:
  useredit -u john -np newpass          # Change password only
  useredit -u john -nu johnsmith        # Change username only  
  useredit -u john -np newpass -nu johnsmith -y  # Change both
""",
        'add': """
add -n FIRST_NAME -l LAST_NAME -nt NATIONAL_ID -p PHONE -c CITY [-y]
  -n  First name (required)
  -l  Last name (required)
  -nt National ID (10 digits, required)
  -p  Phone (+989123456789, required)
  -c  City (required)
  -y  Auto confirm
Example: add -n ashkan -l mirgomari -nt 1276297246 -p +989056703298 -c isfahan -y
""",
        'delete': """
delete -id RECORD_ID [-y]
  -id Record ID to delete (required)
  -y  Auto confirm
Example: delete -id ABC123 -y
""",
        'view': """
view -id RECORD_ID
  -id Record ID to view (required)
Example: view -id ABC123
""",
        'search': """
search [-fn FIRST_NAME] [-ln LAST_NAME] [-c CITY] [-nt NATIONAL_ID] [-p PHONE] [-m MODE]
  -fn First name filter
  -ln Last name filter  
  -c  City filter
  -nt National ID filter
  -p  Phone filter
  -m  Search mode (and|or, default: and)
Example: search -fn ashkan -c isfahan -m or
""",
        'export': """
export [-f FILENAME] [-y]
  -f  Custom filename
  -y  Auto confirm
Example: export -f my_data.csv -y
""",
        'status': """
status [OPTIONS]

Display comprehensive system status and health information.

OPTIONS:
  -s, --show SECTION    Display specific section only
                        Available sections: resource, metrics, security
  -h, --help           Show this help message

EXAMPLES:
  status                    # Display all system information
  status -s resource        # Show only system resources
  status --show metrics     # Show only datana metrics
  status -s security        # Show only security information
"""
    }
    
    if command in helps:
        print(helps[command])
    else:
        print(f"No help available for {command}")