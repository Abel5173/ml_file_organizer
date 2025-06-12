import shutil
import os 
from classifier.topic_classifier import detect_topic
from classifier.file_classifier import get_file_type
from utils.file_utils import create_directory_structure, rename_file, save_metadata
import hashlib

BASE_PATH = '/mnt/hdd/Downloads/'
TELEGRAM_PATH = os.path.join(BASE_PATH, 'Telegram Desktop')

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_duplicate(file_path, dest_dir):
    """Check if a file is a duplicate of any existing file."""
    if not os.path.exists(dest_dir):
        return False
        
    # If the file is already in the destination directory, it's not a duplicate
    if os.path.dirname(file_path) == dest_dir:
        return False
        
    new_file_hash = calculate_file_hash(file_path)
    
    for existing_file in os.listdir(dest_dir):
        if os.path.isfile(os.path.join(dest_dir, existing_file)):
            existing_file_path = os.path.join(dest_dir, existing_file)
            if calculate_file_hash(existing_file_path) == new_file_hash:
                return True
    return False

def ensure_extension(file_path, new_name):
    """Ensure the new filename has the correct extension."""
    original_ext = os.path.splitext(file_path)[1]
    if not original_ext and os.path.exists(file_path):
        # Try to determine extension from mime type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            ext = mimetypes.guess_extension(mime_type)
            if ext:
                return f"{new_name}{ext}"
    return f"{new_name}{original_ext}"

def handle_file(file_path):
    """Handle a file by analyzing its content and organizing it intelligently."""
    try:
        # Get file type and content analysis
        file_type = get_file_type(file_path)
        content_info = detect_topic(file_path)
        
        # Generate new filename based on content
        new_name = rename_file(file_path, content_info)
        
        # Ensure the new filename has the correct extension
        new_name = ensure_extension(file_path, new_name)
        
        # Determine if file is from Telegram
        is_telegram_file = TELEGRAM_PATH in file_path
        
        # Choose base path based on source
        base_path = TELEGRAM_PATH if is_telegram_file else BASE_PATH
        
        # Create directory structure based on content analysis
        dest_dir = create_directory_structure(base_path, content_info)
        
        # Check for duplicates
        if is_duplicate(file_path, dest_dir):
            print(f"Skipping duplicate file: {file_path}")
            return
        
        # Move the file to its new location
        dest_path = os.path.join(dest_dir, new_name)
        
        # If the file is already in the correct location with the correct name, skip moving
        if os.path.dirname(file_path) == dest_dir and os.path.basename(file_path) == new_name:
            print(f"File already in correct location: {file_path}")
        else:
            shutil.move(file_path, dest_path)
            print(f"Moved file from {file_path} to {dest_path}")
        
        # Save metadata
        save_metadata(dest_path, content_info, file_path)
        
        print(f"Organized file:")
        print(f"  From: {file_path}")
        print(f"  To: {dest_path}")
        print(f"  Category: {content_info.get('category', 'Unknown')}")
        print(f"  Subcategory: {content_info.get('subcategory', 'Unknown')}")
        print(f"  Description: {content_info.get('description', 'Unknown')}")
        print(f"  Tags: {', '.join(content_info.get('tags', []))}")
        print(f"  Source: {'Telegram' if is_telegram_file else 'Downloads'}")
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()

