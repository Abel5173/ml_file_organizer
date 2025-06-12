import time
import os
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from organizer.organizer import handle_file

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        self.processing_files = set()
        self.file_sizes = {}
        self.stable_time = 2  # seconds to wait for file size to stabilize

    def wait_for_download_completion(self, file_path):
        """Wait for a file to finish downloading by monitoring its size."""
        if file_path in self.processing_files:
            return False

        self.processing_files.add(file_path)
        try:
            last_size = -1
            stable_count = 0
            start_time = time.time()

            while True:
                if not os.path.exists(file_path):
                    print(f"File was removed before download completed: {file_path}")
                    return False

                current_size = os.path.getsize(file_path)
                
                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 2:  # Size hasn't changed for 2 checks
                        # Check if file is accessible (not locked by download process)
                        try:
                            with open(file_path, 'rb') as f:
                                f.read(1)
                            return True
                        except (IOError, PermissionError):
                            # File is still being written to
                            stable_count = 0
                else:
                    stable_count = 0
                    last_size = current_size

                # Timeout after 5 minutes
                if time.time() - start_time > 300:
                    print(f"Timeout waiting for download to complete: {file_path}")
                    return False

                time.sleep(1)
        finally:
            self.processing_files.remove(file_path)

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"\nNew file detected: {file_path}")
            
            # Wait for download to complete
            if self.wait_for_download_completion(file_path):
                print(f"Download completed, processing file: {file_path}")
                handle_file(file_path)
            else:
                print(f"Skipping incomplete download: {file_path}")

def start_watching():
    # Define paths
    downloads_path = '/mnt/hdd/Downloads'
    telegram_path = os.path.join(downloads_path, 'Telegram Desktop')
    
    # Create Telegram Desktop directory if it doesn't exist
    os.makedirs(telegram_path, exist_ok=True)
    
    # Set up the observer
    event_handler = FileHandler()
    observer = Observer()
    
    # Watch both directories
    observer.schedule(event_handler, downloads_path, recursive=False)
    observer.schedule(event_handler, telegram_path, recursive=False)
    
    observer.start()
    print(f"Watching for new files in:")
    print(f"  - {downloads_path}")
    print(f"  - {telegram_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping file watcher...")
    
    observer.join()

if __name__ == "__main__":
    start_watching()