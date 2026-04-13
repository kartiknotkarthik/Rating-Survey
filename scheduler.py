import schedule
import time
import subprocess
import os
import pytz
from datetime import datetime
import sys

# Configuration
FIXED_RECIPIENT = "kartik.notkarthik@gmail.com"
FIXED_NAME = "Karry"
SCHEDULED_TIME_IST = "22:00"  # 10:00 PM
SCHEDULED_DAY = "monday"
IST = pytz.timezone('Asia/Kolkata')

def run_pulse_job():
    print(f"\n[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Triggering Scheduled GROWW Pulse...")
    try:
        # Construct the command to run the CLI main.py
        # We use sys.executable to ensure we use the same python environment
        cmd = [
            sys.executable, 
            "main.py", 
            "--email", FIXED_RECIPIENT, 
            "--name", FIXED_NAME
        ]
        
        # Run the backend pipeline
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Successfully executed scheduled pipeline.")
            print(stdout)
        else:
            print(f"Error during scheduled execution: {stderr}")
            
    except Exception as e:
        print(f"Scheduler Job failed: {e}")

def main():
    print("--- GROWW Pulse Weekly Scheduler Started ---")
    print(f"Target: Every {SCHEDULED_DAY.capitalize()} at {SCHEDULED_TIME_IST} IST")
    print(f"Recipient: {FIXED_RECIPIENT}")
    print("---------------------------------------------")

    # Day mapping
    job_scheduler = getattr(schedule.every(), SCHEDULED_DAY)
    
    # Schedule logic: 
    # Since 'schedule' uses local time, we calculate the offset or use a trick
    # Here we check the time in a loop for simpler cross-platform IST support
    
    while True:
        now_ist = datetime.now(IST)
        
        # Check if today is the scheduled day and current time matches
        if now_ist.strftime("%A").lower() == SCHEDULED_DAY:
            if now_ist.strftime("%H:%M") == SCHEDULED_TIME_IST:
                run_pulse_job()
                # Wait 61 seconds to avoid triggering multiple times in the same minute
                time.sleep(61)
        
        # Check every 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    main()
