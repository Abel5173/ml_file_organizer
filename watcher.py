import inotify.adapters
import time
import yaml
import os
import shutil
from dotenv import load_dotenv
from utils.classify import classify_file
from utils.cache import load_cache, save_cache
from utils.config import load_config


def watch_downloads():
    load_dotenv()  # Load .env file
    config = load_config()
    downloads = os.path.expanduser(config["paths"]["downloads"])
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    max_requests = config["api"]["rate_limit"]["max_requests_per_hour"]
    cache = load_cache()
    request_count = cache.get("request_count", 0)
    last_reset = cache.get("last_reset", time.time())

    if not token:
        raise ValueError("Hugging Face API token not found in .env file")

    i = inotify.adapters.Inotify()
    i.add_watch(downloads, mask=inotify.constants.IN_CREATE |
                inotify.constants.IN_MOVED_TO)

    print(f"Watching {downloads} for new files...")
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        if ("IN_CREATE" in type_names or "IN_MOVED_TO" in type_names) and not filename.startswith("."):
            # Reset count hourly
            if time.time() - last_reset >= 3600:
                request_count = 0
                last_reset = time.time()
                cache["request_count"] = request_count
                cache["last_reset"] = last_reset
                save_cache(cache)

            if request_count >= max_requests:
                wait_time = 3600 - (time.time() - last_reset)
                print(
                    f"Reached API limit ({max_requests}/hour). Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
                request_count = 0
                last_reset = time.time()
                cache["request_count"] = request_count
                cache["last_reset"] = last_reset
                save_cache(cache)

            file_path = os.path.join(path, filename)
            print(f"Detected new file: {filename}")
            category = classify_file(file_path, token, config, downloads)
            dest_dir = os.path.join(downloads, category)
            dest_path = os.path.join(dest_dir, filename)
            print(f"Moving {filename} to {category}")
            try:
                shutil.move(file_path, dest_path)
                request_count += 1
                cache["request_count"] = request_count
                save_cache(cache)
            except Exception as e:
                print(f"Error moving {filename}: {e}")


if __name__ == "__main__":
    watch_downloads()
