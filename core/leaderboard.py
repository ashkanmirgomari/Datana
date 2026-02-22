# core/leaderboard.py
from core.gamification import GamificationSystem, RANKS
from tabulate import tabulate

class Leaderboard:
    
    @staticmethod
    def get_rank_progress(username):
        """Get progress to next rank"""
        data = GamificationSystem.load_user_data()
        
        if username not in data:
            return None
        
        points = data[username]["points"]
        current_rank = GamificationSystem.get_user_rank(username)
        
        # Find next rank
        next_rank = None
        for rank in RANKS:
            if rank["id"] == current_rank["id"] + 1:
                next_rank = rank
                break
        
        if not next_rank:
            return {
                "current": current_rank,
                "next": None,
                "progress": 100,
                "points_needed": 0
            }
        
        points_needed = next_rank["min_points"] - points
        progress = ((points - current_rank["min_points"]) / 
                   (next_rank["min_points"] - current_rank["min_points"])) * 100
        
        return {
            "current": current_rank,
            "next": next_rank,
            "progress": progress,
            "points_needed": points_needed
        }
    
    @staticmethod
    def show_leaderboard(limit=10, format_type="table"):
        """Display leaderboard"""
        users = GamificationSystem.get_leaderboard(limit)
        
        if not users:
            print("\nNo users found in leaderboard yet.")
            return
        
        if format_type == "table":
            table_data = []
            for i, user in enumerate(users, 1):
                table_data.append([
                    i,
                    user["username"],
                    user["points"],
                    user["rank"]["name"],
                    user["records"],
                    f"{user['streak']} days"
                ])
            
            print("\n" + "="*70)
            print("🏆 LEADERBOARD")
            print("="*70)
            print(tabulate(table_data, 
                         headers=["#", "Username", "Points", "Rank", "Records", "Streak"],
                         tablefmt="grid"))
            print("="*70)
        
        elif format_type == "minimal":
            for i, user in enumerate(users, 1):
                print(f"{i:2}. {user['username']:<15} {user['points']:>5} pts [{user['rank']['name']}]")
    
    @staticmethod
    def show_user_profile(username):
        """Show detailed profile for a user"""
        data = GamificationSystem.load_user_data()
        badges = GamificationSystem.get_user_badges(username)
        rank = GamificationSystem.get_user_rank(username)
        
        if username not in data:
            print(f"\nNo data found for user: {username}")
            return
        
        user_data = data[username]
        
        print("\n" + "="*60)
        print(f"👤 USER PROFILE: {username}")
        print("="*60)
        
        # Rank info
        print(f"\n📊 RANK:")
        print(f"   {rank['name']} (Level {rank['level']})")
        print(f"   Points: {user_data['points']}")
        print(f"   Progress: {user_data['points'] - rank['min_points']}/{rank['max_points'] - rank['min_points']}")
        
        # Stats
        print(f"\n📈 STATS:")
        print(f"   Total Records: {user_data['total_records']}")
        print(f"   Total Backups: {user_data['total_backups']}")
        print(f"   Total Searches: {user_data['total_searches']}")
        print(f"   Total Exports: {user_data['total_exports']}")
        print(f"   Login Streak: {user_data['login_streak']} days")
        print(f"   Member since: {user_data['first_seen'][:10]}")
        
        # Badges
        print(f"\n🏅 BADGES ({len(badges)}):")
        if badges:
            for badge in badges:
                print(f"   • {badge['name']} (+{badge['points']} pts)")
        else:
            print("   No badges yet")
        
        print("="*60)