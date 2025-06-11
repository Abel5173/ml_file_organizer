import os
import glob
from utils.classify import classify_file
from utils.cache import load_cache
from utils.config import load_config
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        print("Error: HUGGINGFACE_API_TOKEN not set in .env")
        return

    # Load configuration
    config = load_config()
    downloads_dir = os.path.expanduser(config["paths"]["downloads"])

    # Load cache
    cache = load_cache()

    # Process all files in Downloads
    for file_path in glob.glob(os.path.join(downloads_dir, "*")):
        if os.path.isfile(file_path):
            try:
                category = classify_file(file_path, token, config, downloads_dir)
                print(f"Moving {os.path.basename(file_path)} to {category}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()