# core/gamification.py
import json
import os
from datetime import datetime, timedelta
from core.utils import DATA_DIR
from core.logger import log

RANKS_FILE = os.path.join(DATA_DIR, "user_ranks.json")
BADGES_FILE = os.path.join(DATA_DIR, "user_badges.json")
TASKS_FILE = os.path.join(DATA_DIR, "daily_tasks.json")

# ========== Rank Definitions ==========
RANKS = [
    {
        "id": 1,
        "name": "Novice",
        "level": 1,
        "min_points": 0,
        "max_points": 100,
        "color": "#94a3b8",
        "description": "Newcomer"
    },
    {
        "id": 2,
        "name": "Apprentice",
        "level": 2,
        "min_points": 101,
        "max_points": 300,
        "color": "#10b981",
        "description": "Learning the ropes"
    },
    {
        "id": 3,
        "name": "Active User",
        "level": 3,
        "min_points": 301,
        "max_points": 600,
        "color": "#3b82f6",
        "description": "Regular user"
    },
    {
        "id": 4,
        "name": "Professional",
        "level": 4,
        "min_points": 601,
        "max_points": 1000,
        "color": "#8b5cf6",
        "description": "Power user"
    },
    {
        "id": 5,
        "name": "Master",
        "level": 5,
        "min_points": 1001,
        "max_points": 1500,
        "color": "#f59e0b",
        "description": "Expert user"
    },
    {
        "id": 6,
        "name": "Legend",
        "level": 6,
        "min_points": 1501,
        "max_points": 999999,
        "color": "#ec4899",
        "description": "Legendary user"
    }
]

# ========== Badge Definitions ==========
BADGES = [
    {
        "id": "first_record",
        "name": "First Step",
        "description": "Added your first record",
        "points": 10,
        "icon": "📝"
    },
    {
        "id": "record_master_10",
        "name": "Collector",
        "description": "Added 10 records",
        "points": 20,
        "icon": "📚"
    },
    {
        "id": "record_master_50",
        "name": "Data Writer",
        "description": "Added 50 records",
        "points": 50,
        "icon": "📊"
    },
    {
        "id": "record_master_100",
        "name": "Data Lord",
        "description": "Added 100 records",
        "points": 100,
        "icon": "💿"
    },
    {
        "id": "backup_first",
        "name": "Guardian",
        "description": "Created first backup",
        "points": 15,
        "icon": "💾"
    },
    {
        "id": "backup_master_5",
        "name": "Backup Pro",
        "description": "Created 5 backups",
        "points": 30,
        "icon": "🛡️"
    },
    {
        "id": "search_master_50",
        "name": "Detective",
        "description": "Performed 50 searches",
        "points": 40,
        "icon": "🔍"
    },
    {
        "id": "login_streak_7",
        "name": "Regular",
        "description": "7-day login streak",
        "points": 25,
        "icon": "🔥"
    },
    {
        "id": "login_streak_30",
        "name": "Dedicated",
        "description": "30-day login streak",
        "points": 75,
        "icon": "⚡"
    },
    {
        "id": "export_master",
        "name": "Exporter",
        "description": "Exported data 10 times",
        "points": 35,
        "icon": "📤"
    },
    {
        "id": "helper",
        "name": "Helper",
        "description": "Used help command 20 times",
        "points": 15,
        "icon": "❓"
    },
    {
        "id": "night_owl",
        "name": "Night Owl",
        "description": "Active after midnight",
        "points": 20,
        "icon": "🌙"
    },
    {
        "id": "early_bird",
        "name": "Early Bird",
        "description": "Active before 6 AM",
        "points": 20,
        "icon": "☀️"
    },
    {
        "id": "perfect_week",
        "name": "Perfect Week",
        "description": "Active every day for a week",
        "points": 100,
        "icon": "🏆"
    }
]

# ========== Daily Tasks ==========
DAILY_TASKS = [
    {
        "id": "daily_add",
        "name": "Daily Addition",
        "description": "Add at least 1 record today",
        "points": 10,
        "icon": "➕"
    },
    {
        "id": "daily_search",
        "name": "Daily Search",
        "description": "Perform 3 searches today",
        "points": 5,
        "icon": "🔍"
    },
    {
        "id": "daily_backup",
        "name": "Daily Backup",
        "description": "Create a backup",
        "points": 15,
        "icon": "💾"
    },
    {
        "id": "daily_login",
        "name": "Daily Login",
        "description": "Just log in",
        "points": 5,
        "icon": "🔑"
    }
]

class GamificationSystem:
    
    @staticmethod
    def load_user_data():
        """Load user rank and badge data"""
        if os.path.exists(RANKS_FILE):
            try:
                with open(RANKS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_user_data(data):
        """Save user rank and badge data"""
        os.makedirs(os.path.dirname(RANKS_FILE), exist_ok=True)
        with open(RANKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_badges():
        """Load user badges"""
        if os.path.exists(BADGES_FILE):
            try:
                with open(BADGES_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_badges(data):
        """Save user badges"""
        os.makedirs(os.path.dirname(BADGES_FILE), exist_ok=True)
        with open(BADGES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_tasks():
        """Load daily tasks completion"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def save_tasks(data):
        """Save daily tasks completion"""
        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        with open(TASKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def get_user_rank(username):
        """Get current rank for a user"""
        data = GamificationSystem.load_user_data()
        
        if username not in data:
            # Initialize new user
            data[username] = {
                "points": 0,
                "last_login": None,
                "login_streak": 0,
                "total_records": 0,
                "total_backups": 0,
                "total_searches": 0,
                "total_exports": 0,
                "first_seen": datetime.now().isoformat()
            }
            GamificationSystem.save_user_data(data)
        
        points = data[username]["points"]
        
        # Find rank based on points
        for rank in RANKS:
            if rank["min_points"] <= points <= rank["max_points"]:
                return rank
        
        return RANKS[0]  # Default to Novice
    
    @staticmethod
    def get_user_badges(username):
        """Get all badges for a user"""
        badges = GamificationSystem.load_badges()
        return badges.get(username, [])
    
    @staticmethod
    def get_daily_tasks(username):
        """Get daily tasks for user"""
        tasks = GamificationSystem.load_tasks()
        today = datetime.now().date().isoformat()
        
        if username not in tasks or tasks[username].get("date") != today:
            # Reset tasks for new day
            tasks[username] = {
                "date": today,
                "completed": []
            }
            GamificationSystem.save_tasks(tasks)
        
        result = []
        for task in DAILY_TASKS:
            result.append({
                "id": task["id"],
                "name": task["name"],
                "description": task["description"],
                "points": task["points"],
                "icon": task["icon"],
                "completed": task["id"] in tasks[username]["completed"]
            })
        
        return result
    
    @staticmethod
    def get_leaderboard(limit=10):
        """Get top users by points"""
        data = GamificationSystem.load_user_data()
        
        # Create list of (username, points)
        users = []
        for username, info in data.items():
            users.append({
                "username": username,
                "points": info.get("points", 0),
                "records": info.get("total_records", 0),
                "streak": info.get("login_streak", 0),
                "rank": GamificationSystem.get_user_rank(username)
            })
        
        # Sort by points descending
        users.sort(key=lambda x: x["points"], reverse=True)
        
        return users[:limit]
    
@staticmethod
def record_event(username, event_type):
    """Record user activity for gamification"""
    data = GamificationSystem.load_user_data()
    
    if username not in data:
        data[username] = {
            "points": 0,
            "last_login": None,
            "login_streak": 0,
            "total_records": 0,
            "total_backups": 0,
            "total_searches": 0,
            "total_exports": 0,
            "first_seen": datetime.now().isoformat()
        }
    
    today = datetime.now().date()
    
    if event_type == "login":
        last = data[username].get("last_login")
        if last:
            try:
                last_date = datetime.fromisoformat(last).date()
                if last_date == today - timedelta(days=1):
                    data[username]["login_streak"] += 1
                elif last_date < today - timedelta(days=1):
                    data[username]["login_streak"] = 1
            except:
                data[username]["login_streak"] = 1
        else:
            data[username]["login_streak"] = 1
        
        data[username]["last_login"] = datetime.now().isoformat()
        
        # Check for streak badges
        streak = data[username]["login_streak"]
        if streak == 7:
            GamificationSystem.award_badge(username, "login_streak_7")
        elif streak == 30:
            GamificationSystem.award_badge(username, "login_streak_30")
        
        # Check for time-based badges
        hour = datetime.now().hour
        if hour < 6:
            GamificationSystem.award_badge(username, "night_owl")
        elif hour < 8:
            GamificationSystem.award_badge(username, "early_bird")
    
    elif event_type == "add_record":
        data[username]["total_records"] += 1
        count = data[username]["total_records"]
        
        if count == 1:
            GamificationSystem.award_badge(username, "first_record")
        elif count == 10:
            GamificationSystem.award_badge(username, "record_master_10")
        elif count == 50:
            GamificationSystem.award_badge(username, "record_master_50")
        elif count == 100:
            GamificationSystem.award_badge(username, "record_master_100")
        
        GamificationSystem.add_points(username, 2, "Added record")

        GamificationSystem.save_user_data(data)
    
    @staticmethod
    def award_badge(username, badge_id):
        """Award a badge to user"""
        badges = GamificationSystem.load_badges()
        
        if username not in badges:
            badges[username] = []
        
        # Check if already has badge
        for badge in badges[username]:
            if badge["id"] == badge_id:
                return False
        
        # Find badge details
        badge_details = None
        for badge in BADGES:
            if badge["id"] == badge_id:
                badge_details = badge
                break
        
        if not badge_details:
            return False
        
        # Add badge
        badges[username].append({
            "id": badge_id,
            "name": badge_details["name"],
            "description": badge_details["description"],
            "icon": badge_details["icon"],
            "points": badge_details["points"],
            "awarded_at": datetime.now().isoformat()
        })
        
        GamificationSystem.save_badges(badges)
        
        # Add points for badge
        GamificationSystem.add_points(username, badge_details["points"], f"Badge: {badge_details['name']}")
        
        log(f"GAMIFICATION: {username} earned badge {badge_details['name']}")
        return True
    
    @staticmethod
    def add_points(username, points, reason=""):
        """Add points to user"""
        data = GamificationSystem.load_user_data()
        
        if username not in data:
            data[username] = {
                "points": 0,
                "last_login": None,
                "login_streak": 0,
                "total_records": 0,
                "total_backups": 0,
                "total_searches": 0,
                "total_exports": 0,
                "first_seen": datetime.now().isoformat()
            }
        
        data[username]["points"] += points
        GamificationSystem.save_user_data(data)
        return True