import time
import subprocess
import os
import pytz
from datetime import datetime, timedelta
import sys

# Configuration
FIXED_RECIPIENT = "kartik.notkarthik@gmail.com"
FIXED_NAME = "Karry"
IST = pytz.timezone('Asia/Kolkata')
LOG_FILE = "scheduler.log"

def log_message(message):
    timestamp = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

def run_pulse_job():
    log_message("Triggering Scheduled GROWW Pulse...")
    try:
        # We run the command from the 'backend' directory to satisfy imports
        # Or we can set PYTHONPATH. Let's use cwd for simplicity and reliability.
        cmd = [
            sys.executable, 
            "main.py", 
            "--email", FIXED_RECIPIENT, 
            "--name", FIXED_NAME
        ]
        
        backend_dir = os.path.join(os.getcwd(), "backend")
        
        log_message(f"Executing: {' '.join(cmd)} in {backend_dir}")
        
        # Run the backend pipeline
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            cwd=backend_dir
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            log_message("Successfully executed scheduled pipeline.")
            log_message(f"Output: {stdout[:2000]}...") # Log more output
        else:
            log_message(f"ERROR during scheduled execution:\n{stderr}")
            
    except Exception as e:
        log_message(f"Scheduler Job failed: {e}")

def main():
    log_message("--- GROWW Pulse Daily Scheduler Started ---")
    log_message(f"Target Time: 10:00 AM IST Daily")
    log_message(f"Recipient: {FIXED_RECIPIENT}")
    log_message(f"Logs: {os.path.abspath(LOG_FILE)}")
    log_message("---------------------------------------------")

    last_run_date = None
    
    while True:
        now_ist = datetime.now(IST)
        current_date = now_ist.date()
        
        # Trigger at 10:00 AM IST
        if now_ist.hour == 10 and now_ist.minute == 0:
            if last_run_date != current_date:
                run_pulse_job()
                last_run_date = current_date
                # Sleep for 61 seconds to ensure we don't trigger again in the same minute
                time.sleep(61)
        
        # Check every 30 seconds to stay responsive
        time.sleep(30)

if __name__ == "__main__":
    main()
