# core/reminders.py
import json
import os
from datetime import datetime, timedelta
from core.utils import DATA_DIR

REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")

class ReminderSystem:
    @staticmethod
    def load_reminders():
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    @staticmethod
    def save_reminders(reminders):
        os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, indent=2)
    
    @staticmethod
    def add_reminder(text, days=0, hours=0, minutes=0):
        reminders = ReminderSystem.load_reminders()
        
        due_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
        
        reminder = {
            "id": len(reminders) + 1,
            "text": text,
            "created": datetime.now().isoformat(),
            "due": due_time.isoformat(),
            "completed": False
        }
        
        reminders.append(reminder)
        ReminderSystem.save_reminders(reminders)
        return reminder["id"]
    
    @staticmethod
    def list_reminders(show_completed=False):
        reminders = ReminderSystem.load_reminders()
        
        if not reminders:
            return []
        
        if not show_completed:
            reminders = [r for r in reminders if not r["completed"]]
        
        reminders.sort(key=lambda x: x["due"])
        return reminders
    
    @staticmethod
    def complete_reminder(reminder_id):
        reminders = ReminderSystem.load_reminders()
        
        for reminder in reminders:
            if reminder["id"] == reminder_id:
                reminder["completed"] = True
                ReminderSystem.save_reminders(reminders)
                return True
        
        return False
    
    @staticmethod
    def check_due_reminders():
        reminders = ReminderSystem.load_reminders()
        now = datetime.now()
        due_reminders = []
        
        for reminder in reminders:
            if not reminder["completed"]:
                due_time = datetime.fromisoformat(reminder["due"])
                if due_time <= now:
                    due_reminders.append(reminder)
        
        return due_reminders