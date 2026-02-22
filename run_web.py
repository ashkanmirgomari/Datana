#!/usr/bin/env python3
# run_web.py
import os
import sys
import socket

# تنظیم مسیر
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from web.app import app

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 60)
    print("Datana Web Interface")
    print("=" * 60)
    print(f"Local access: http://127.0.0.1:5000")
    print(f"Network access: http://{local_ip}:5000")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)