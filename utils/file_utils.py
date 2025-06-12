import os 
from PyPDF2 import PdfReader
from docx import Document
import re
from datetime import datetime
import json
import fitz  # PyMuPDF

# Image subcategory mappings
IMAGE_SUBCATEGORIES = {
    # Code and Documentation
    "code": ["code", "programming", "screenshot", "terminal", "console", "ide", "editor"],
    "documentation": ["document", "pdf", "text", "article", "paper", "research"],
    
    # Nature and Outdoors
    "nature": ["landscape", "mountain", "forest", "beach", "sky", "sunset", "sunrise", "cloud"],
    "wildlife": ["animal", "bird", "fish", "insect", "wildlife", "nature"],
    
    # Animals
    "pets": ["cat", "dog", "pet", "animal", "puppy", "kitten"],
    "wildlife": ["wildlife", "animal", "bird", "fish", "insect"],
    
    # People and Portraits
    "portraits": ["person", "portrait", "face", "people", "human"],
    "family": ["family", "group", "people", "portrait"],
    
    # Food and Drink
    "food": ["food", "meal", "dish", "restaurant", "cooking", "recipe"],
    "drinks": ["drink", "beverage", "coffee", "tea", "wine"],
    
    # Architecture and Buildings
    "architecture": ["building", "architecture", "house", "city", "urban"],
    "interior": ["room", "interior", "furniture", "design"],
    
    # Technology
    "devices": ["phone", "computer", "laptop", "tablet", "device", "gadget"],
    "electronics": ["electronic", "circuit", "hardware", "component"],
    
    # Art and Design
    "art": ["art", "painting", "drawing", "illustration", "design"],
    "graphics": ["graphic", "logo", "icon", "banner", "poster"],
    
    # Travel and Places
    "travel": ["travel", "vacation", "trip", "journey", "destination"],
    "landmarks": ["landmark", "monument", "statue", "historical"],
    
    # Sports and Activities
    "sports": ["sport", "game", "athlete", "team", "competition"],
    "activities": ["activity", "hobby", "exercise", "fitness"],
    
    # Vehicles
    "vehicles": ["car", "vehicle", "automobile", "motorcycle", "bicycle"],
    "transportation": ["transport", "airplane", "train", "ship", "bus"],
    
    # Business and Work
    "business": ["business", "office", "work", "meeting", "presentation"],
    "education": ["education", "school", "classroom", "learning", "study"],
    
    # Events and Celebrations
    "events": ["event", "party", "celebration", "festival", "ceremony"],
    "holidays": ["holiday", "christmas", "birthday", "anniversary"],
    
    # Medical and Science
    "medical": ["medical", "health", "hospital", "doctor", "patient"],
    "science": ["science", "laboratory", "experiment", "research"],
    
    # Screenshots and UI
    "screenshots": ["screenshot", "screen", "ui", "interface", "app"],
    "ui_design": ["ui", "interface", "design", "mockup", "wireframe"],
    
    # Memes and Social
    "memes": ["meme", "funny", "humor", "joke", "comic"],
    "social": ["social", "media", "post", "share", "content"]
}

def get_image_subcategory(description, tags):
    """Determine the most appropriate subcategory for an image based on its description and tags."""
    description_lower = description.lower()
    tags_lower = [tag.lower() for tag in tags]
    
    # Check each subcategory's keywords against the description and tags
    for subcategory, keywords in IMAGE_SUBCATEGORIES.items():
        if any(keyword in description_lower for keyword in keywords) or \
           any(keyword in tags_lower for keyword in keywords):
            return subcategory
    
    return "miscellaneous"

def read_text_content(file_path):
    """Read text content from various file types with improved error handling."""
    ext = os.path.splitext(file_path)[-1].lower()
    try:
        if ext in ['.txt', '.md', '.py', '.js', '.java', '.cpp', '.html', '.css']:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif ext in ['.pdf']:
            # Try PyMuPDF first (more reliable)
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                return text
            except Exception as e:
                print(f"PyMuPDF failed, trying PyPDF2: {str(e)}")
                # Fallback to PyPDF2
                reader = PdfReader(file_path)
                return ' '.join([page.extract_text() for page in reader.pages])
        elif ext in ['.docx']:
            doc = Document(file_path)
            return ' '.join([para.text for para in doc.paragraphs])
        else:
            print(f"Unsupported file type for text extraction: {ext}")
            return None
    except Exception as e:
        print(f"Error reading text content from {file_path}: {e}")
        return None


def extract_filename(file_path):
    """Extract the base filename without extension from a file path."""
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    return name_without_ext


def create_directory_structure(base_path, content_info):
    """Create a directory structure based on ML-driven content analysis."""
    category = content_info.get("category", "Unknown")
    subcategory = content_info.get("subcategory", "Unknown")
    
    # Create the full path including category and subcategory
    full_path = os.path.join(base_path, category, subcategory)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def generate_simple_filename(content_info, original_name):
    """Generate a simple, clean filename based on content analysis."""
    # Try to get a meaningful name from the content
    description = content_info.get("description", "")
    category = content_info.get("category", "Unknown")
    subcategory = content_info.get("subcategory", "Unknown")
    
    # If we have a good description, use it
    if description and description != "Unknown":
        # Clean and simplify the description
        clean_name = re.sub(r'[^\w\s-]', '', description)
        clean_name = clean_name.lower()
        clean_name = re.sub(r'\s+', '-', clean_name)
        clean_name = re.sub(r'-+', '-', clean_name)
        clean_name = clean_name.strip('-')
        
        # If the name is too long, take the first few words
        if len(clean_name) > 20:
            words = clean_name.split('-')
            clean_name = '-'.join(words[:2])
    else:
        # Use the original filename as base
        base_name = os.path.splitext(original_name)[0]
        clean_name = re.sub(r'[^\w\s-]', '', base_name)
        clean_name = re.sub(r'\s+', '-', clean_name)
        clean_name = re.sub(r'-+', '-', clean_name)
        clean_name = clean_name.strip('-')
        
        # If still too long, take first part
        if len(clean_name) > 20:
            clean_name = clean_name[:20]
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{clean_name}_{timestamp}"


def save_metadata(file_path, content_info, original_path):
    """Save metadata about the file."""
    # Create metadata directory in the same directory as the file
    metadata_dir = os.path.join(os.path.dirname(file_path), ".metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Create metadata filename based on the original file
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    metadata_file = os.path.join(metadata_dir, f"{base_name}.json")
    
    # Prepare metadata
    metadata = {
        "original_name": os.path.basename(original_path),
        "original_path": original_path,
        "category": content_info.get("category", "Unknown"),
        "subcategory": content_info.get("subcategory", "Unknown"),
        "description": content_info.get("description", "Unknown"),
        "tags": content_info.get("tags", []),
        "created_at": datetime.now().isoformat(),
        "file_type": os.path.splitext(file_path)[1],
        "source": os.path.dirname(original_path)
    }
    
    # Save metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def rename_file(file_path, content_info):
    """Generate a new filename and organize the file based on content analysis."""
    ext = os.path.splitext(file_path)[1]
    new_name = generate_simple_filename(content_info, os.path.basename(file_path))
    return f"{new_name}{ext}"
