import os
import shutil
from pathlib import Path
from organizer.organizer import handle_file
from PIL import Image
import io

# Test directory setup
TEST_DIR = "test_files"

def create_sample_image():
    """Create a simple test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def create_sample_text():
    """Create sample text content."""
    return {
        "python_script.py": """import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def analyze_data(data):
    # Perform data analysis
    df = pd.DataFrame(data)
    X_train, X_test = train_test_split(df, test_size=0.2)
    return np.mean(X_train)
""",
        "document.txt": """Machine Learning Research Paper

This document discusses the application of deep learning in computer vision.
We explore various architectures and their performance on image classification tasks.
The research focuses on transfer learning and model optimization techniques.
""",
        "code.js": """// Web Application Code
const express = require('express');
const app = express();

app.get('/api/data', (req, res) => {
    const data = {
        items: [
            { id: 1, name: 'Item 1' },
            { id: 2, name: 'Item 2' }
        ]
    };
    res.json(data);
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
"""
    }

def setup_test_environment():
    """Create test directory and files."""
    # Create test directory
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    
    # Create test files with real content
    test_files = {
        "text": create_sample_text(),
        "media": {
            "image.jpg": create_sample_image()
        }
    }
    
    # Create test files
    for category, files in test_files.items():
        category_dir = os.path.join(TEST_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
        
        for filename, content in files.items():
            file_path = os.path.join(category_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)

def run_tests():
    """Run tests on the file organization system."""
    print("Starting file organization tests...")
    
    # Process each test file
    for category in os.listdir(TEST_DIR):
        category_path = os.path.join(TEST_DIR, category)
        if os.path.isdir(category_path):
            for filename in os.listdir(category_path):
                file_path = os.path.join(category_path, filename)
                print(f"\nProcessing: {file_path}")
                try:
                    handle_file(file_path)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    import traceback
                    traceback.print_exc()

def cleanup():
    """Clean up test environment."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    print("\nTest environment cleaned up.")

if __name__ == "__main__":
    try:
        setup_test_environment()
        run_tests()
    finally:
        cleanup()