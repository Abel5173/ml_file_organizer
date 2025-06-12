import os
import requests
from utils.file_utils import read_text_content
from dotenv import load_dotenv
import time
from PIL import Image

load_dotenv()

HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

if not HUGGING_FACE_TOKEN:
    raise ValueError("HUGGING_FACE_TOKEN environment variable not set.")

HEADERS = {
    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
}

# Models for different aspects of content analysis
TEXT_CLASSIFIER = "facebook/bart-large-mnli"  # For general text classification
TEXT_SUMMARIZER = "facebook/bart-large-cnn"   # For generating content summaries
IMAGE_CLASSIFIER = "google/vit-base-patch16-224"  # For image classification
CODE_CLASSIFIER = "microsoft/codebert-base"   # For code file analysis
AUDIO_CLASSIFIER = "facebook/wav2vec2-base-960h"  # For audio classification
VIDEO_CLASSIFIER = "microsoft/xclip-base-patch32"  # For video classification
SPREADSHEET_CLASSIFIER = "microsoft/table-transformer-detection"  # For spreadsheet analysis
PRESENTATION_CLASSIFIER = "microsoft/table-transformer-detection"  # For presentation analysis
ARCHIVE_CLASSIFIER = "facebook/bart-large-mnli"  # For archive content analysis

# File type mappings
FILE_TYPE_MODELS = {
    '.mp3': AUDIO_CLASSIFIER,
    '.wav': AUDIO_CLASSIFIER,
    '.mp4': VIDEO_CLASSIFIER,
    '.avi': VIDEO_CLASSIFIER,
    '.mkv': VIDEO_CLASSIFIER,
    '.xlsx': SPREADSHEET_CLASSIFIER,
    '.xls': SPREADSHEET_CLASSIFIER,
    '.csv': SPREADSHEET_CLASSIFIER,
    '.ppt': PRESENTATION_CLASSIFIER,
    '.pptx': PRESENTATION_CLASSIFIER,
    '.zip': ARCHIVE_CLASSIFIER,
    '.rar': ARCHIVE_CLASSIFIER,
    '.7z': ARCHIVE_CLASSIFIER,
    '.tar': ARCHIVE_CLASSIFIER,
    '.gz': ARCHIVE_CLASSIFIER,
}

# Model endpoints
MODEL_ENDPOINTS = {
    'text': f"https://api-inference.huggingface.co/models/{TEXT_CLASSIFIER}",
    'image': f"https://api-inference.huggingface.co/models/{IMAGE_CLASSIFIER}",
    'audio': f"https://api-inference.huggingface.co/models/{AUDIO_CLASSIFIER}",
    'video': f"https://api-inference.huggingface.co/models/{VIDEO_CLASSIFIER}",
    'code': f"https://api-inference.huggingface.co/models/{CODE_CLASSIFIER}",
    'spreadsheet': f"https://api-inference.huggingface.co/models/{SPREADSHEET_CLASSIFIER}",
    'presentation': f"https://api-inference.huggingface.co/models/{PRESENTATION_CLASSIFIER}",
    'archive': f"https://api-inference.huggingface.co/models/{ARCHIVE_CLASSIFIER}"
}


def query_hf_model(model_url, payload, is_binary=False):
    """Query the Hugging Face model with improved error handling."""
    try:
        if is_binary:
            headers = HEADERS.copy()
            headers["Content-Type"] = "image/jpeg"
            response = requests.post(
                model_url,
                headers=headers,
                data=payload["inputs"],
                timeout=30  # Add timeout
            )
        else:
            response = requests.post(
                model_url,
                headers=HEADERS,
                json=payload,
                timeout=30  # Add timeout
            )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            print(f"Model is loading, please wait...")
            # Wait for model to load
            time.sleep(20)
            return query_hf_model(model_url, payload, is_binary)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout while querying model: {model_url}")
        return None
    except Exception as e:
        print(f"Error querying model: {str(e)}")
        return None


def analyze_text_content(text):
    """Analyze text content using multiple models to get comprehensive understanding."""
    if not text:
        return {"category": "Unknown", "description": "Unknown", "tags": [], "subcategories": []}

    # Get general classification with hierarchical categories
    classification = query_hf_model(
        MODEL_ENDPOINTS['text'],
        {
            "inputs": text[:512],
            "parameters": {
                "candidate_labels": [
                    "Programming/Code", "Programming/Documentation", "Programming/Tutorial",
                    "Research/Academic", "Research/Scientific", "Research/Technical",
                    "Business/Finance", "Business/Management", "Business/Marketing",
                    "Education/Learning", "Education/Teaching", "Education/Reference",
                    "Creative/Art", "Creative/Design", "Creative/Media",
                    "Personal/Notes", "Personal/Journal", "Personal/Planning",
                    "Technical/System", "Technical/Network", "Technical/Security",
                    "Professional/Report", "Professional/Presentation", "Professional/Proposal",
                    "Entertainment/Games", "Entertainment/Music", "Entertainment/Videos",
                    "Reference/Guide", "Reference/Manual", "Reference/Dictionary"
                ]
            }
        }
    )

    # Get content summary
    summary = query_hf_model(
        MODEL_ENDPOINTS['text'],
        {
            "inputs": text[:1024],
            "parameters": {
                "max_length": 100,
                "min_length": 30
            }
        }
    )

    # Extract category and subcategory
    try:
        if classification and isinstance(classification, list) and len(classification) > 0:
            if "labels" in classification[0]:
                full_category = classification[0]["labels"][0]
                category, subcategory = full_category.split("/")
            else:
                category = "Unknown"
                subcategory = "Unknown"
        else:
            category = "Unknown"
            subcategory = "Unknown"
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error extracting category: {str(e)}")
        category = "Unknown"
        subcategory = "Unknown"

    # Get description
    try:
        if summary and isinstance(summary, list) and len(summary) > 0:
            if "summary_text" in summary[0]:
                description = summary[0]["summary_text"]
            elif "generated_text" in summary[0]:
                description = summary[0]["generated_text"]
            else:
                description = text[:100] + "..."
        else:
            description = text[:100] + "..."
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error extracting description: {str(e)}")
        description = text[:100] + "..."
    
    # Generate tags based on content
    tags = []
    content_lower = text.lower()
    
    # Add category and subcategory to tags
    tags.extend([category.lower(), subcategory.lower()])
    
    # Content-specific tags
    if any(lang in content_lower for lang in ["python", "javascript", "java", "c++", "ruby", "php"]):
        tags.append("programming")
    if "data" in content_lower:
        tags.append("data")
    if "machine learning" in content_lower or "ml" in content_lower:
        tags.append("ml")
    if "web" in content_lower:
        tags.append("web")
    if "database" in content_lower:
        tags.append("database")
    
    return {
        "category": category,
        "subcategory": subcategory,
        "description": description,
        "tags": tags
    }


def analyze_specialized_content(file_path, file_type):
    """Analyze specialized content types using appropriate models."""
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext in ['.mp3', '.wav']:
        # Audio analysis
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
                result = query_hf_model(
                    MODEL_ENDPOINTS['audio'],
                    {"inputs": audio_data},
                    is_binary=True
                )
                if result:
                    return {
                        "category": "Audio",
                        "description": f"Audio file: {result[0].get('label', 'Unknown')}",
                        "tags": ["audio", result[0].get('label', '').lower()]
                    }
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
    
    elif ext in ['.mp4', '.avi', '.mkv']:
        # Video analysis
        try:
            with open(file_path, "rb") as f:
                video_data = f.read()
                result = query_hf_model(
                    MODEL_ENDPOINTS['video'],
                    {"inputs": video_data},
                    is_binary=True
                )
                if result:
                    return {
                        "category": "Video",
                        "description": f"Video content: {result[0].get('label', 'Unknown')}",
                        "tags": ["video", result[0].get('label', '').lower()]
                    }
        except Exception as e:
            print(f"Error processing video: {str(e)}")
    
    elif ext in ['.xlsx', '.xls', '.csv']:
        # Spreadsheet analysis
        text = read_text_content(file_path)
        if text:
            result = query_hf_model(
                MODEL_ENDPOINTS['spreadsheet'],
                {
                    "inputs": text[:512],
                    "parameters": {
                        "candidate_labels": [
                            "Financial Data", "Statistical Analysis", "Project Planning",
                            "Inventory", "Schedule", "Budget", "Report", "Database"
                        ]
                    }
                }
            )
            if result:
                return {
                    "category": "Spreadsheet",
                    "description": f"Spreadsheet: {result[0]['labels'][0]}",
                    "tags": ["spreadsheet", result[0]['labels'][0].lower()]
                }
    
    elif ext in ['.ppt', '.pptx']:
        # Presentation analysis
        text = read_text_content(file_path)
        if text:
            result = query_hf_model(
                MODEL_ENDPOINTS['presentation'],
                {
                    "inputs": text[:512],
                    "parameters": {
                        "candidate_labels": [
                            "Business Presentation", "Educational", "Technical",
                            "Project Overview", "Sales Pitch", "Training Material",
                            "Research Presentation", "Status Report"
                        ]
                    }
                }
            )
            if result:
                return {
                    "category": "Presentation",
                    "description": f"Presentation: {result[0]['labels'][0]}",
                    "tags": ["presentation", result[0]['labels'][0].lower()]
                }
    
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        # Archive analysis
        text = read_text_content(file_path)
        if text:
            result = query_hf_model(
                MODEL_ENDPOINTS['archive'],
                {
                    "inputs": text[:512],
                    "parameters": {
                        "candidate_labels": [
                            "Software Package", "Document Collection", "Media Archive",
                            "Backup Data", "Project Files", "Resource Pack"
                        ]
                    }
                }
            )
            if result:
                return {
                    "category": "Archive",
                    "description": f"Archive: {result[0]['labels'][0]}",
                    "tags": ["archive", result[0]['labels'][0].lower()]
                }
    
    return None


def detect_topic(file_path):
    """Analyze file content and return comprehensive information about it."""
    ext = os.path.splitext(file_path)[-1].lower()
    
    # Try specialized content analysis first
    specialized_result = analyze_specialized_content(file_path, ext)
    if specialized_result:
        return specialized_result
    
    # Handle text-based files
    if ext in ['.pdf', '.docx', '.txt', '.md', '.py', '.js', '.java', '.cpp', '.html', '.css']:
        text = read_text_content(file_path)
        if text:
            # For PDFs and documents, try to determine the type first
            if ext in ['.pdf', '.docx']:
                # Try to classify the document type
                doc_classification = query_hf_model(
                    MODEL_ENDPOINTS['text'],
                    {
                        "inputs": text[:512],
                        "parameters": {
                            "candidate_labels": [
                                "Book/Literature", "Book/Self-Help", "Book/Technical",
                                "Document/Report", "Document/Research", "Document/Manual",
                                "Education/Textbook", "Education/Guide", "Education/Reference",
                                "Business/Proposal", "Business/Report", "Business/Manual",
                                "Technical/Manual", "Technical/Guide", "Technical/Reference"
                            ]
                        }
                    }
                )
                
                if doc_classification and isinstance(doc_classification, list) and len(doc_classification) > 0:
                    if "labels" in doc_classification[0]:
                        category, subcategory = doc_classification[0]["labels"][0].split("/")
                        return {
                            "category": category,
                            "subcategory": subcategory,
                            "description": text[:200] + "...",
                            "tags": [category.lower(), subcategory.lower(), "document", ext[1:]]
                        }
            
            # If document classification fails or for other text files, use general analysis
            return analyze_text_content(text)
    
    # Handle image files
    elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            print(f"Corrupted image file detected: {file_path} ({str(e)})")
            return {
                "category": "Corrupted",
                "subcategory": "Invalid",
                "description": "Corrupted image file",
                "tags": ["corrupted", "image"]
            }
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()
                # Get image classification
                result = query_hf_model(
                    f"https://api-inference.huggingface.co/models/{IMAGE_CLASSIFIER}",
                    {"inputs": image_data},
                    is_binary=True
                )
                
                if result:
                    # Get hierarchical categorization
                    context_result = query_hf_model(
                        MODEL_ENDPOINTS['text'],
                        {
                            "inputs": result[0]["label"],
                            "parameters": {
                                "candidate_labels": [
                                    "Media/Photo", "Media/Screenshot", "Media/Art",
                                    "Document/Code", "Document/Text", "Document/Diagram",
                                    "Content/Personal", "Content/Professional", "Content/Educational",
                                    "Design/UI", "Design/Graphic", "Design/Architecture",
                                    "Reference/Technical", "Reference/Visual", "Reference/Guide"
                                ]
                            }
                        }
                    )
                    
                    main_label = result[0]["label"]
                    if context_result and "labels" in context_result[0]:
                        category, subcategory = context_result[0]["labels"][0].split("/")
                    else:
                        category = "Media"
                        subcategory = "Photo"
                    
                    tags = ["image", main_label.lower(), category.lower(), subcategory.lower()]
                    
                    return {
                        "category": category,
                        "subcategory": subcategory,
                        "description": f"{main_label} ({category}/{subcategory})",
                        "tags": tags
                    }
        except Exception as e:
            print(f"Error processing image: {str(e)}")
    
    # Handle code files specifically
    if ext in ['.py', '.js', '.java', '.cpp', '.html', '.css']:
        text = read_text_content(file_path)
        if text:
            code_analysis = query_hf_model(
                f"https://api-inference.huggingface.co/models/{CODE_CLASSIFIER}",
                {
                    "inputs": text[:512],
                    "parameters": {
                        "candidate_labels": [
                            "Programming/Web", "Programming/Data", "Programming/System",
                            "Programming/Mobile", "Programming/Game", "Programming/Database",
                            "Programming/DevOps", "Programming/Security", "Programming/UI"
                        ]
                    }
                }
            )
            if code_analysis and "labels" in code_analysis[0]:
                category, subcategory = code_analysis[0]["labels"][0].split("/")
                return {
                    "category": category,
                    "subcategory": subcategory,
                    "description": f"{category} code: {subcategory}",
                    "tags": ["code", ext[1:], category.lower(), subcategory.lower()]
                }

    return {
        "category": "Unknown",
        "subcategory": "Unknown",
        "description": "Unknown",
        "tags": []
    }
