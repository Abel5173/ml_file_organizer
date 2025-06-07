# ML File Organizer

## Overview
ML File Organizer is a Python-based project that automatically organizes files in the `~/Downloads` folder on a Linux system (tested on Ubuntu 24.04 LTS) using machine learning. It sorts files into a structured hierarchy based on their type and content, creating folders dynamically to maintain an organized filesystem. The project combines metadata-based sorting (e.g., file extensions) with content-based classification using a zero-shot machine learning model to categorize complex files like PDFs into meaningful subcategories.

### Features
- **Folder Structure**: Organizes files into top-level folders (`Archives`, `Music`, `Programs`, `Videos`, `Documents`, `Pictures`, `Telegram Desktop`) and `Documents` subfolders (`10Academy`, `CSVs`, `CVs`, `Excel`, `Others`, `PDFs`, `PowerPoint`, `Text`, `Word`).
- **Metadata-Based Sorting**: Uses file extensions to quickly sort images (`.jpg`, `.png`) to `Pictures`, videos (`.mp4`) to `Videos`, audio (`.mp3`) to `Music`, and more.
- **ML-Based Sorting**: Employs a zero-shot classifier (`facebook/bart-large-mnli`) to analyze PDF content and categorize them into `Documents` subfolders like `Contracts`, `Invoices`, `CVs`, or `Articles`.
- **Dynamic Folder Creation**: Automatically creates required folders and subfolders if they don’t exist.
- **Real-Time Monitoring**: Uses `inotify` to detect new files in `~/Downloads` and organize them instantly.

### How It Works
1. **File Detection**: The `watcher.py` script monitors the `~/Downloads` folder for new or moved files.
2. **Classification**:
   - Simple files (e.g., `.jpg`, `.mp3`, `.docx`) are sorted based on MIME types or extensions.
   - PDFs are analyzed using text extraction (`pdfplumber`) and classified with a zero-shot model into `Documents` subcategories.
3. **Organization**: Files are moved to their respective folders, with folders created as needed.
4. **Configuration**: Settings (e.g., categories, ML model) are defined in `config.yaml` for easy customization.

### Project Structure
- `src/`: Core scripts (`main.py`, `watcher.py`).
- `utils/`: Helper functions for text extraction (`extract.py`) and classification (`classify.py`).
- `data/`: Sample files for testing.
- `model/`: Storage for trained or pre-trained models.
- `tests/`: Unit tests (`test_organize.py`).
- `config.yaml`: Configuration for paths and categories.
- `requirements.txt`: Python dependencies.

### Setup
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip tesseract-ocr libtesseract-dev python3-inotify
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

