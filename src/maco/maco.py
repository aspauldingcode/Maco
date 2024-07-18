import codecs
import sqlite3
import sys
import os
import uuid
import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import biplist
import configparser
import signal
import psutil
import json
import argparse
import atexit
import shutil

def kill_existing_processes():
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'python' and process.pid != current_process.pid:
            try:
                cmdline = process.info['cmdline']
                if cmdline and 'mac_notifications_gui.py' in cmdline[-1]:
                    print(f"Terminating existing process: {process.pid}")
                    process.terminate()
                    process.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass

def RemoveTabsNewLines(str):
    try:
        return str.replace("\t", " ").replace("\r", " ").replace("\n", "")
    except:
        pass
    return str

def ReadMacAbsoluteTime(mac_abs_time):
    try:
        return datetime.datetime.utcfromtimestamp(mac_abs_time + 978307200).strftime('%Y-%m-%d %H:%M')
    except:
        pass
    return ''

import json

app_id_list_path = os.path.expanduser('~/.config/maco/app_id_list.json')

# Check if the file exists, if not create it and populate with example messages
if not os.path.exists(app_id_list_path):
    os.makedirs(os.path.dirname(app_id_list_path), exist_ok=True)
    example_data = {
        "com.example.app1": "Example App 1",
        "com.apple.mobilesms": "Messages",
        "com.apple.scripteditor2": "Applescript",
    }
    with open(app_id_list_path, 'w') as f:
        json.dump(example_data, f, indent=4)

# Read the file
with open(app_id_list_path, 'r') as f:
    APP_ID_TO_NAME = json.load(f)

# Create a reverse mapping
NAME_TO_APP_ID = {v: k for k, v in APP_ID_TO_NAME.items()}

# Load blacklist
blacklist_path = os.path.expanduser('~/.config/maco/blacklist')
if not os.path.exists(blacklist_path):
    os.makedirs(os.path.dirname(blacklist_path), exist_ok=True)
    with open(blacklist_path, 'w') as f:
        f.write("# Add app IDs or names to blacklist, one per line\n")
        f.write("# Example:\n")
        f.write("# com.example.app1\n")
        f.write("# Messages\n")

with open(blacklist_path, 'r') as f:
    BLACKLIST = set(line.strip() for line in f if line.strip() and not line.startswith('#'))

# Convert app names in blacklist to app IDs
BLACKLIST = set(NAME_TO_APP_ID.get(item, item) for item in BLACKLIST)

def rounded_rect(canvas, x, y, w, h, c, outline, fill, border_width):
    if c == 0:
        # Draw a rectangle with sharp corners
        canvas.create_rectangle(x, y, x+w, y+h, fill=fill, outline=outline, width=border_width)
    else:
        # Draw the background with rounded corners
        canvas.create_rectangle(x+c, y+c, x+w-c, y+h-c, fill=fill, outline="")
        canvas.create_arc(x, y, x+2*c, y+2*c, start=90, extent=90, fill=fill, outline="")
        canvas.create_arc(x+w-2*c, y+h-2*c, x+w, y+h, start=270, extent=90, fill=fill, outline="")
        canvas.create_arc(x+w-2*c, y, x+w, y+2*c, start=0, extent=90, fill=fill, outline="")
        canvas.create_arc(x, y+h-2*c, x+2*c, y+h, start=180, extent=90, fill=fill, outline="")
        
        # Draw the outline on top of the background
        canvas.create_arc(x, y, x+2*c, y+2*c, start=90, extent=90, style="arc", outline=outline, width=border_width)
        canvas.create_arc(x+w-2*c, y+h-2*c, x+w, y+h, start=270, extent=90, style="arc", outline=outline, width=border_width)
        canvas.create_arc(x+w-2*c, y, x+w, y+2*c, start=0, extent=90, style="arc", outline=outline, width=border_width)
        canvas.create_arc(x, y+h-2*c, x+2*c, y+h, start=180, extent=90, style="arc", outline=outline, width=border_width)
        canvas.create_line(x+c, y, x+w-c, y, fill=outline, width=border_width)
        canvas.create_line(x+c, y+h, x+w-c, y+h, fill=outline, width=border_width)
        canvas.create_line(x, y+c, x, y+h-c, fill=outline, width=border_width)
        canvas.create_line(x+w, y+c, x+w, y+h-c, fill=outline, width=border_width)

class NotificationWindow:
    def __init__(self, notification, x, y, auto_hide_delay, on_close_callback, config):
        self.window = tk.Toplevel()
        self.window.title(f"Notification from {notification['Bundle']}")
        
        # Get window dimensions from config
        width = int(config.get('width', '300'))
        height = int(config.get('height', '100'))
        padding = int(config.get('padding', '5'))
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")  # Initial window size
        self.window.overrideredirect(True)  # Remove the title bar
        self.window.attributes("-topmost", True)  # Keep window on top
        
        # Set background color and opacity from config
        bg_color = config.get('background-color', '#ffffff')
        bg_opacity = 0.0
        if len(bg_color) == 9:  # Including '#'
            bg_opacity = int(bg_color[7:], 16) / 255.0
            bg_color = bg_color[:7]
        
        # Set border color and size from config
        border_color = config.get('border-color', '#8ec07c')
        border_opacity = 1.0
        if len(border_color) == 9:  # Including '#'
            border_opacity = int(border_color[7:], 16) / 255.0
            border_color = border_color[:7]
        border_size = int(config.get('border-size', '2'))
        
        # Get border radius from config
        border_radius = int(config.get('border-radius', '0'))
        
        # Create a canvas that fills the entire window with transparent background
        self.window.attributes("-transparent", True)
        canvas = tk.Canvas(self.window, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set the canvas background to a fully transparent color
        canvas.configure(bg='systemTransparent')
        
        # Draw rounded rectangle for both border and background
        rounded_rect(canvas, border_size, border_size, width - 2*border_size, height - 2*border_size, border_radius, border_color, bg_color, border_size)
        
        # Create a frame inside the rounded rectangle
        inner_frame = tk.Frame(canvas, bg=bg_color)
        canvas.create_window(width // 2, height // 2, window=inner_frame, width=width - 2*border_size - 2*border_radius, height=height - 2*border_size - 2*border_radius)
        
        frame = ttk.Frame(inner_frame, padding=padding)
        frame.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('default')  # Use default theme
        style.configure('TFrame', background=bg_color)
        
        text_color = config.get('text-color', '#d5c4a1')
        if len(text_color) == 9:  # Including '#'
            text_color = text_color[:7]
        style.configure('TLabel', background=bg_color, foreground=text_color)
        
        header_frame = ttk.Frame(frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=2)
        
        # Use app name if available, otherwise use app ID
        app_name = APP_ID_TO_NAME.get(notification['Bundle'], notification['Bundle'])
        
        # Parse font configuration
        font_config = config.get('font', 'San Francisco 10').split()
        font_family = ' '.join(font_config[:-1]) if len(font_config) > 1 else font_config[0]
        font_size = int(font_config[-1])
        
        ttk.Label(header_frame, text=app_name, font=(font_family, font_size), style='TLabel').pack(side=tk.LEFT)
        ttk.Label(header_frame, text=notification['Time'], font=(font_family, font_size), style='TLabel').pack(side=tk.RIGHT)
        
        ttk.Label(frame, text=notification['Title'], font=(font_family, font_size, "bold"), style='TLabel').pack(pady=2)
        if notification['SubTitle']:
            ttk.Label(frame, text=notification['SubTitle'], font=(font_family, font_size, "italic"), style='TLabel').pack(pady=2)
        ttk.Label(frame, text=notification['Message'], wraplength=280, font=(font_family, font_size), style='TLabel').pack(pady=5)
        # Adjust window height based on content
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        self.window.geometry(f"{width}x{height}+{x}+{y - height}")  # Adjust y to raise the window

        # Set window opacity immediately without fading
        self.window.attributes("-alpha", 1 - bg_opacity)

        # Schedule the window to close after the specified delay
        self.window.after(auto_hide_delay, self.close)
        self.on_close_callback = on_close_callback

    def close(self):
        self.window.destroy()
        self.on_close_callback(self)

class MacoNotifications:
    def __init__(self, config_path=None):
        kill_existing_processes()
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.active_windows = []
        self.config_path = config_path
        self.load_config()
        
        print("Raw config:", self.config)  # Debug print
        
        self.max_visible = int(self.config.get('max-visible', '-1'))
        self.auto_hide_delay = int(self.config.get('default-timeout', '5000'))
        self.max_history = int(self.config.get('max-history', '5'))
        self.sort_order = self.config.get('sort', '-time')
        self.history = []
        self.blacklist = BLACKLIST  # Use the global BLACKLIST set
        print(f"Config settings: max_visible={self.max_visible}, auto_hide_delay={self.auto_hide_delay}, max_history={self.max_history}, sort_order={self.sort_order}, blacklist={self.blacklist}")
        
        # Set root background color and opacity from config
        bg_color = self.config.get('background-color', '#ffffff')
        bg_opacity = 0.0
        if len(bg_color) == 9:  # Including '#'
            bg_opacity = int(bg_color[7:], 16) / 255.0
            bg_color = bg_color[:7]
        if not bg_color.startswith('#'):
            bg_color = f'#{bg_color}'
        
        # Create a panel that fills the entire root window
        self.panel = tk.Frame(self.root, bg=bg_color)
        self.panel.pack(fill=tk.BOTH, expand=True)
        
        self.root.configure(bg=bg_color)
        self.root.attributes("-alpha", 1 - bg_opacity)
        
        self.viewed_notifications = self.load_viewed_notifications()
        self.notifications_queue = []
        self.process_notifications()

    def load_config(self):
        if self.config_path:
            config_path = os.path.expanduser(self.config_path)
        else:
            config_path = os.path.expanduser('~/.config/maco/config')
        
        if not os.path.exists(config_path):
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
        
        self.config = {}
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = value.strip()
        
        # print(f"Loaded config from {config_path}:", self.config)  # Debug print

        self.anchor = self.config.get('anchor', 'top-right')
        print(f"Config settings: ... anchor={self.anchor}")

    def show_next_notifications(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Define initial position and direction based on anchor
        if self.anchor.startswith('top'):
            y = 0
            direction = 1  # Move downwards
        elif self.anchor.startswith('bottom'):
            y = screen_height
            direction = -1  # Move upwards
        else:  # center
            y = screen_height // 2
            direction = 1  # Move downwards

        if 'left' in self.anchor:
            x = 0
        elif 'right' in self.anchor:
            x = screen_width
        else:  # center
            x = screen_width // 2

        while self.notifications_queue and (self.max_visible == -1 or len(self.active_windows) < self.max_visible):
            notification = self.notifications_queue.pop(0)
            
            # Adjust x and y based on anchor
            if 'right' in self.anchor:
                x -= self.config.get('width', 300)
            if self.anchor.startswith('bottom'):
                y -= self.config.get('height', 100)
            
            window = NotificationWindow(self.root, notification, self.config, x, y, self.auto_hide_delay, self.on_notification_closed)
            self.active_windows.append(window)
            
            # Update y for next notification
            y += direction * (self.config.get('height', 100) + self.config.get('margin', 10))

        self.update_history()

    def load_viewed_notifications(self):
        statefile_path = os.path.expanduser('~/.config/maco/viewed_notifications.json')
        if os.path.exists(statefile_path):
            with open(statefile_path, 'r') as f:
                return json.load(f)
        else:
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(statefile_path), exist_ok=True)
            with open(statefile_path, 'w') as f:
                json.dump({}, f)
            return {}

    def save_viewed_notifications(self):
        statefile_path = os.path.expanduser('~/.config/maco/viewed_notifications.json')
        os.makedirs(os.path.dirname(statefile_path), exist_ok=True)
        with open(statefile_path, 'w') as f:
            json.dump(self.viewed_notifications, f)

    def process_notifications(self):
        try:
            input_path = self.find_notification_db()
            if not input_path:
                print("Error: Notification database not found.")
                self.retry_process_notifications()
                return

            output_path = "/tmp/Maco-notifications.csv"
            self.process_notification_db(input_path, output_path)
            
            notifications = self.read_notifications(output_path)
            
            # Filter out viewed notifications and blacklisted apps
            new_notifications = [n for n in notifications if self.is_new_notification(n) and not self.is_blacklisted(n['Bundle'])]
            
            # Sort notifications based on the configured sort order
            if self.sort_order == '+time':
                new_notifications.sort(key=lambda x: x['Time'])
            elif self.sort_order == '-time':
                new_notifications.sort(key=lambda x: x['Time'], reverse=True)
            elif self.sort_order == '+priority':
                new_notifications.sort(key=lambda x: x.get('Priority', 0))
            elif self.sort_order == '-priority':
                new_notifications.sort(key=lambda x: x.get('Priority', 0), reverse=True)
            
            self.notifications_queue.extend(new_notifications)
            self.show_next_notifications()
            
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            # Schedule the next check
            self.root.after(1000, self.process_notifications)

    def is_new_notification(self, notification):
        key = f"{notification['Time']}_{notification['Bundle']}_{notification['Title']}"
        if key not in self.viewed_notifications:
            self.viewed_notifications[key] = True
            self.save_viewed_notifications()  # Save after each new notification
            return True
        return False

    def is_blacklisted(self, bundle):
        # Check if the bundle (app ID) is in the blacklist
        if bundle.strip() in self.blacklist:
            return True
        
        # Check if the app name corresponding to the bundle is in the blacklist
        app_name = APP_ID_TO_NAME.get(bundle.strip())
        if app_name and app_name in self.blacklist:
            return True
        
        return False

    def retry_process_notifications(self):
        print("Retrying to process notifications...")
        time.sleep(1)
        self.process_notifications()

    def find_notification_db(self):
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
                return None
        except subprocess.CalledProcessError as e:
            return None

    def process_notification_db(self, input_path, output_path):
        try:
            with sqlite3.connect(input_path) as conn:
                if not hasattr(self, 'last_db_message') or self.last_db_message != "Opened database successfully":
                    print("Opened database successfully")
                    self.last_db_message = "Opened database successfully"

                db_version = self.get_db_version(conn)
                if db_version >= 17:
                    self.parse_ver_17_db(conn, input_path, output_path)
                else:
                    self.parse_older_db(conn, output_path)
        except sqlite3.Error as e:
            raise Exception(f"SQLite error processing notification database: {str(e)}")
        except Exception as ex:
            raise Exception(f"Error processing notification database: {str(ex)}")
        
    def get_db_version(self, conn):
        try:
            cursor = conn.execute("SELECT value from dbinfo WHERE key LIKE 'compatibleVersion'")
            for row in cursor:
                return int(row[0])
        except Exception as ex:
            print(f"Exception trying to determine db version: {str(ex)}")
        return 15

    def parse_ver_17_db(self, conn, input_path, output_path):
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT (SELECT identifier from app where app.app_id=record.app_id) as app, "
                                  "uuid, data, presented, delivered_date FROM record")

            with codecs.open(output_path, 'w', encoding='utf-16') as csv:
                csv.write("Time\tShown\tBundle\tAppPath\tUUID\tTitle\tSubTitle\tMessage\r\n")
                for row in cursor:
                    try:
                        plist = biplist.readPlistFromString(row['data'])
                        req = plist.get('req', {})
                        title = RemoveTabsNewLines(req.get('titl', ''))
                        subtitle = RemoveTabsNewLines(req.get('subt', ''))
                        message = RemoveTabsNewLines(req.get('body', ''))
                        time = ReadMacAbsoluteTime(row['delivered_date'])
                        csv.write(f"{time}\t{row['presented']}\t{row['app']}\t\t{row['uuid']}\t{title}\t{subtitle}\t{message}\r\n")
                    except Exception as ex:
                        print(f"Error processing row: {str(ex)}")
        except Exception as ex:
            print(f"Error parsing version 17+ database: {str(ex)}")

    def parse_older_db(self, conn, output_path):
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT datetime(date_presented + 978307200, 'unixepoch', 'localtime') as time, "
                                  "actually_presented AS shown, "
                                  "(SELECT bundleid from app_info WHERE app_info.app_id = presented_notifications.app_id) AS bundle, "
                                  "(SELECT last_known_path from app_loc WHERE app_loc.app_id = presented_notifications.app_id) AS appPath, "
                                  "(SELECT uuid from notifications WHERE notifications.note_id = presented_notifications.note_id) AS uuid, "
                                  "(SELECT encoded_data from notifications WHERE notifications.note_id = presented_notifications.note_id) AS dataPlist "
                                  "from presented_notifications")

            with codecs.open(output_path, 'w', encoding='utf-16') as csv:
                csv.write("Time\tShown\tBundle\tAppPath\tUUID\tTitle\tSubTitle\tMessage\r\n")
                for row in cursor:
                    try:
                        plist = biplist.readPlistFromString(row['dataPlist'])
                        title = subtitle = message = ""
                        title_index = int(plist['$objects'][1].get('NSTitle', 2))
                        subtitle_index = int(plist['$objects'][1].get('NSSubtitle', -1))
                        text_index = int(plist['$objects'][1].get('NSInformativetext', 3))
                        
                        title = RemoveTabsNewLines(plist['$objects'][title_index])
                        if subtitle_index > -1:
                            subtitle = RemoveTabsNewLines(plist['$objects'][subtitle_index])
                        message = RemoveTabsNewLines(plist['$objects'][text_index])
                        
                        csv.write(f"{row['time']}\t{row['shown']}\t{row['bundle']}\t{row['appPath']}\t{row['uuid']}\t{title}\t{subtitle}\t{message}\r\n")
                    except Exception as ex:
                        print(f"Error processing row: {str(ex)}")
        except Exception as ex:
            print(f"Error parsing older version database: {str(ex)}")

    def read_notifications(self, file_path):
        notifications = []
        encodings = ['utf-16', 'utf-8', 'utf-8-sig', 'latin-1']
        for encoding in encodings:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as file:
                    lines = file.readlines()[1:]  # Skip header
                    for line in lines:
                        parts = line.strip().split('\t')
                        if len(parts) >= 5:
                            notifications.append({
                                'Time': parts[0],
                                'Bundle': parts[2],
                                'Title': parts[5],
                                'SubTitle': parts[6] if len(parts) > 6 else '',
                                'Message': parts[7] if len(parts) > 7 else ''
                            })
                break
            except UnicodeDecodeError:
                continue
        
        if not notifications:
            raise Exception("Unable to read notifications from the file.")
        
        return notifications

    def display_notifications(self, notifications):
        self.notifications_queue = notifications
        self.show_next_notifications()

    def show_next_notifications(self):
        if self.active_windows:
            # If there are active windows, wait for them to close
            self.root.after(100, self.show_next_notifications)
            return

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(self.config.get('width', 300))
        window_height = int(self.config.get('height', 60))
        margin = int(self.config.get('margin', 20))

        # Get anchor from config, default to 'bottom-right' if not specified
        anchor = self.config.get('anchor', 'bottom-right')

        # Calculate the number of notifications to show
        num_notifications = min(self.max_visible if self.max_visible != -1 else len(self.notifications_queue), len(self.notifications_queue))

        # Calculate base x and y positions based on anchor
        if 'left' in anchor:
            x = margin
        elif 'right' in anchor:
            x = screen_width - window_width - margin
        else:  # center
            x = (screen_width - window_width) // 2

        if 'top' in anchor:
            y = margin
            direction = 1  # Move downwards
        elif 'bottom' in anchor:
            y = screen_height - window_height - margin
            direction = -1  # Move upwards
        else:  # center
            y = (screen_height - window_height) // 2
            direction = 1  # Move downwards

        for i in range(num_notifications):
            notification = self.notifications_queue.pop(0)
            self.show_notification(notification, x, y)
            y += direction * (window_height + margin)

        if self.notifications_queue:
            self.root.after(self.auto_hide_delay + 100, self.show_next_notifications)

    def show_notification(self, notification, x, y):
        window = NotificationWindow(notification, x, y, self.auto_hide_delay, self.remove_window, self.config)
        self.active_windows.append(window)

    def remove_window(self, window):
        if window in self.active_windows:
            self.active_windows.remove(window)
        
        if not self.active_windows and self.notifications_queue:
            self.root.after(100, self.show_next_notifications)

    def run(self):
        self.root.mainloop()

def start_server():
    subprocess.run(["launchctl", "unload", "-w", "/System/Library/LaunchAgents/com.apple.notificationcenterui.plist"])
    maco = MacoNotifications()
    maco.run()

def stop_server(is_shutdown=False):
    subprocess.run(["launchctl", "load", "-w", "/System/Library/LaunchAgents/com.apple.notificationcenterui.plist"])
    if is_shutdown:
        delete_files()

def delete_files():
    db_path = find_notification_db()
    viewed_notifications_path = os.path.expanduser('~/.config/maco/viewed_notifications.json')
    
    delete_file(db_path, "database")
    delete_file(viewed_notifications_path, "viewed notifications")

def find_notification_db():
    max_retries = 3
    cmd = "lsof -p $(ps aux | grep -m1 usernoted | awk '{ print $2 }') | awk '{ print $NF }' | grep 'db2/db$' | xargs dirname"
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            db_dir = result.stdout.strip()
            if db_dir:
                return os.path.join(db_dir, 'db')
            print(f"Notification Center database directory not found. Attempt {attempt + 1}/{max_retries}")
        except subprocess.CalledProcessError as e:
            print(f"Error finding Notification Center database: {e}. Attempt {attempt + 1}/{max_retries}")
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print("Failed to find Notification Center database after multiple attempts.")
    return None

def delete_file(file_path, file_type):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Successfully removed {file_type} file: {file_path}")
        except OSError as e:
            print(f"Error removing {file_type} file: {e}")
    else:
        print(f"{file_type.capitalize()} file not found or could not be accessed.")

def is_system_shutting_down():
    try:
        output = subprocess.check_output(["pmset", "-g", "log"], universal_newlines=True)
        return "shutdown cause" in output.lower() or "restart" in output.lower()
    except subprocess.CalledProcessError:
        return False

def signal_handler(signum, frame):
    print("Received signal to terminate. Shutting down...")
    stop_server(is_shutdown=is_system_shutting_down())
    exit(0)

def run_continuously():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(stop_server, is_shutdown=is_system_shutting_down())
    
    start_server()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

def main():
    parser = argparse.ArgumentParser(description="Maco Notifications")
    parser.add_argument('-c', '--config', help="Custom path to the config file. Default is ~/.config/maco/config.")
    args = parser.parse_args()
    
    maco = MacoNotifications(config_path=args.config)
    maco.run()

if __name__ == "__main__":
    main()