# ML File Organizer

A Python project to automatically organize files in a directory using file extensions and machine learning classification.

---

## Project Structure

```
ml_file_organizer/
├── main.py
├── watcher.py
├── utils/
│   ├── __init__.py
│   ├── classify.py
│   ├── config.py
│   └── cache.py
├── config.yaml
├── cache.json
├── tests/
│   └── test_organize.py
└── .env
```

---

## File Descriptions

- **main.py**  
  Entry point for organizing files. Loads configuration, scans the target directory, classifies files, and moves them to appropriate folders.

- **watcher.py**  
  Monitors a directory for new files in real-time. When a new file is detected, it classifies and moves it using the same logic as `main.py`.

- **utils/classify.py**  
  Contains logic to classify files based on extension or, for unknown types, using a machine learning model (e.g., Hugging Face API). Handles mapping between file types and destination folders.

- **utils/config.py**  
  Loads and parses the configuration file (`config.yaml`). Provides configuration data to other modules.

- **utils/cache.py**  
  Manages a cache (`cache.json`) to store classification results and avoid redundant API calls.

- **config.yaml**  
  User-editable configuration file. Defines folder names and which file extensions belong to each category.

- **cache.json**  
  Stores cached classification results for faster future runs.

- **tests/test_organize.py**  
  Contains unit tests for the file organization logic.

- **.env**  
  Stores environment variables, such as the Hugging Face API token.

---

## Workflow

1. **Configuration**

   - Edit `config.yaml` to define how files should be organized.
   - Add your Hugging Face API token to `.env`.

2. **Running the Organizer**

   - Run `main.py` to organize all files in the target directory.
     - Loads config.
     - Scans directory for files.
     - For each file:
       - Checks cache for previous classification.
       - If not cached, classifies by extension or ML model.
       - Moves file to the appropriate folder.
       - Updates cache.

3. **Real-Time Monitoring (Optional)**

   - Run `watcher.py` to monitor the directory for new files.
   - When a new file appears, it is classified and moved as above.

4. **Testing**
   - Run tests in `tests/test_organize.py` to verify classification and organization logic.

---

## Summary Diagram

```
User configures → Runs main.py/watcher.py → Loads config → Scans/monitors files
        ↓
  Classifies files (extension/ML) → Moves files → Updates cache
```

---

## Requirements

- Python 3.8+
- Hugging Face API token (for ML classification)
- Required Python packages (see `requirements.txt` if present)

---

## License

MIT License (or specify your license here)
