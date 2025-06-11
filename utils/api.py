import time
import io
from PIL import Image
import base64
import os
import requests


def text_classification(text, model_name, token, candidate_labels, config):
    retry_delay = config["api"]["rate_limit"]["retry_delay"]
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": text,
                "parameters": {"candidate_labels": candidate_labels}
            }
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["labels"][0]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            print(f"Text classification error: {e}")
            return "Others"
        except Exception as e:
            print(f"Text classification error: {e}")
            return "Others"
    print("Max retries reached for text classification")
    return "Others"


def image_classification(file_path, model_name, token, candidate_labels, config):
    retry_delay = config["api"]["rate_limit"]["retry_delay"]
    for attempt in range(3):
        try:
            with Image.open(file_path).convert("RGB") as img:
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": img_str,
                "parameters": {"candidate_labels": candidate_labels}
            }
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["labels"][0]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            print(f"Image classification error {file_path}: {e}")
            return "Others"
        except Exception as e:
            print(f"Image classification error {file_path}: {e}")
            return "Others"
    print("Max retries reached for image classification")
    return "Others"


