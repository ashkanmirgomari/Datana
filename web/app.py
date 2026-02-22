# web/app.py
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# ========== مهم: تنظیم مسیر ==========
# به دست آوردن مسیر ریشه پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # یک سطح بالا (از web به ریشه)
sys.path.insert(0, parent_dir)  # اضافه کردن ریشه به PATH
# ====================================

# حالا می‌تونه core رو پیدا کنه
from core.auth import verify, load_users, save_users
from core.database import (
    load_records, save_records, add_record, search_by_id, delete_record_by_id,
    advanced_search, get_system_stats, create_backup, get_available_backups,
    restore_from_backup, get_exports_dir, export_csv
)
from core.analytics import Analytics
from core.validators import DataValidator
from core.logger import log
from core.utils import VERSION, DATA_DIR
from core.reminders import ReminderSystem
from core.jokes import JokeSystem
from core.autobackup import autobackup_status, run_autobackup, update_autobackup_config
from core.gamification import GamificationSystem  # این خط جدید
from core.leaderboard import Leaderboard  # این خط جدید
from datetime import datetime
import psutil
import time

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
app.secret_key = os.urandom(24).hex()
# ============================================
# Web Routes
# ============================================

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_info = verify(username, password)
        
        if user_info:
            session['username'] = username
            session['role'] = user_info['role']
            flash('Login successful!', 'success')
            
            due_reminders = ReminderSystem.check_due_reminders()
            if due_reminders:
                session['due_reminders'] = len(due_reminders)
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', version=VERSION)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stats = get_system_stats()
    joke = JokeSystem.get_random_joke()
    
    records = load_records()
    recent_records = records[-5:] if records else []
    
    reminders = ReminderSystem.list_reminders()
    due_reminders = [r for r in reminders if not r.get('completed')][:3]
    
    backup_status = autobackup_status()
    
    return render_template('dashboard.html',
                         username=session['username'],
                         role=session['role'],
                         stats=stats,
                         recent_records=recent_records,
                         joke=joke,
                         reminders=due_reminders,
                         backup_status=backup_status,
                         version=VERSION)

@app.route('/records')
def records():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    records_list = load_records()
    records_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    total = len(records_list)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = records_list[start:end]
    
    stats = get_system_stats()
    
    return render_template('records.html',
                         username=session['username'],
                         role=session['role'],
                         records=paginated_records,
                         page=page,
                         total_pages=(total + per_page - 1) // per_page,
                         total=total,
                         stats=stats,
                         version=VERSION)

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/record/<record_id>')
def record_detail(record_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    record = search_by_id(record_id)
    
    if not record:
        flash('Record not found', 'error')
        return redirect(url_for('records'))
    
    return render_template('record_detail.html',
                         username=session['username'],
                         role=session['role'],
                         record=record,
                         version=VERSION)

@app.route('/add', methods=['GET', 'POST'])
def add_record_web():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session['role'] not in ['root', 'admin', 'staff']:
        flash('You do not have permission to add records', 'error')
        return redirect(url_for('dashboard'))
    
    stats = get_system_stats()
    
    if request.method == 'POST':
        # دریافت داده‌ها از فرم
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        national_id = request.form.get('national_id', '').strip()
        phone = request.form.get('phone', '').strip()
        dob = request.form.get('dob', '').strip()
        address = request.form.get('address', '').strip()
        tags = request.form.get('tags', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # اعتبارسنجی
        errors = []
        
        # اعتبارسنجی نام
        if not first_name:
            errors.append('First name is required')
        else:
            is_valid, msg = DataValidator.validate_english_name(first_name, 'First name')
            if not is_valid:
                errors.append(msg)
        
        if not last_name:
            errors.append('Last name is required')
        else:
            is_valid, msg = DataValidator.validate_english_name(last_name, 'Last name')
            if not is_valid:
                errors.append(msg)
        
        # اعتبارسنجی کد ملی (اختیاری)
        if national_id:
            is_valid, msg = DataValidator.validate_national_id(national_id)
            if not is_valid:
                errors.append(msg)
        
        # اعتبارسنجی تلفن (اختیاری)
        if phone:
            is_valid, msg = DataValidator.validate_iranian_phone(phone)
            if not is_valid:
                errors.append(msg)
        
        # اعتبارسنجی شهر (اختیاری)
        if address:
            is_valid, msg = DataValidator.validate_city_name(address)
            if not is_valid:
                errors.append(msg)
        
        # اعتبارسنجی تاریخ تولد (اختیاری)
        if dob:
            try:
                # چک کردن فرمت تاریخ
                datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                errors.append('Invalid date format. Use YYYY-MM-DD')
        
        # اگر خطایی بود، نشون بده
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('add.html',
                                 username=session['username'],
                                 role=session['role'],
                                 form_data=request.form,
                                 stats=stats,
                                 version=VERSION)
        
        # اضافه کردن رکورد
        try:
            record_id = add_record(
                first=first_name,
                last=last_name,
                national_id=national_id if national_id else None,
                phone=phone if phone else None,
                address=address if address else None,
                dob=dob if dob else None,
                tags=tags if tags else None,
                notes=notes if notes else None
            )
            
            # ثبت رویداد برای gamification
            try:
                from core.gamification import GamificationSystem
                GamificationSystem.record_event(session['username'], 'add_record')
            except Exception as e:
                print(f"Gamification error: {e}")
            
            flash(f'Record added successfully! ID: {record_id}', 'success')
            log(f"WEB_ADD: {session['username']} added record={record_id}")
            return redirect(url_for('records'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add.html',
                                 username=session['username'],
                                 role=session['role'],
                                 form_data=request.form,
                                 stats=stats,
                                 version=VERSION)
        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return render_template('add.html',
                                 username=session['username'],
                                 role=session['role'],
                                 form_data=request.form,
                                 stats=stats,
                                 version=VERSION)
    
    # اگر GET بود، فرم رو نشون بده
    return render_template('add.html',
                         username=session['username'],
                         role=session['role'],
                         stats=stats,
                         version=VERSION)


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    stats = get_system_stats()
    
    try:
        from core.gamification import GamificationSystem
        from core.leaderboard import Leaderboard
        
        # ثبت رویداد لاگین
        GamificationSystem.record_event(username, 'login')
        
        # گرفتن آخرین داده‌ها از دیتابیس
        all_data = GamificationSystem.load_user_data()
        
        # محاسبه آمار واقعی از دیتابیس
        from core.database import load_records
        records = load_records()
        
        # شمارش رکوردهای این کاربر (اگه سیستم چند کاربره دارید)
        user_records = 0
        for record in records:
            # اگه فیلد created_by دارید یا هر روش دیگه‌ای برای تشخیص کاربر
            # اینجا ساده شده: کل رکوردها رو حساب میکنه
            user_records = len(records)
        
        # آپدیت آمار کاربر
        if username in all_data:
            all_data[username]['total_records'] = user_records
            GamificationSystem.save_user_data(all_data)
        
        user_data = all_data.get(username, {
            'points': 0,
            'total_records': user_records,
            'total_backups': 0,
            'total_searches': 0,
            'total_exports': 0,
            'login_streak': 0,
            'first_seen': datetime.now().isoformat()[:10]
        })
        
        badges = GamificationSystem.get_user_badges(username)
        rank = GamificationSystem.get_user_rank(username)
        progress = Leaderboard.get_rank_progress(username)
        daily_tasks = GamificationSystem.get_daily_tasks(username)
        
        print(f"Profile data for {username}: {user_data}")  # برای دیباگ
        
    except Exception as e:
        print(f"Gamification error: {e}")
        import traceback
        traceback.print_exc()
        
        from core.database import load_records
        records = load_records()
        
        user_data = {
            'points': 0,
            'total_records': len(records),
            'total_backups': 0,
            'total_searches': 0,
            'total_exports': 0,
            'login_streak': 0,
            'first_seen': datetime.now().isoformat()[:10]
        }
        badges = []
        rank = {'name': 'Novice', 'level': 1, 'color': '#94a3b8', 'description': 'Newcomer'}
        progress = None
        daily_tasks = []
    
    return render_template('profile.html',
                         username=username,
                         role=session['role'],
                         stats=stats,
                         user_data=user_data,
                         badges=badges,
                         rank=rank,
                         progress=progress,
                         daily_tasks=daily_tasks,
                         version=VERSION)

@app.route('/leaderboard')
def leaderboard_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stats = get_system_stats()
    leaderboard = GamificationSystem.get_leaderboard(20)
    
    # Get badge counts for each user
    all_badges = GamificationSystem.load_badges()
    user_badges = {}
    for item in leaderboard:
        username = item['username']
        user_badges[username] = all_badges.get(username, [])
    
    return render_template('leaderboard.html',
                         username=session['username'],
                         role=session['role'],
                         stats=stats,
                         leaderboard=leaderboard,
                         user_badges=user_badges,
                         current_user=session['username'],
                         version=VERSION)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    results = []
    search_performed = False
    
    stats = get_system_stats()
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        city = request.form.get('city', '').strip()
        national_id = request.form.get('national_id', '').strip()
        phone = request.form.get('phone', '').strip()
        mode = request.form.get('mode', 'and')
        
        if any([first_name, last_name, city, national_id, phone]):
            results = advanced_search(
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None,
                city=city if city else None,
                national_id=national_id if national_id else None,
                phone=phone if phone else None,
                search_mode=mode
            )
            search_performed = True
    
    return render_template('search.html',
                         username=session['username'],
                         role=session['role'],
                         results=results,
                         search_performed=search_performed,
                         stats=stats,
                         version=VERSION)

@app.route('/delete/<record_id>', methods=['POST'])
def delete_record(record_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session['role'] not in ['root', 'admin']:
        flash('You do not have permission to delete records', 'error')
        return redirect(url_for('records'))
    
    success = delete_record_by_id(record_id)
    
    if success:
        flash(f'Record {record_id} deleted successfully', 'success')
        log(f"WEB_DELETE: {session['username']} deleted record={record_id}")
    else:
        flash(f'Record {record_id} not found', 'error')
    
    return redirect(url_for('records'))

@app.route('/export', methods=['GET', 'POST'])
def export():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stats = get_system_stats()
    
    if request.method == 'POST':
        count, path = export_csv()
        
        if count > 0 and path:
            flash(f'Exported {count} records to {os.path.basename(path)}', 'success')
        else:
            flash('Export failed or no records to export', 'error')
        
        return redirect(url_for('records'))
    
    exports_dir = get_exports_dir()
    exports = []
    
    if os.path.exists(exports_dir):
        for f in os.listdir(exports_dir):
            if f.endswith('.csv'):
                file_path = os.path.join(exports_dir, f)
                exports.append({
                    'name': f,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
                })
    
    exports.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('export.html',
                         username=session['username'],
                         role=session['role'],
                         exports=exports[:10],
                         stats=stats,
                         version=VERSION)

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session['role'] not in ['root', 'admin']:
        flash('You do not have permission to manage backups', 'error')
        return redirect(url_for('dashboard'))
    
    stats = get_system_stats()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            path = create_backup()
            if path:
                flash(f'Backup created: {os.path.basename(path)}', 'success')
            else:
                flash('Backup failed', 'error')
        
        elif action == 'restore':
            backup_file = request.form.get('backup_file')
            if backup_file:
                success, msg = restore_from_backup(backup_file)
                if success:
                    flash(msg, 'success')
                else:
                    flash(msg, 'error')
    
    backups = get_available_backups()
    backup_status = autobackup_status()
    
    return render_template('backup.html',
                         username=session['username'],
                         role=session['role'],
                         backups=backups,
                         backup_status=backup_status,
                         stats=stats,
                         version=VERSION)

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    report_type = request.args.get('type', 'user')
    
    stats = get_system_stats()
    
    if report_type == 'user':
        report = Analytics.user_activity_report()
    elif report_type == 'data':
        report = Analytics.data_quality_report()
    elif report_type == 'system':
        report = Analytics.system_status_report()
    elif report_type == 'security':
        report = Analytics.security_report()
    else:
        report = Analytics.user_activity_report()
    
    return render_template('reports.html',
                         username=session['username'],
                         role=session['role'],
                         report=report,
                         report_type=report_type,
                         stats=stats,
                         version=VERSION)

@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stats = get_system_stats()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            text = request.form.get('text')
            days = int(request.form.get('days', 0))
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 0))
            
            if text:
                reminder_id = ReminderSystem.add_reminder(text, days, hours, minutes)
                flash(f'Reminder added! ID: {reminder_id}', 'success')
        
        elif action == 'complete':
            reminder_id = int(request.form.get('reminder_id'))
            if ReminderSystem.complete_reminder(reminder_id):
                flash('Reminder completed', 'success')
    
    reminders_list = ReminderSystem.list_reminders(show_completed=True)
    
    return render_template('reminders.html',
                         username=session['username'],
                         role=session['role'],
                         reminders=reminders_list,
                         stats=stats,
                         version=VERSION)

@app.route('/api/stats')
def api_stats():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = get_system_stats()
    return jsonify(stats)

@app.route('/api/joke')
def api_joke():
    return jsonify({'joke': JokeSystem.get_random_joke()})

@app.route('/api/tip')
def api_tip():
    return jsonify({'tip': JokeSystem.get_random_tip()})

# ============================================
# Monitoring Routes
# ============================================
import psutil
import time

@app.route('/monitoring')
def monitoring_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('monitoring.html',
                         username=session['username'],
                         role=session['role'],
                         version=VERSION)

@app.route('/api/monitoring/stats')
def api_monitoring_stats():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # System stats
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Datana stats
    records = load_records()
    users = load_users()
    stats = get_system_stats()
    
    # Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    # Today's activity
    today = datetime.now().date()
    today_adds = sum(1 for r in records if r.get('created_at', '').startswith(str(today)))
    
    return jsonify({
        'cpu': round(cpu_percent, 1),
        'memory': {
            'used': round(memory.used / (1024**3), 1),
            'total': round(memory.total / (1024**3), 1),
            'percent': memory.percent
        },
        'disk': {
            'used': round(disk.used / (1024**3), 1),
            'total': round(disk.total / (1024**3), 1),
            'percent': disk.percent
        },
        'records': {
            'total': len(records),
            'today': today_adds
        },
        'uptime': f"{days}d {hours}h {minutes}m",
        'active_users': len(users),
        'db_size': f"{round(stats['data_size'] / 1024, 1)} KB",
        'last_backup': stats['last_backup'][:10] if stats['last_backup'] != 'No backups found' else 'Never',
        'activity': {
            'adds': today_adds,
            'deletes': 0,
            'searches': 0
        }
    })

@app.route('/api/monitoring/processes')
def api_monitoring_processes():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': round(pinfo['cpu_percent'], 1),
                    'memory': round(pinfo['memory_percent'], 1),
                    'status': pinfo['status']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return jsonify(processes[:10])

@app.route('/api/monitoring/alerts')
def api_monitoring_alerts():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    alerts = []
    
    # Check CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    if cpu_percent > 80:
        alerts.append({
            'type': 'warning',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'High CPU usage: {cpu_percent}%'
        })
    
    # Check Memory
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        alerts.append({
            'type': 'error',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'Critical memory usage: {memory.percent}%'
        })
    elif memory.percent > 75:
        alerts.append({
            'type': 'warning',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'High memory usage: {memory.percent}%'
        })
    
    # Check Disk
    disk = psutil.disk_usage('/')
    if disk.percent > 95:
        alerts.append({
            'type': 'error',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'Critical disk space: {disk.percent}% used'
        })
    elif disk.percent > 85:
        alerts.append({
            'type': 'warning',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'Low disk space: {disk.percent}% used'
        })
    
    # Check backup
    from core.database import get_last_backup_info
    last_backup = get_last_backup_info()
    if last_backup == 'No backups found':
        alerts.append({
            'type': 'warning',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': 'No backups found! Create one soon.'
        })
    
    return jsonify(alerts)

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    
    print("=" * 60)
    print("Datana Web Interface")
    print("=" * 60)
    print(f"Starting web server on http://{host}:{port}")
    print(f"PID: {os.getpid()}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=debug, host=host, port=port)