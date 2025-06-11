import os
import json
import hashlib


def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_cache(cache_file="cache.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache, cache_file="cache.json"):
    with open(cache_file, "w") as f:
        json.dump(cache, f)


def get_cached_category(file_path, cache):
    file_hash = get_file_hash(file_path)
    return cache.get(file_hash)


def cache_category(file_path, category, cache):
    file_hash = get_file_hash(file_path)
    cache[file_hash] = category
    save_cache(cache)
