import time
import requests
from utils.cache import get_cached_category, cache_category, load_cache, save_cache
from utils.api import image_classification
from utils.extract import extract_pdf_text, extract_csv_text, extract_image_text, extract_code_text, extract_keywords, get_text_embedding
from sklearn.cluster import KMeans
import numpy as np
import os
import mimetypes

def summarize_text(text, token, model_name, config):
    """Generate a topic name via summarization."""
    retry_delay = config["api"]["rate_limit"]["retry_delay"]
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": text[:config["api"]["text_limit"]],
                "parameters": {"max_length": 10, "min_length": 2}
            }
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            summary = response.json()[0]["summary_text"]
            # Clean and capitalize topic name
            summary = " ".join(word.capitalize()
                               for word in summary.split() if word.isalnum())
            return summary or "Others"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            print(f"Summarization error: {e}")
            return "Others"
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Others"
    print("Max retries reached for summarization")
    return "Others"


def infer_folder_name(text, token, config, base_folder, file_path):
    """Infer subfolder by clustering embeddings and summarizing topics."""
    cache = load_cache()
    embeddings = cache.get("embeddings", {})
    topics = cache.get("topics", {})

    # Get embedding for current file
    embedding = get_text_embedding(
        text, token, config["api"]["embedding_model"], config)
    if embedding is None:
        return "Others"

    # Store embedding
    file_hash = get_file_hash(file_path)
    embeddings[file_hash] = embedding.tolist()
    cache["embeddings"] = embeddings

    # Collect all embeddings for clustering
    embedding_list = np.array(list(embeddings.values()))
    if len(embedding_list) < 2:
        # Single file: summarize text for topic
        topic = summarize_text(
            text, token, config["api"]["summarization_model"], config)
        topics[topic] = [file_hash]
        cache["topics"] = topics
        save_cache(cache)
        return topic

    # Cluster embeddings
    kmeans = KMeans(n_clusters=min(5, len(embedding_list)), random_state=42)
    labels = kmeans.fit_predict(embedding_list)

    # Assign file to cluster
    cluster_id = labels[list(embeddings.keys()).index(file_hash)]

    # Get topic for cluster
    cluster_files = [k for i, k in enumerate(
        embeddings.keys()) if labels[i] == cluster_id]
    if cluster_files[0] in topics.values():
        # Existing topic
        for topic, files in topics.items():
            if cluster_files[0] in files:
                topics[topic].append(file_hash)
                cache["topics"] = topics
                save_cache(cache)
                return topic

    # New topic: summarize representative text
    representative_text = text  # Use current file's text
    topic = summarize_text(representative_text, token,
                           config["api"]["summarization_model"], config)
    topics[topic] = cluster_files + [file_hash]
    cache["topics"] = topics
    save_cache(cache)
    return topic


def classify_file(file_path, token, config, downloads_dir):
    cache = load_cache()
    cached_category = get_cached_category(file_path, cache)
    if cached_category:
        return cached_category

    file_ext = os.path.splitext(file_path)[1].lower()
    base_folders = config["base_folders"]

    # Determine base folder by extension
    base_folder = "Miscellaneous"
    for folder in base_folders:
        if file_ext in folder["extensions"]:
            base_folder = folder["name"]
            break

    # Create base folder
    os.makedirs(os.path.join(downloads_dir, base_folder), exist_ok=True)

    # Infer subfolder
    subfolder = "Others"
    if base_folder == "Images":
        subfolder = image_classification(file_path, config["api"]["vision_model"], token, [
                                         "Photos", "Screenshots", "Graphics", "Memes", "Others"], config)
    elif base_folder.startswith("Documents/"):
        text_extractors = {
            ".pdf": extract_pdf_text,
            ".csv": extract_csv_text,
            ".txt": extract_code_text
        }
        text = text_extractors.get(file_ext, lambda x: "")(file_path)
        if text:
            subfolder = infer_folder_name(
                text, token, config, base_folder, file_path)
    elif base_folder == "Code":
        text = extract_code_text(file_path)
        if text:
            subfolder = infer_folder_name(
                text, token, config, base_folder, file_path)
    elif base_folder in ["Videos", "Music", "Archives", "Executables"]:
        subfolder = "General"  # Default for non-text files

    # Create subfolder and cache result
    category = f"{base_folder}/{subfolder}"
    os.makedirs(os.path.join(downloads_dir,
                base_folder, subfolder), exist_ok=True)
    cache_category(file_path, category, cache)
    return category


def get_file_hash(file_path):
    """Helper function to compute file hash."""
    from hashlib import md5
    hasher = md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


