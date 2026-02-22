<div align="center">
  <img src="https://img.icons8.com/fluency/96/database.png" width="100"/>
  <h1>DATANA</h1>
  <p><strong>Mini Local Database Manager with CLI & Web Interface</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/version-1.1.0.9-purple?style=for-the-badge" />
    <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge" />
    <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
    <img src="https://img.shields.io/badge/Flask-2.3+-red?style=for-the-badge" />
  </p>
  
  <p>
    <a href="#-features">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-usage">Usage</a> •
    <a href="#-commands">Commands</a> •
    <a href="#-web-interface">Web Interface</a> •
  </p>
</div>

---

## ✨ Features

### 🖥️ Command Line Interface
- **30+ Commands** for complete database management
- **User authentication** with role-based access (root, admin, staff, viewer)
- **Encrypted storage** for records and users
- **Advanced search** with regex and filters
- **Bulk operations** for mass updates/deletes
- **Auto-backup** system with scheduling
- **Gamification** with ranks, badges, and leaderboard
- **Reminder system** for important tasks
- **Fun commands** (joke, tip, fact) for a better experience

### 🌐 Web Panel
- **Modern UI** with Glassmorphism design
- **Dark/Light theme** with toggle
- **Fully responsive** for mobile and tablet
- **Real-time monitoring** with charts
- **User profiles** with gamification stats
- **Leaderboard** to compete with others
- **Complete CRUD operations**
- **Advanced search** with filters
- **Backup management** from browser
- **Export to CSV** with one click

### 🔒 Security
- **AES-256 encryption** for all data
- **bcrypt password hashing**
- **Session management** with timeout
- **Iranian data validation** (national ID, phone)
- **Activity logging** with integrity check

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/ashkanmirgomari/datana.git
cd datana

# Install dependencies
pip install -r requirements.txt

# Run Datana
python datana.py
```

### Using pip (coming soon)
```bash
pip install datana
datana
```

---

## 🚀 Usage

### Starting Datana

```bash
# Start CLI
python datana.py

# Start web panel (from CLI)
datana> run webpanel -p 5000

# Start web panel directly
python run_web.py
```

### First Login
- **Username:** `root`
- **Password:** `root`

> ⚠️ Change the default password immediately!

---

## 📋 Commands

### User Management
| Command | Description | Example |
|---------|-------------|---------|
| `useradd -u USER -p PASS -r ROLE` | Add new user | `useradd -u john -p 123 -r admin` |
| `userdel -u USER` | Delete user | `userdel -u john` |
| `usermod -u USER -r ROLE` | Change user role | `usermod -u john -r staff` |
| `userlist` | List all users | `userlist` |

### Record Operations
| Command | Description | Example |
|---------|-------------|---------|
| `add -n FIRST -l LAST -nt ID -p PHONE -c CITY` | Add record | `add -n ashkan -l mirgomari -nt 1276297246 -p +989056703298 -c isfahan` |
| `search -fn NAME -ln NAME -c CITY` | Search records | `search -fn ashkan -c isfahan` |
| `view -id ID` | View record | `view -id ABC123` |
| `edit -id ID` | Edit record | `edit -id ABC123` |
| `delete -id ID` | Delete record | `delete -id ABC123` |
| `lists` | List all records | `lists` |

### Bulk Operations
| Command | Description | Example |
|---------|-------------|---------|
| `bulk delete --city tehran` | Delete all records from Tehran | `bulk delete --city tehran --confirm` |
| `bulk update --all --add-tag vip` | Add tag to all records | `bulk update --all --add-tag vip` |
| `bulk export --ids ID1,ID2 --format csv` | Export specific records | `bulk export --ids ABC123,DEF456 --format csv` |

### System Commands
| Command | Description | Example |
|---------|-------------|---------|
| `backup` | Create backup | `backup` |
| `restore` | Restore from backup | `restore` |
| `autobackup` | Configure auto-backup | `autobackup --enable --mode daily` |
| `status` | System status | `status` |
| `stats` | Database statistics | `stats` |
| `logs` | View system logs | `logs` |

### Fun Commands
| Command | Description |
|---------|-------------|
| `joke` | Get a random programming joke |
| `tip` | Get a useful tip |
| `fact` | Get a fact about Datana |
| `reminder` | Manage reminders |

---

## 🌐 Web Interface

### Access
```
http://localhost:5000
```

### Pages
- **Dashboard** - Overview with stats and charts
- **Records** - Manage all records
- **Add Record** - Create new entries
- **Profile** - Your gamification stats
- **Leaderboard** - Compete with other users
- **Reports** - View analytics
- **Backup** - Manage backups
- **Monitoring** - System health
- **Reminders** - Your reminders

### Features
- **Glassmorphism design** with blur effects
- **Dark/Light theme** toggle
- **Responsive** mobile-friendly layout
- **Animated icons** and smooth transitions
- **Live preview** when adding records
- **Real-time charts** for monitoring
- **Toast notifications** for actions

---

## 🎮 Gamification

### Ranks
| Level | Rank | Points |
|-------|------|--------|
| 1 | Novice | 0-100 |
| 2 | Apprentice | 101-300 |
| 3 | Active User | 301-600 |
| 4 | Professional | 601-1000 |
| 5 | Master | 1001-1500 |
| 6 | Legend | 1500+ |

### Badges
| Badge | How to Earn |
|-------|-------------|
| 🥇 First Step | Add your first record |
| 📚 Collector | Add 10 records |
| 📊 Data Writer | Add 50 records |
| 💿 Data Lord | Add 100 records |
| 💾 Guardian | Create first backup |
| 🛡️ Backup Pro | Create 5 backups |
| 🔍 Detective | Perform 50 searches |
| 🔥 Regular | 7-day login streak |
| ⚡ Dedicated | 30-day login streak |
| 🌙 Night Owl | Active after midnight |
| ☀️ Early Bird | Active before 6 AM |

---


## 🛠️ Configuration

### Data Directory
All data is stored in `data/` directory:
- `records.enc` - Encrypted records
- `users.enc` - Encrypted users
- `logs.txt` - System logs
- `backups/` - Backup files
- `exports/` - Exported CSV files

### Auto-backup Configuration
```bash
# Enable daily auto-backup
autobackup --enable --mode daily

# Enable weekly auto-backup
autobackup --enable --mode weekly

# Disable auto-backup
autobackup --disable
```

---

## 🧪 Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_database
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ashkan Mirgomari**
- GitHub: [@ashkanmirgomari](https://github.com/ashkanmirgomari)
- Email: ashkanmirgomari@gmail.com

---

## 🙏 Acknowledgments

- All contributors and users
- Python community
- Flask framework
- Font Awesome for icons
- Google Fonts for typography

---

<div align="center">
  <sub>Built with ❤️ by Ashkan Mirgomari and AI</sub>
  <br />
  <sub>© 2026 Datana - Mini Local Database</sub>
</div>