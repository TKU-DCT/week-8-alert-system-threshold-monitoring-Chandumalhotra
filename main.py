import psutil
from datetime import datetime
import sqlite3
import os
import time
import subprocess
import platform

DB_NAME = "log.db"

# Define threshold values
CPU_THRESHOLD = 80.0
MEM_THRESHOLD = 85.0
DISK_THRESHOLD = 90.0

def get_system_info():
    # TODO: Collect system info (timestamp, cpu, memory, disk, ping)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    ping_status, ping_time = ping_host("8.8.8.8")
    
    return (timestamp, cpu, memory, disk, ping_status, ping_time)

def ping_host(host):
    # TODO: Ping 8.8.8.8 and return ("UP", ms) or ("DOWN", -1)
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            ping_time = parse_ping_time(result.stdout)
            return ("UP", ping_time)
        else:
            return ("DOWN", -1)
    except Exception as e:
        return ("DOWN", -1)

def parse_ping_time(output):
    # TODO: Extract ping response time from command output
    try:
        if platform.system() == "Windows":
            # Windows format: "Reply from ...: bytes=32 time=20ms"
            import re
            match = re.search(r'time[<=]+(\d+)ms', output)
            if match:
                return float(match.group(1))
        else:
            # Linux/Mac format: "time=20.1 ms"
            import re
            match = re.search(r'time=([0-9.]+)\s*ms', output)
            if match:
                return float(match.group(1))
    except Exception as e:
        pass
    return 0.0

def insert_log(data):
    # TODO: Insert log data into SQLite (reuse Week 7 function)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                ping_status TEXT,
                ping_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert data
        cursor.execute("""
            INSERT INTO system_log (timestamp, cpu_usage, memory_usage, disk_usage, ping_status, ping_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        
        conn.commit()
        conn.close()
        print(f"Logged: {data}")
    except Exception as e:
        print(f"Error inserting log: {e}")

def check_alerts(cpu, memory, disk):
    # TODO: Print alert messages if any value exceeds its threshold
    if cpu > CPU_THRESHOLD:
        print(f"⚠️ ALERT: High CPU usage! ({cpu}%)")
    if memory > MEM_THRESHOLD:
        print(f"⚠️ ALERT: High Memory usage! ({memory}%)")
    if disk > DISK_THRESHOLD:
        print(f"⚠️ ALERT: Low Disk Space! ({disk}%)")

if __name__ == "__main__":
    # TODO: Initialize and log 5 records (every 10 seconds)
    # For each record, call check_alerts()
    print("Starting system monitoring and alert system...")
    print(f"Thresholds - CPU: {CPU_THRESHOLD}%, Memory: {MEM_THRESHOLD}%, Disk: {DISK_THRESHOLD}%")
    print("=" * 60)
    
    for i in range(5):
        try:
            # Get system information
            data = get_system_info()
            timestamp, cpu, memory, disk, ping_status, ping_time = data
            
            # Insert into database
            insert_log(data)
            
            # Check and trigger alerts
            check_alerts(cpu, memory, disk)
            
            print("-" * 60)
            
            # Wait 10 seconds before next record (except after the last one)
            if i < 4:
                print("Waiting 10 seconds before next record...")
                time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
    
    print("Monitoring complete!")
