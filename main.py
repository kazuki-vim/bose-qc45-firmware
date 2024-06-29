import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Define the directory to monitor
monitor_directory = os.path.join(os.getenv('LOCALAPPDATA'), 'Temp')
pattern = "Bose Updater"
print("directory: ", monitor_directory)

# Function to check if a file with the given pattern is created
def check_for_file_creation():
    for filename in os.listdir(monitor_directory):
        if filename.startswith(pattern):
            return filename
    return None

# Function to check if a file is completely written
def is_file_complete(filepath):
    # Check if the file size remains constant over a short interval
    initial_size = os.path.getsize(filepath)
    time.sleep(0.5)  # Wait briefly
    final_size = os.path.getsize(filepath)
    return initial_size == final_size

# Function to handle file creation event
def handle_file_creation(filepath):
    print(f"[datetime.now().strftime('%H:%M:%S')] Detected new file: {filepath}")

    time_sleep = 3.5
    print(f"Wait: {time_sleep}s")
    time.sleep(time_sleep)

    print(f"[datetime.now().strftime('%H:%M:%S')] File writing complete: {filepath}")

    # Copy another file from download folder and rename it
    download_folder = monitor_directory
    file_to_copy = "bose.bin"

    try:
        shutil.copy(os.path.join(download_folder, file_to_copy), os.path.join(monitor_directory, filepath))
        print(f"[datetime.now().strftime('%H:%M:%S')] Copied {file_to_copy} to {filepath}")
    except Exception as e:
        print(f"Failed to copy {file_to_copy} to {filepath}: {e}")

# Define a custom event handler to monitor filesystem events
class CustomFileSystemEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        if os.path.basename(filepath).startswith(pattern):
            handle_file_creation(filepath)

# Set up filesystem event monitoring
event_handler = CustomFileSystemEventHandler()
observer = Observer()
observer.schedule(event_handler, monitor_directory, recursive=False)
observer.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
