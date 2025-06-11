import time
import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
from collections import Counter
import re
import requests
import numpy as np
import json


def extract_pdf_text(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        return text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""


def extract_csv_text(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""


def extract_image_text(file_path):
    try:
        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""


def extract_code_text(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error extracting code from {file_path}: {e}")
        return ""


def extract_keywords(text, limit=5):
    """Extract top keywords for topic naming."""
    if not text:
        return []
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {"the", "and", "or", "is", "are",
                 "in", "to", "for", "of", "a", "an"}
    words = [w for w in words if w not in stopwords and len(w) > 3]
    return [word for word, _ in Counter(words).most_common(limit)]


def get_text_embedding(text, token, model_name, config):
    """Get text embedding via Hugging Face API."""
    retry_delay = config["api"]["rate_limit"]["retry_delay"]
    if not text:
        print("Embedding error: Empty text input")
        return None

    # Truncate text to API limit
    text = text[:config["api"]["text_limit"]]

    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"inputs": text}
            print(
                f"Attempt {attempt + 1}: Sending embedding request for text: {text[:50]}...")
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(
                f"Embedding response: {json.dumps(result, indent=2)[:100]}...")
            if isinstance(result, list) and len(result) > 0:
                return np.array(result)
            else:
                print(f"Unexpected response format: {result}")
                return None
        except requests.exceptions.HTTPError as e:
            print(f"Embedding HTTP error: {e}, Response: {e.response.text}")
            if e.response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return None
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    print("Max retries reached for embedding")
    return None
