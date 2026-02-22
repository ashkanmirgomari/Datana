# core/jokes.py
import random

class JokeSystem:
    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "Why do Java developers wear glasses? Because they can't C#.",
        "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'",
        "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
        "Why do Python programmers wear glasses? Because they can't C.",
        "What's the object-oriented way to become wealthy? Inheritance.",
        "Why did the developer go broke? Because he used up all his cache.",
        "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25.",
        "What's a programmer's favorite place to hang out? Foo Bar."
    ]
    
    TECH_TIPS = [
        "Tip: Use 'search --regex' for powerful pattern matching.",
        "Tip: Auto-backup can be configured with 'autobackup' command.",
        "Tip: Export your data regularly with 'export' command.",
        "Tip: Use 'status -s security' to check system security.",
        "Tip: 'lists' command supports pagination - try 'n' for next page."
    ]
    
    @staticmethod
    def get_random_joke():
        return random.choice(JokeSystem.JOKES)
    
    @staticmethod
    def get_random_tip():
        return random.choice(JokeSystem.TECH_TIPS)
    
    @staticmethod
    def get_fun_fact():
        facts = [
            "Datana encrypts all data with AES-256 encryption.",
            "Your passwords are hashed with bcrypt for maximum security.",
            "System automatically validates Iranian national IDs.",
            "Backup files are stored in encrypted format.",
            "All user activities are logged for security auditing."
        ]
        return random.choice(facts)