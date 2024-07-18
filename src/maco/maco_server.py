import subprocess
import atexit
import os
import shutil
import time
import psutil

def start_server():
    # Unload the notification center UI
    subprocess.run(["launchctl", "unload", "-w", "/System/Library/LaunchAgents/com.apple.notificationcenterui.plist"])
    
    # Run the maco.py program
    gui_script_path = os.path.join(os.path.dirname(__file__), "maco.py")
    subprocess.Popen(["python3", gui_script_path])

def stop_server(is_shutdown=False):
    # Load the notification center UI
    subprocess.run(["launchctl", "load", "-w", "/System/Library/LaunchAgents/com.apple.notificationcenterui.plist"])
    
    if is_shutdown:
        # Delete the database file and viewed_notifications only on system shutdown or restart
        delete_files()

def delete_files():
    def find_notification_db():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    "lsof -p $(ps aux | grep -m1 usernoted | awk '{ print $2 }') | awk '{ print $NF }' | grep 'db2/db$' | xargs dirname",
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                db_path = result.stdout.strip()
                if db_path:
                    return os.path.join(db_path, 'db')
                else:
                    print(f"Notification Center database directory not found. Attempt {attempt + 1}/{max_retries}")
            except subprocess.CalledProcessError as e:
                print(f"Error finding Notification Center database: {e}. Attempt {attempt + 1}/{max_retries}")
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait for 1 second before retrying
        
        print("Failed to find Notification Center database after multiple attempts.")
        return None
    
    db_path = find_notification_db()
    viewed_notifications_path = os.path.expanduser('~/.config/maco/viewed_notifications.json')
    
    if db_path and os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Successfully removed database file: {db_path}")
        except OSError as e:
            print(f"Error removing database file: {e}")
    else:
        print("Database file not found or could not be accessed.")

    if os.path.exists(viewed_notifications_path):
        try:
            os.remove(viewed_notifications_path)
            print(f"Successfully removed viewed notifications file: {viewed_notifications_path}")
        except OSError as e:
            print(f"Error removing viewed notifications file: {e}")
    else:
        print("Viewed notifications file not found.")

def is_system_shutting_down():
    # Check if the system is shutting down or restarting
    try:
        output = subprocess.check_output(["pmset", "-g", "log"], universal_newlines=True)
        return "shutdown cause" in output.lower() or "restart" in output.lower()
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    # Register the stop_server function to be called on exit
    atexit.register(stop_server, is_shutdown=is_system_shutting_down())
    
    # Start the server
    start_server()
    
    # Keep the server running
    try:
        while True:
            time.sleep(1)  # Sleep for 1 second to reduce CPU usage
    except KeyboardInterrupt:
        # Handle keyboard interrupt gracefully
        print("Keyboard interrupt detected. Shutting down...")
    finally:
        stop_server(is_shutdown=is_system_shutting_down())