import logging
import os
import time
import shutil
import sys
import tempfile

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(module)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("fsevents").setLevel(logging.WARNING)

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
    logger.info("initial_size %s", initial_size)
    time.sleep(0.5)  # Wait briefly
    if initial_size == 0:
        return False
    final_size = os.path.getsize(filepath)
    logger.info("initial_size %s final_size %s", initial_size, final_size)
    return initial_size == final_size

# Function to handle file creation event
def handle_file_creation(filepath):
    logger.info("Detected new file matching firmware download pattern: %s", filepath)
    # while not is_file_complete(filepath):
    #       logger.info("download is still not completed..")
    #
    # logger.info(f"Detected download completed: %s", filepath)

    try:
        while True:
            try:
                shutil.copy(firmware_path, os.path.join(monitor_directory, filepath))
                logger.info("Copied %s to %s", firmware_path, filepath)
            except Exception as e:
                logger.exception("Failed to copy %s to %s", firmware_path, filepath)
                raise
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("CTRL-C pressed, exiting..")
        sys.exit(0)

# Define a custom event handler to monitor filesystem events
class CustomFileSystemEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        logger.debug(f"detected created file {filepath}")
        if os.path.basename(filepath).startswith(pattern):
            handle_file_creation(filepath)

if len(sys.argv) == 1:
    firmware_path = "firmware/duran_encrypted_prod_1.0.3-ee3f55e.bin"
elif len(sys.argv) == 2:
    firmware_path = sys.argv[1]
else:
    print(f'usage: {sys.argv[0]} [firmware-bin-file-path]', file=sys.stderr)
    sys.exit(1)

assert os.path.exists(firmware_path)

monitor_directory = os.path.realpath(tempfile.gettempdir())


pattern = "Bose Updater"
logger.info("monitoring directory: %s", monitor_directory)

# Set up filesystem event monitoring
event_handler = CustomFileSystemEventHandler()
observer = Observer()
observer.schedule(event_handler, monitor_directory, recursive=False)
observer.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    logger.info("CTRL-C pressed, exiting..")
    sys.exit(0)


