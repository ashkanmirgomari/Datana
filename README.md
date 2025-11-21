# Datana CS50 Final Project
#### Video Demo: https://youtu.be/ne2sHOTRlQw
#### Description: CS50P final project 2025 , Datana and how datana works

# 🛡️ Datana - mini-Local Database

**Enterprise-grade secure data management with military-level encryption**

## ✨ Features
- 🔐 **Military-grade encryption** (Fernet + AES)
- 👥 **Role-based access control** (4 levels)
- 📊 **Advanced analytics & reporting**
- 💾 **Automated backup & restore**
- 🔍 **Advanced search** (Regex, Date, Filters)
- 📈 **Real-time system monitoring**
- 🛡️ **Security auditing & logging**

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ashkanmirgomari/datana.git
cd datana

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Datana
python project.py

# 4. Login with default credentials:
#    Username: root
#    Password: root

```

## 🔐 Default Login
**For first-time use, login with:**

- 👤**Username:** ```root```

- 🔐**Password:** ```root```

## 👥 User Management

**After login you can:**

- **Create new users:** ```useradd -u USERNAME -p PASSWORD -r ROLE ```

- **Change passwords:** ```useredit -u USERNAME -np NEW_PASSWORD ```

- **Modify user roles:** ```usermod -u USERNAME -r ROLE ```

- **Delete users:** ```userdel -u USERNAME ```


## 🛠️ Advanced Password Change

**To change the default root password directly in code:**

**Open core/auth.py**

**Find line 32 (the generate_default_users function)**

**Modify the root_hash value**

## 💻 Available Commands
**System Management**
```bash
status                    # System health monitoring**
stats                     # Statistics and analytics**
backup                    # Create encrypted backup
restore                   # Restore from backup
autobackup                # Configure auto-backup
logs                      # View system logs
```
**Data Operations**
```bash
add -n John -l Doe...    # Add secure records
search -fn John          # Advanced search
view -id RECORD_ID       # View specific record
edit                     # Edit existing record
delete -id RECORD_ID     # Delete record
lists                    # List all records with pagination
export -f data.csv       # Export to CSV
```
**User Management (Root only)**
```bash
useradd -u john -p pass -r admin    # Add user**
useredit -u john -np newpass        # Change password**
usermod -u john -r staff            # Change role**
userdel -u john                     # Delete user**
userlist                            # List all users**
```
**Utility Commands**
```bash
help                     # Show command help**
clear                    # Clear screen**
whoami                   # Show current user**
exit / logout            # Exit system**
```

## 🏗️ System Architecture
```bash
Core Modules:
├── Security Layer (auth.py, validators.py, secure_logger.py)
├── Database Engine (database.py, config_manager.py)
├── CLI Interface (commands.py, argument_parser.py)
├── Analytics Engine (analytics.py, stats.py)
├── Search System (advanced_search.py)
└── Backup System (backup.py, autobackup.py)
```

## 🔒 Security Features

**1 - End-to-end encryption for all stored data**

**2 - Four-tier role system (root, admin, staff, viewer)**

**3 - Session timeout after 15 minutes of inactivity**

**4 - Secure password hashing with bcrypt**

**5 - Audit logging with integrity verification**

**6 - Input validation for Iranian data standards**


## 🎯 Role Permissions
```bash
Role	Permissions
root	Full system access, user management, backup/restore
admin	Data operations, logs, system monitoring
staff	Add, search, view, export records
viewer	Search and view records only
```

## 📁 Project Structure
```bash
Datana/
├── core/                 # Core system modules
├── scripts/              # Utility scripts
├── data/                 # Encrypted data (auto-created)
├── project.py           # Main entry point
├── datana.py            # Alias for project.py
└── requirements.txt     # Python dependencies
```

## ⚠️ Important Notes

**1 - Change the default root password immediately after first login**

**2 - Regular backups are recommended**

**3 - System data is stored in encrypted format only**

**4 - Session automatically logs out after 15 minutes of inactivity**


## 🐛 Reporting Issues

**- Found a bug? Please create an issue with:**

**- Steps to reproduce**

**- Expected vs actual behavior**

**- System environment details**

## 📄 License
**Copyright © 2025 Ashkan Mirgomari. All rights reserved.**