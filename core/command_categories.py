COMMAND_CATEGORIES = {
    "user": {
        "name": "User Management",
        "commands": ["useradd", "userdel", "usermod", "useredit", "userlist"],
        "description": "Manage system users and permissions"
    },
    "data": {
        "name": "Data Operations", 
        "commands": ["add", "edit", "delete", "view", "search", "lists"],
        "description": "Create, read, update, and delete records"
    },
    "system": {
        "name": "System & Security",
        "commands": ["status", "backup", "restore", "autobackup", "config", "logs"],
        "description": "System maintenance and security tools"
    },
    "export": {
        "name": "Export & Reports",
        "commands": ["export", "report", "stats"],
        "description": "Export data and generate reports"
    },
    "utility": {
        "name": "Utilities",
        "commands": ["help", "clear", "whoami", "joke", "reminder", "time", "run"],
        "description": "Utility commands and helpers"
    }
}